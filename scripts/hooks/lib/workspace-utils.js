/**
 * Shared utility: Workspace detection and phase derivation.
 *
 * Used by session-start.js, user-prompt-rules-reminder.js, and phase commands.
 * Supports both CO workspaces (workspaces/ subdirectory) and multi-repo
 * orchestrators (child repos with their own .git).
 */

const fs = require("fs");
const path = require("path");

/**
 * Detect the project mode: "orchestrator" or "workspace".
 *
 * @param {string} cwd - Project root directory
 * @returns {"orchestrator" | "workspace"}
 */
function detectProjectMode(cwd) {
  try {
    if (fs.existsSync(path.join(cwd, ".claude", "sync-manifest.yaml"))) {
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
  } catch {}
  return "workspace";
}

/**
 * Detect the active workspace under workspaces/.
 * Returns the most recently modified project directory, or null if none.
 *
 * @param {string} cwd - Project root directory
 * @returns {{ name: string, path: string } | null}
 */
function detectActiveWorkspace(cwd) {
  const wsDir = path.join(cwd, "workspaces");
  try {
    const entries = fs.readdirSync(wsDir, { withFileTypes: true });
    const projects = entries
      .filter(
        (e) =>
          e.isDirectory() &&
          e.name !== "instructions" &&
          !e.name.startsWith("_"),
      )
      .map((e) => {
        const fullPath = path.join(wsDir, e.name);
        try {
          const stat = fs.statSync(fullPath);
          return { name: e.name, path: fullPath, mtime: stat.mtime.getTime() };
        } catch {
          return null;
        }
      })
      .filter(Boolean)
      .sort((a, b) => b.mtime - a.mtime);

    return projects.length > 0
      ? { name: projects[0].name, path: projects[0].path }
      : null;
  } catch {
    return null;
  }
}

/**
 * List child repos in an orchestrator root.
 * Returns array of { name, path, hasGit, dirty, lastCommitAge } sorted by recency.
 *
 * @param {string} cwd - Orchestrator root directory
 * @returns {Array<{ name: string, path: string, hasGit: boolean, dirty: boolean, lastCommitAge: string }>}
 */
function listChildRepos(cwd) {
  const results = [];
  try {
    const entries = fs.readdirSync(cwd, { withFileTypes: true });
    for (const entry of entries) {
      if (
        !entry.isDirectory() ||
        entry.name.startsWith(".") ||
        entry.name === "scripts" ||
        entry.name === "node_modules"
      )
        continue;
      const repoPath = path.join(cwd, entry.name);
      const hasGit = fs.existsSync(path.join(repoPath, ".git"));
      if (!hasGit) {
        results.push({
          name: entry.name,
          path: repoPath,
          hasGit: false,
          dirty: false,
          lastCommitAge: "n/a",
        });
        continue;
      }

      let dirty = false;
      let lastCommitAge = "unknown";
      try {
        const { execSync } = require("child_process");
        const status = execSync("git status --porcelain", {
          cwd: repoPath,
          encoding: "utf8",
          timeout: 3000,
        }).trim();
        dirty = status.length > 0;

        const logLine = execSync(
          'git log -1 --format="%cr" 2>/dev/null || echo "no commits"',
          { cwd: repoPath, encoding: "utf8", timeout: 3000 },
        ).trim();
        lastCommitAge = logLine;
      } catch {}

      results.push({
        name: entry.name,
        path: repoPath,
        hasGit: true,
        dirty,
        lastCommitAge,
      });
    }
  } catch {}
  return results;
}

/**
 * Derive the current phase from workspace filesystem state.
 *
 * @param {string} workspacePath - Absolute path to workspace directory
 * @param {string} cwd - Project root
 * @returns {string} Phase identifier
 */
function derivePhase(workspacePath, cwd) {
  if (cwd) {
    const agentProjectDir = path.join(cwd, ".claude", "agents", "project");
    const skillProjectDir = path.join(cwd, ".claude", "skills", "project");
    if (dirHasFiles(agentProjectDir) || dirHasFiles(skillProjectDir)) {
      return "05-codify";
    }
  }
  if (dirHasFiles(path.join(workspacePath, "05-codify"))) return "05-codify";
  if (dirHasFiles(path.join(workspacePath, "04-validate")))
    return "04-validate";

  const completedCount = countFiles(
    path.join(workspacePath, "todos", "completed"),
  );
  if (
    completedCount > 0 ||
    dirHasFiles(path.join(workspacePath, "src")) ||
    dirHasFiles(path.join(workspacePath, "apps")) ||
    dirHasFiles(path.join(workspacePath, "03-drafts"))
  ) {
    return "03-implement";
  }

  const activeCount = countFiles(path.join(workspacePath, "todos", "active"));
  if (activeCount > 0 || dirHasFiles(path.join(workspacePath, "02-plans"))) {
    return "02-plan";
  }

  if (
    dirHasFiles(path.join(workspacePath, "01-analysis")) ||
    dirHasFiles(path.join(workspacePath, "03-user-flows"))
  ) {
    return "01-analyze";
  }

  return "not-started";
}

/**
 * Get todo progress counts.
 *
 * @param {string} workspacePath
 * @returns {{ active: number, completed: number }}
 */
function getTodoProgress(workspacePath) {
  return {
    active: countFiles(path.join(workspacePath, "todos", "active")),
    completed: countFiles(path.join(workspacePath, "todos", "completed")),
  };
}

/**
 * Read .session-notes content if present.
 *
 * @param {string} workspacePath
 * @returns {{ content: string, stale: boolean, age: string } | null}
 */
function getSessionNotes(workspacePath) {
  const notesPath = path.join(workspacePath, ".session-notes");
  return readSessionNotesFile(notesPath);
}

/**
 * Find all .session-notes across repo root, workspaces, and child repos.
 *
 * Searches:
 *   1. cwd/.session-notes (repo root)
 *   2. cwd/workspaces/<dir>/.session-notes (workspace dirs, if workspaces/ exists)
 *   3. cwd/<child>/.session-notes (child repos, if orchestrator mode)
 *
 * @param {string} cwd - Project root directory
 * @returns {Array<{ path: string, relativePath: string, workspace: string|null, content: string, stale: boolean, age: string, mtime: number }>}
 */
function findAllSessionNotes(cwd) {
  const results = [];

  // Check repo root
  const rootNotes = path.join(cwd, ".session-notes");
  const rootResult = readSessionNotesFile(rootNotes);
  if (rootResult) {
    results.push({
      ...rootResult,
      path: rootNotes,
      relativePath: ".session-notes",
      workspace: null,
    });
  }

  // Check workspace dirs (CO workspace pattern)
  const wsDir = path.join(cwd, "workspaces");
  try {
    const entries = fs.readdirSync(wsDir, { withFileTypes: true });
    for (const entry of entries) {
      if (
        !entry.isDirectory() ||
        entry.name === "instructions" ||
        entry.name.startsWith("_")
      )
        continue;
      const notesPath = path.join(wsDir, entry.name, ".session-notes");
      const result = readSessionNotesFile(notesPath);
      if (result) {
        results.push({
          ...result,
          path: notesPath,
          relativePath: `workspaces/${entry.name}/.session-notes`,
          workspace: entry.name,
        });
      }
    }
  } catch {}

  // Check child repos (orchestrator pattern)
  if (detectProjectMode(cwd) === "orchestrator") {
    try {
      const entries = fs.readdirSync(cwd, { withFileTypes: true });
      for (const entry of entries) {
        if (
          !entry.isDirectory() ||
          entry.name.startsWith(".") ||
          entry.name === "scripts" ||
          entry.name === "node_modules" ||
          entry.name === "workspaces"
        )
          continue;
        const childNotesPath = path.join(cwd, entry.name, ".session-notes");
        const result = readSessionNotesFile(childNotesPath);
        if (result) {
          results.push({
            ...result,
            path: childNotesPath,
            relativePath: `${entry.name}/.session-notes`,
            workspace: entry.name,
          });
        }
      }
    } catch {}
  }

  // Sort newest first
  results.sort((a, b) => b.mtime - a.mtime);
  return results;
}

/**
 * Read a single .session-notes file and compute age metadata.
 *
 * @param {string} notesPath - Absolute path to .session-notes
 * @returns {{ content: string, stale: boolean, age: string, mtime: number } | null}
 */
function readSessionNotesFile(notesPath) {
  try {
    const content = fs.readFileSync(notesPath, "utf8");
    const stat = fs.statSync(notesPath);
    const mtime = stat.mtime.getTime();
    const ageMs = Date.now() - mtime;
    const ageHours = Math.round(ageMs / (1000 * 60 * 60));
    const stale = ageMs > 24 * 60 * 60 * 1000;

    let age;
    if (ageHours < 1) age = "< 1h ago";
    else if (ageHours < 24) age = `${ageHours}h ago`;
    else age = `${Math.round(ageHours / 24)}d ago`;

    return { content: content.trim(), stale, age, mtime };
  } catch {
    return null;
  }
}

/**
 * Build a compact 1-line summary for per-turn injection.
 * Orchestrator: shows child repo status.
 * CO workspace: shows workspace phase and todos.
 *
 * @param {string} cwd
 * @returns {string | null}
 */
function buildWorkspaceSummary(cwd) {
  const mode = detectProjectMode(cwd);

  if (mode === "orchestrator") {
    const repos = listChildRepos(cwd);
    const gitRepos = repos.filter((r) => r.hasGit);
    const dirtyRepos = gitRepos.filter((r) => r.dirty);
    const parts = [`Orchestrator | ${gitRepos.length} repos`];
    if (dirtyRepos.length > 0) {
      parts.push(
        `${dirtyRepos.length} dirty: ${dirtyRepos.map((r) => r.name).join(", ")}`,
      );
    }
    return parts.join(" | ");
  }

  const ws = detectActiveWorkspace(cwd);
  if (!ws) return null;

  const phase = derivePhase(ws.path, cwd);
  const todos = getTodoProgress(ws.path);

  const parts = [ws.name, `Phase: ${phase}`];
  if (todos.active > 0 || todos.completed > 0) {
    parts.push(`Todos: ${todos.active} active / ${todos.completed} done`);
  }

  return parts.join(" | ");
}

// ── Helpers ────────────────────────────────────────────────────────────

function dirHasFiles(dirPath) {
  try {
    const entries = fs.readdirSync(dirPath);
    return entries.some((e) => !e.startsWith("."));
  } catch {
    return false;
  }
}

function countFiles(dirPath) {
  try {
    return fs.readdirSync(dirPath).filter((e) => !e.startsWith(".")).length;
  } catch {
    return 0;
  }
}

module.exports = {
  detectProjectMode,
  detectActiveWorkspace,
  listChildRepos,
  derivePhase,
  getTodoProgress,
  getSessionNotes,
  findAllSessionNotes,
  buildWorkspaceSummary,
  dirHasFiles,
  countFiles,
};
