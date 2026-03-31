#!/usr/bin/env node

/**
 * Stop Hook - Graceful Shutdown Handler
 *
 * Purpose: Handle stop signals when Claude Code is interrupted
 * - Save final checkpoint before shutdown
 * - Mark session as interrupted
 * - Log observation for learning system
 * - Clean up temporary resources
 *
 * Orchestrator-aware: adapts shutdown message for multi-repo context.
 *
 * Exit Codes:
 * - 0: Success (allow graceful shutdown)
 *
 * Note: This hook should NEVER block shutdown - always return 0
 */

const fs = require("fs");
const path = require("path");
const {
  resolveLearningDir,
  ensureLearningDir,
} = require("./lib/learning-utils");
const {
  detectProjectMode,
  detectActiveWorkspace,
} = require("./lib/workspace-utils");

// Timeout fallback — prevents hanging the Claude Code session
const TIMEOUT_MS = 5000;
const _timeout = setTimeout(() => {
  console.log(JSON.stringify({ continue: true }));
  process.exit(0);
}, TIMEOUT_MS);

const HOME = process.env.HOME || process.env.USERPROFILE;
const CLAUDE_DIR = path.join(HOME, ".claude");
const CHECKPOINTS_DIR = path.join(CLAUDE_DIR, "checkpoints");

function ensureDir(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}

function saveCheckpoint(sessionId, cwd, pendingWork) {
  try {
    ensureDir(CHECKPOINTS_DIR);
    const checkpoint = {
      timestamp: new Date().toISOString(),
      session_id: sessionId,
      cwd: cwd,
      type: "stop",
      pending_work: pendingWork || null,
      interrupted: true,
    };
    const checkpointPath = path.join(
      CHECKPOINTS_DIR,
      `stop_${sessionId}_${Date.now()}.json`,
    );
    fs.writeFileSync(checkpointPath, JSON.stringify(checkpoint, null, 2));
    return checkpointPath;
  } catch {
    return null;
  }
}

function logObservation(sessionId, reason, cwd) {
  try {
    const learningDir = ensureLearningDir(cwd);
    const observationsFile = path.join(learningDir, "observations.jsonl");
    const observation = {
      timestamp: new Date().toISOString(),
      type: "stop",
      session_id: sessionId,
      reason: reason || "unknown",
      success: true,
    };
    fs.appendFileSync(observationsFile, JSON.stringify(observation) + "\n");
    return true;
  } catch {
    return false;
  }
}

function cleanupResources(cwd) {
  try {
    if (cwd && fs.existsSync(cwd)) {
      const tmpPattern = /^\.claude-tmp/;
      const files = fs.readdirSync(cwd);
      for (const file of files) {
        if (tmpPattern.test(file)) {
          try {
            fs.unlinkSync(path.join(cwd, file));
          } catch {}
        }
      }
    }
    return true;
  } catch {
    return false;
  }
}

async function main() {
  let input = "";
  process.stdin.setEncoding("utf8");

  for await (const chunk of process.stdin) {
    input += chunk;
  }

  let data = {};
  try {
    data = JSON.parse(input);
  } catch {}

  const sessionId = (data.session_id || `stop_${Date.now()}`).replace(
    /[^a-zA-Z0-9_-]/g,
    "_",
  );
  const cwd = data.cwd || process.cwd();
  const pendingWork = data.pending_work || null;
  const reason = data.reason || "signal";

  // Context-aware shutdown message
  try {
    const mode = detectProjectMode(cwd);
    if (mode === "orchestrator") {
      console.error(
        `[ORCHESTRATOR] Session ending. Run /wrapup next time before closing to save ecosystem context.`,
      );
    } else {
      const ws = detectActiveWorkspace(cwd);
      if (ws) {
        console.error(
          `[WORKSPACE] Session ending for ${ws.name}. Run /wrapup next time before closing to save session context.`,
        );
      }
    }
  } catch {}

  saveCheckpoint(sessionId, cwd, pendingWork);
  logObservation(sessionId, reason, cwd);
  cleanupResources(cwd);

  console.log(JSON.stringify({ continue: true }));
  process.exit(0);
}

main().catch(() => {
  console.log(JSON.stringify({ continue: true }));
  process.exit(0);
});
