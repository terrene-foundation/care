#!/usr/bin/env node
/**
 * Hook: session-start
 * Event: SessionStart
 * Purpose: Initialize session, detect workspace state, inject session notes
 *          into Claude context, output configuration.
 *
 * Exit Codes:
 *   0 = success (continue)
 *   2 = blocking error (stop tool execution)
 *   other = non-blocking error (warn and continue)
 */

const fs = require("fs");
const path = require("path");
const {
  parseEnvFile,
  discoverModelsAndKeys,
  ensureEnvFile,
  buildCompactSummary,
} = require("./lib/env-utils");
const {
  resolveLearningDir,
  ensureLearningDir,
  logObservation: logLearningObservation,
} = require("./lib/learning-utils");
const {
  detectProjectMode,
  detectActiveWorkspace,
  listChildRepos,
  derivePhase,
  getTodoProgress,
  findAllSessionNotes,
} = require("./lib/workspace-utils");
const { checkVersion } = require("./lib/version-utils");

// Timeout fallback — prevents hanging the Claude Code session
const TIMEOUT_MS = 10000;
const _timeout = setTimeout(() => {
  console.log(JSON.stringify({ continue: true }));
  process.exit(1);
}, TIMEOUT_MS);

let input = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk) => (input += chunk));
process.stdin.on("end", () => {
  try {
    const data = JSON.parse(input);
    const result = initializeSession(data);
    const output = { continue: true };
    if (result.sessionNotesContext) {
      output.hookSpecificOutput = {
        hookEventName: "SessionStart",
        additionalContext: result.sessionNotesContext,
      };
    }
    console.log(JSON.stringify(output));
    process.exit(0);
  } catch (error) {
    console.error(`[HOOK ERROR] ${error.message}`);
    console.log(JSON.stringify({ continue: true }));
    process.exit(1);
  }
});

