#!/usr/bin/env node
/**
 * Hook: pre-compact
 * Event: PreCompact
 * Purpose: Save critical context before compaction
 *
 *
 * Exit Codes:
 *   0 = success (continue)
 *   2 = blocking error (stop tool execution)
 *   other = non-blocking error (warn and continue)
 */

const fs = require("fs");
const path = require("path");
const {
  resolveLearningDir,
  ensureLearningDir,
  logObservation: logLearningObservation,
  countObservations,
} = require("./lib/learning-utils");
const {
  detectProjectMode,
  detectActiveWorkspace,
} = require("./lib/workspace-utils");

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
    savePreCompactState(data);
    // PreCompact hooks don't support hookSpecificOutput in schema
    console.log(JSON.stringify({ continue: true }));
    process.exit(0);
  } catch (error) {
    console.error(`[HOOK ERROR] ${error.message}`);
    console.log(JSON.stringify({ continue: true }));
    process.exit(1);
  }
});

function savePreCompactState(data) {
  // Sanitize session_id to prevent path traversal
  const session_id = (data.session_id || "").replace(/[^a-zA-Z0-9_-]/g, "_");
  const cwd = data.cwd;
  const homeDir = process.env.HOME || process.env.USERPROFILE;
  const checkpointDir = path.join(homeDir, ".claude", "checkpoints");
  const learningDir = resolveLearningDir(cwd);

  // Ensure directories exist
  [checkpointDir].forEach((dir) => {
    try {
      fs.mkdirSync(dir, { recursive: true });
    } catch {}
  });
  ensureLearningDir(cwd);

  const checkpoint = {
    session_id,
    cwd,
    compactedAt: new Date().toISOString(),
    preservedContext: {
      projectType: detectProjectTypeSimple(cwd),
      recentlyModified: findRecentlyModified(cwd),
      workspaceAreas: detectWorkspaceAreas(cwd),
    },
  };

  try {
    // Save checkpoint
    const checkpointFile = path.join(
      checkpointDir,
      `${session_id}-${Date.now()}.json`,
    );
    fs.writeFileSync(checkpointFile, JSON.stringify(checkpoint, null, 2));

    // Log observation
    logLearningObservation(
      cwd,
      "pre_compact",
      {
        project_type: "co-workspace",
        recently_modified_count:
          checkpoint.preservedContext.recentlyModified.length,
        workspace_areas: checkpoint.preservedContext.workspaceAreas,
      },
      {
        session_id,
      },
    );

    // ── Remind to save session notes before compaction ──────
    try {
      const mode = detectProjectMode(cwd);
      if (mode === "orchestrator") {
        console.error(
          `[ORCHESTRATOR] Context compacting. Run /wrapup to save ecosystem context before losing it.`,
        );
      } else {
        const ws = detectActiveWorkspace(cwd);
        if (ws) {
          console.error(
            `[WORKSPACE] Context compacting. Before losing context, write session notes to workspaces/${ws.name}/.session-notes (or run /wrapup).`,
          );
        }
      }
    } catch {}

    // Clean up old checkpoints (keep last 10 per session)
    cleanupOldCheckpoints(checkpointDir, session_id, 10);

    return { checkpointed: true, path: checkpointFile };
  } catch (error) {
    return { checkpointed: false, error: error.message };
  }
}

/**
 * Find recently modified files (last hour) — workspace artifacts and documents.
 */
function findRecentlyModified(cwd) {
  try {
    const oneHourAgo = Date.now() - 60 * 60 * 1000;
    const recentFiles = [];

    const files = fs
      .readdirSync(cwd)
      .filter((f) => f.endsWith(".md") || f.endsWith(".json"));

    for (const file of files) {
      try {
        const stats = fs.statSync(path.join(cwd, file));
        if (stats.mtime.getTime() > oneHourAgo) {
          recentFiles.push(file);
        }
      } catch {}
    }

    // Also check workspaces/ top level
    try {
      const wsDir = path.join(cwd, "workspaces");
      if (fs.existsSync(wsDir)) {
        const entries = fs.readdirSync(wsDir, { withFileTypes: true });
        for (const entry of entries) {
          if (entry.isDirectory() && !entry.name.startsWith("_")) {
            try {
              const subFiles = fs.readdirSync(path.join(wsDir, entry.name));
              for (const f of subFiles.filter((f) => f.endsWith(".md"))) {
                const stats = fs.statSync(path.join(wsDir, entry.name, f));
                if (stats.mtime.getTime() > oneHourAgo) {
                  recentFiles.push(`workspaces/${entry.name}/${f}`);
                }
              }
            } catch {}
          }
        }
      }
    } catch {}

    return recentFiles.slice(0, 20);
  } catch {
    return [];
  }
}

/**
 * Detect which workspace areas exist (workspaces/ subdirectories).
 */
function detectWorkspaceAreas(cwd) {
  const areas = {};
  try {
    const wsDir = path.join(cwd, "workspaces");
    if (!fs.existsSync(wsDir)) return areas;

    const entries = fs.readdirSync(wsDir, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.isDirectory() && !entry.name.startsWith("_")) {
        try {
          const count = fs
            .readdirSync(path.join(wsDir, entry.name))
            .filter((f) => !f.startsWith(".")).length;
          if (count > 0) {
            areas[entry.name] = count;
          }
        } catch {}
      }
    }
  } catch {}
  return areas;
}

/**
 * Simple project type detection for checkpoint/observation logging.
 */
function detectProjectTypeSimple(cwd) {
  try {
    if (fs.existsSync(path.join(cwd, ".claude", "sync-manifest.yaml")))
      return "orchestrator";
    if (fs.existsSync(path.join(cwd, "workspaces"))) return "co-workspace";
    return "co-project";
  } catch {
    return "unknown";
  }
}

function cleanupOldCheckpoints(checkpointDir, sessionId, keepCount) {
  try {
    const prefix = `${sessionId}-`;
    const files = fs
      .readdirSync(checkpointDir)
      .filter((f) => f.startsWith(prefix))
      .map((f) => ({
        name: f,
        path: path.join(checkpointDir, f),
        mtime: fs.statSync(path.join(checkpointDir, f)).mtime,
      }))
      .sort((a, b) => b.mtime - a.mtime);

    // Remove files beyond keepCount
    for (const file of files.slice(keepCount)) {
      try {
        fs.unlinkSync(file.path);
      } catch {}
    }
  } catch {}
}
