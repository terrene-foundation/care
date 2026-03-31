#!/usr/bin/env node
/**
 * Hook: session-end
 * Event: SessionEnd
 * Purpose: Save session state for future resumption
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

// Timeout fallback — prevents hanging the Claude Code session
const TIMEOUT_MS = 15000;
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
    saveSession(data);
    // SessionEnd hooks don't support hookSpecificOutput in schema
    console.log(JSON.stringify({ continue: true }));
    process.exit(0);
  } catch (error) {
    console.error(`[HOOK ERROR] ${error.message}`);
    console.log(JSON.stringify({ continue: true }));
    process.exit(1);
  }
});

function saveSession(data) {
  // Sanitize session_id to prevent path traversal
  const session_id = (data.session_id || "").replace(/[^a-zA-Z0-9_-]/g, "_");
  const cwd = data.cwd;
  const homeDir = process.env.HOME || process.env.USERPROFILE;
  const sessionDir = path.join(homeDir, ".claude", "sessions");
  const learningDir = resolveLearningDir(cwd);

  // Ensure directories exist
  [sessionDir].forEach((dir) => {
    try {
      fs.mkdirSync(dir, { recursive: true });
    } catch {}
  });
  ensureLearningDir(cwd);

  // Collect session statistics
  const sessionData = {
    session_id,
    cwd,
    endedAt: new Date().toISOString(),
    stats: collectSessionStats(cwd),
  };

  try {
    // Save to session-specific file
    const sessionFile = path.join(sessionDir, `${session_id}.json`);
    fs.writeFileSync(sessionFile, JSON.stringify(sessionData, null, 2));

    // Save as last session for quick resume
    const lastSessionFile = path.join(sessionDir, "last-session.json");
    fs.writeFileSync(lastSessionFile, JSON.stringify(sessionData, null, 2));

    // Log session summary observation
    logLearningObservation(
      cwd,
      "session_summary",
      {
        file_counts: sessionData.stats,
        project_type: detectProjectTypeSimple(cwd),
        duration_estimate: estimateSessionDuration(session_id, sessionDir),
      },
      {
        session_id,
      },
    );

    // --- Feedback loop: render instincts to rules file ---
    try {
      writeInstinctsRule(cwd, learningDir);
    } catch {}

    // Clean up old sessions (keep last 20)
    cleanupOldSessions(sessionDir, 20);

    return { saved: true, path: sessionFile };
  } catch (error) {
    return { saved: false, error: error.message };
  }
}

/**
 * Collect stats relevant to a research workspace.
 * Counts documents, workspace artifacts, and journal entries.
 */
function collectSessionStats(cwd) {
  try {
    const stats = {
      markdownFiles: 0,
      workspaceFiles: 0,
      journalEntries: 0,
    };

    // Count top-level markdown files
    const files = fs.readdirSync(cwd).filter((f) => f.endsWith(".md"));
    stats.markdownFiles = files.length;

    // Count workspace artifacts
    try {
      const wsDir = path.join(cwd, "workspaces");
      if (fs.existsSync(wsDir)) {
        const entries = fs
          .readdirSync(wsDir, { withFileTypes: true })
          .filter((e) => e.isDirectory() && !e.name.startsWith("_"));
        stats.workspaceFiles = entries.length;

        // Count journal entries across workspaces
        for (const entry of entries) {
          try {
            const journalDir = path.join(wsDir, entry.name, "journal");
            if (fs.existsSync(journalDir)) {
              stats.journalEntries += fs
                .readdirSync(journalDir)
                .filter((f) => f.endsWith(".md") && f !== "README.md").length;
            }
          } catch {}
        }
      }
    } catch {}

    return stats;
  } catch {
    return {};
  }
}

function estimateSessionDuration(sessionId, sessionDir) {
  try {
    const sessionFile = path.join(sessionDir, `${sessionId}.json`);
    if (fs.existsSync(sessionFile)) {
      const data = JSON.parse(fs.readFileSync(sessionFile, "utf8"));
      if (data.startedAt) {
        const start = new Date(data.startedAt).getTime();
        const end = Date.now();
        return Math.round((end - start) / 1000); // seconds
      }
    }
    return null;
  } catch {
    return null;
  }
}

/**
 * Render learned instincts to .claude/rules/learned-instincts.md
 * so Claude Code auto-loads them on the next session.
 */
function writeInstinctsRule(cwd, learningDir) {
  const { renderInstincts } = require("./lib/instinct-renderer");
  const markdown = renderInstincts(learningDir);
  if (!markdown) return;

  const rulesDir = path.join(cwd, ".claude", "rules");
  try {
    fs.mkdirSync(rulesDir, { recursive: true });
  } catch {}

  const rulePath = path.join(rulesDir, "learned-instincts.md");
  fs.writeFileSync(rulePath, markdown);
}

/**
 * Simple project type detection for observation logging.
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

function cleanupOldSessions(sessionDir, keepCount) {
  try {
    const files = fs
      .readdirSync(sessionDir)
      .filter((f) => f.endsWith(".json") && f !== "last-session.json")
      .map((f) => ({
        name: f,
        path: path.join(sessionDir, f),
        mtime: fs.statSync(path.join(sessionDir, f)).mtime,
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
