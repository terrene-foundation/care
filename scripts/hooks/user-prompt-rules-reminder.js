#!/usr/bin/env node
/**
 * Hook: user-prompt-rules-reminder
 * Event: UserPromptSubmit
 * Purpose: Inject critical rules into conversation on EVERY user message.
 *          This is the PRIMARY mechanism that survives context compression,
 *          because it runs fresh on every turn (independent of memory).
 *
 * Orchestrator-aware: adapts output for multi-repo vs CO workspace.
 *
 * Exit Codes:
 *   0 = success (continue)
 */

const fs = require("fs");
const path = require("path");
const {
  parseEnvFile,
  discoverModelsAndKeys,
  buildCompactSummary,
} = require("./lib/env-utils");
const {
  detectProjectMode,
  buildWorkspaceSummary,
  findAllSessionNotes,
} = require("./lib/workspace-utils");

const TIMEOUT_MS = 3000;
const timeout = setTimeout(() => {
  console.log(JSON.stringify({ continue: true }));
  process.exit(0);
}, TIMEOUT_MS);

let input = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk) => (input += chunk));
process.stdin.on("end", () => {
  clearTimeout(timeout);
  try {
    const data = JSON.parse(input);
    const result = buildReminder(data);
    console.log(JSON.stringify(result));
    process.exit(0);
  } catch {
    console.log(JSON.stringify({ continue: true }));
    process.exit(0);
  }
});

function buildReminder(data) {
  const cwd = data.cwd || process.cwd();
  const mode = detectProjectMode(cwd);

  // ── Build the reminder lines ──────────────────────────────────────
  const lines = [];

  // Line 1: Env summary — only for non-orchestrator (child repos handle their own .env)
  if (mode !== "orchestrator") {
    const envPath = path.join(cwd, ".env");
    if (fs.existsSync(envPath)) {
      const env = parseEnvFile(envPath);
      const discovery = discoverModelsAndKeys(env);
      const envSummary = buildCompactSummary(env, discovery);
      lines.push(`[ENV] ${envSummary}`);

      const failures = discovery.validations.filter(
        (v) => v.status === "MISSING_KEY",
      );
      if (failures.length > 0) {
        lines.push(
          `[ENV] CRITICAL: ${failures.length} model(s) missing API keys — LLM calls will fail!`,
        );
      }
    }
  }

  // Line 2: Behavioral rules (adapted per mode)
  if (mode === "orchestrator") {
    lines.push(
      "[ORCHESTRATOR] Read-only by default — do NOT modify child repo files without explicit instruction. " +
        "Content flow: foundation/ + publications/ → website/. " +
        "COC sync includes scripts/hooks/ — omitting them is the #1 failure mode.",
    );
  } else {
    lines.push(
      "[CO] Check session notes and journal before re-debating settled decisions. " +
        "Knowledge compounds — capture insights, don't discard them. " +
        "Human-on-the-loop: execute within envelope, escalate at boundaries.",
    );
  }

  // Line 3: Workspace/ecosystem context (survives compaction)
  try {
    const summary = buildWorkspaceSummary(cwd);
    if (summary) {
      const label = mode === "orchestrator" ? "[ECOSYSTEM]" : "[WORKSPACE]";
      lines.push(`${label} ${summary}`);
    }
  } catch {}

  // Session notes (critical for continuity across sessions)
  try {
    const allNotes = findAllSessionNotes(cwd);
    if (allNotes.length === 1) {
      const note = allNotes[0];
      const staleTag = note.stale ? " (STALE — verify before acting)" : "";
      const label = note.workspace ? `[${note.workspace}]` : "[root]";
      lines.push(
        `[SESSION-NOTES] ${label} Read ${note.relativePath} before starting work${staleTag} — updated ${note.age}`,
      );
    } else if (allNotes.length > 1) {
      const parts = allNotes.map((note) => {
        const label = note.workspace || "root";
        const staleTag = note.stale ? " STALE" : "";
        return `${label} (${note.age}${staleTag})`;
      });
      const noun = mode === "orchestrator" ? "repos" : "workspaces";
      lines.push(
        `[SESSION-NOTES] ${allNotes.length} ${noun} with notes: ${parts.join(" | ")}`,
      );
    }
  } catch {}

  return {
    continue: true,
    hookSpecificOutput: {
      hookEventName: "UserPromptSubmit",
      suppressOutput: false,
      message: lines.join("\n"),
    },
  };
}