function initializeSession(data) {
  const session_id = (data.session_id || "unknown").replace(
    /[^a-zA-Z0-9_-]/g,
    "_",
  );
  const cwd = data.cwd || process.cwd();
  const homeDir = process.env.HOME || process.env.USERPROFILE;
  const sessionDir = path.join(homeDir, ".claude", "sessions");
  const learningDir = resolveLearningDir(cwd);
  const result = { sessionNotesContext: null };

  // Ensure directories exist
  [sessionDir].forEach((dir) => {
    try {
      fs.mkdirSync(dir, { recursive: true });
    } catch {}
  });
  ensureLearningDir(cwd);

  // ── Detect project mode ─────────────────────────────────────────────
  const projectMode = detectProjectMode(cwd);
  const projectType = detectProjectType(cwd);

  // ── .env provision (skip for orchestrators — child repos manage their own) ─
  let envExists = false;
  let env = {};
  let discovery = { models: {}, keys: {}, validations: [] };

  if (projectMode !== "orchestrator") {
    const envResult = ensureEnvFile(cwd);
    if (envResult.created) {
      console.error(
        `[ENV] Created .env from ${envResult.source}. Please fill in your API keys.`,
      );
    }

    const envPath = path.join(cwd, ".env");
    envExists = fs.existsSync(envPath);

    if (envExists) {
      env = parseEnvFile(envPath);
      discovery = discoverModelsAndKeys(env);
    }
  }

  // ── Log observation ───────────────────────────────────────────────────
  try {
    const observationsFile = path.join(learningDir, "observations.jsonl");
    fs.appendFileSync(
      observationsFile,
      JSON.stringify({
        type: "session_start",
        session_id,
        cwd,
        timestamp: new Date().toISOString(),
        envExists,
        projectType,
        models: discovery.models,
        keyCount: Object.keys(discovery.keys).length,
        validationFailures: discovery.validations
          .filter((v) => v.status === "MISSING_KEY")
          .map((v) => v.message),
      }) + "\n",
    );
  } catch {}

  // ── Version check (human-facing, stderr only) ─────────────────────────
  try {
    const versionResult = checkVersion(cwd);
    for (const msg of versionResult.messages) {
      console.error(msg);
    }
  } catch {}

  // ── Output status (human-facing, stderr only) ──────────────
  try {
    if (projectMode === "orchestrator") {
      const repos = listChildRepos(cwd);
      const gitRepos = repos.filter((r) => r.hasGit);
      const dirtyRepos = gitRepos.filter((r) => r.dirty);
      const nonGitRepos = repos.filter((r) => !r.hasGit);
      console.error(
        `[ECOSYSTEM] ${gitRepos.length} repos | ${dirtyRepos.length} dirty${dirtyRepos.length > 0 ? ": " + dirtyRepos.map((r) => r.name).join(", ") : ""}${nonGitRepos.length > 0 ? " | planned: " + nonGitRepos.map((r) => r.name).join(", ") : ""}`,
      );
    } else {
      const ws = detectActiveWorkspace(cwd);
      if (ws) {
        const phase = derivePhase(ws.path, cwd);
        const todos = getTodoProgress(ws.path);
        console.error(
          `[WORKSPACE] ${ws.name} | Phase: ${phase} | Todos: ${todos.active} active / ${todos.completed} done`,
        );
      }
    }
  } catch {}

  // ── Session notes (inject into Claude context + human-facing stderr) ─
  try {
    const allNotes = findAllSessionNotes(cwd);
    if (allNotes.length > 0) {
      for (const note of allNotes) {
        const staleTag = note.stale ? " (STALE)" : "";
        const label = note.workspace ? ` [${note.workspace}]` : " [root]";
        console.error(
          `[SESSION-NOTES]${label} ${note.relativePath}${staleTag} — updated ${note.age}`,
        );
      }

      // Build context for Claude — include all notes
      const contextParts = [];
      for (const note of allNotes) {
        const label = note.workspace ? `[${note.workspace}]` : "[root]";
        const staleMark = note.stale ? " (STALE — may be outdated)" : "";
        contextParts.push(
          `## Session Notes ${label}${staleMark} — updated ${note.age}\n\n${note.content}`,
        );
      }
      if (contextParts.length > 0) {
        result.sessionNotesContext =
          "# Previous Session Notes\n\nRead these to understand where the last session left off.\n\n" +
          contextParts.join("\n\n---\n\n");
      }
    }
  } catch {}

  // ── Output model/key summary (skip for orchestrators) ──────────────
  if (projectMode !== "orchestrator") {
    if (envExists) {
      const summary = buildCompactSummary(env, discovery);
      console.error(`[ENV] ${summary}`);

      for (const v of discovery.validations) {
        const icon = v.status === "ok" ? "✓" : "✗";
        console.error(`[ENV]   ${icon} ${v.message}`);
      }

      const failures = discovery.validations.filter(
        (v) => v.status === "MISSING_KEY",
      );
      if (failures.length > 0) {
        console.error(
          `[ENV] WARNING: ${failures.length} model(s) configured without API keys!`,
        );
        console.error(
          "[ENV] LLM operations WILL FAIL. Add missing keys to .env.",
        );
      }
    } else {
      console.error(
        "[ENV] No .env file found. API keys and models not configured.",
      );
    }
  }

  return result;
}

/**
 * Detect the project type based on filesystem contents.
 * Domain-agnostic — works for CO workspaces and multi-repo orchestrators.
 */
function detectProjectType(cwd) {
  try {
    // Check for multi-repo orchestrator pattern (sync-manifest + child repos with .git)
    const hasSyncManifest = fs.existsSync(
      path.join(cwd, ".claude", "sync-manifest.yaml"),
    );
    if (hasSyncManifest) {
      const hasChildRepos = fs
        .readdirSync(cwd, { withFileTypes: true })
        .filter(
          (e) =>
            e.isDirectory() &&
            !e.name.startsWith(".") &&
            e.name !== "scripts" &&
            e.name !== "node_modules",
        )
        .some((e) => {
          try {
            return fs.existsSync(path.join(cwd, e.name, ".git"));
          } catch {
            return false;
          }
        });
      if (hasChildRepos) return "orchestrator";
    }

    const hasWorkspaces = fs.existsSync(path.join(cwd, "workspaces"));
    const hasJournal =
      hasWorkspaces &&
      fs.readdirSync(path.join(cwd, "workspaces")).some((d) => {
        try {
          return fs.existsSync(path.join(cwd, "workspaces", d, "journal"));
        } catch {
          return false;
        }
      });

    if (hasWorkspaces && hasJournal) return "co-workspace";
    if (hasWorkspaces) return "co-workspace";
    return "co-project";
  } catch {
    return "unknown";
  }
}
