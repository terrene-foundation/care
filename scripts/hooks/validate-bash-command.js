#!/usr/bin/env node
/**
 * Hook: validate-bash-command
 * Event: PreToolUse
 * Matcher: Bash
 * Purpose: Block dangerous commands, suggest tmux for long-running,
 *          enforce .env loading for pytest/python commands.
 *          Orchestrator-aware: resolves .env relative to the target
 *          child repo when commands use cd or -C flags.
 *
 * Exit Codes:
 *   0 = success (continue)
 *   2 = blocking error (stop tool execution)
 *   other = non-blocking error (warn and continue)
 */

const fs = require("fs");
const path = require("path");
const {
  logObservation: logLearningObservation,
} = require("./lib/learning-utils");

// Timeout handling for PreToolUse hooks (5 second limit)
const TIMEOUT_MS = 5000;
const timeout = setTimeout(() => {
  console.error("[HOOK TIMEOUT] validate-bash-command exceeded 5s limit");
  console.log(JSON.stringify({ continue: true }));
  process.exit(1);
}, TIMEOUT_MS);

let input = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk) => (input += chunk));
process.stdin.on("end", () => {
  clearTimeout(timeout);
  try {
    const data = JSON.parse(input);
    const result = validateBashCommand(data);
    console.log(
      JSON.stringify({
        continue: result.continue,
        hookSpecificOutput: {
          hookEventName: "PreToolUse",
          validation: result.message,
        },
      }),
    );
    process.exit(result.exitCode);
  } catch (error) {
    console.error(`[HOOK ERROR] ${error.message}`);
    console.log(JSON.stringify({ continue: true }));
    process.exit(1);
  }
});

function validateBashCommand(data) {
  const command = data.tool_input?.command || "";
  const cwd = data.cwd || process.cwd();

  // BLOCK: Dangerous commands (with evasion-resistant patterns)
  const dangerousPatterns = [
    {
      pattern: /rm\s+(-[rRf]+\s+)*\/($|\s|\*)/,
      message: "Blocked: rm on root filesystem",
    },
    {
      pattern: /rm\s+--(?:recursive|force)\b/,
      message: "Blocked: rm recursive/force with long flags",
    },
    { pattern: />\s*\/dev\/sd/, message: "Blocked: Writing to block device" },
    { pattern: /mkfs\./, message: "Blocked: Filesystem formatting" },
    { pattern: /dd\s+if=.*of=\/dev\/sd/, message: "Blocked: dd to disk" },
    { pattern: /:\(\)\{\s*:\|:&\s*\};:/, message: "Blocked: Fork bomb" },
    {
      pattern: /(\w+)\(\)\s*\{\s*\1\s*\|\s*\1\s*&\s*\}\s*;\s*\1/,
      message: "Blocked: Fork bomb variant",
    },
    { pattern: /chmod\s+-R\s+777\s+\//, message: "Blocked: chmod 777 on root" },
    {
      pattern: /curl.*\|\s*(ba)?sh/,
      message: "WARNING: Piping curl to shell is dangerous",
    },
    {
      pattern: /wget.*\|\s*(ba)?sh/,
      message: "WARNING: Piping wget to shell is dangerous",
    },
  ];

  for (const { pattern, message } of dangerousPatterns) {
    if (pattern.test(command)) {
      try {
        logLearningObservation(cwd, "error_occurrence", {
          error_type: "dangerous_command",
          pattern: pattern.source,
          blocked: message.startsWith("Blocked"),
        });
      } catch {}

      if (message.startsWith("Blocked")) {
        return { continue: false, exitCode: 2, message };
      }
      return { continue: true, exitCode: 0, message };
    }
  }

  // ====================================================================
  // ENFORCE: .env loading for pytest/python commands
  // Resolve the effective working directory from cd/git -C patterns
  // ====================================================================
  const isPytest = /\bpytest\b/.test(command);
  const isPython = /\bpython\b/.test(command) || /\bpython3\b/.test(command);

  if (isPytest || isPython) {
    // Determine the effective cwd (may be a child repo)
    const effectiveCwd = resolveEffectiveCwd(command, cwd);

    // Log enriched test pattern observation
    try {
      const testPathMatch = command.match(
        /(?:pytest|python3?\s+-m\s+pytest)\s+([^\s;|&]+)/,
      );
      const testPath = testPathMatch ? testPathMatch[1] : null;

      let testTier = "unit";
      if (testPath) {
        if (/e2e|playwright|end.to.end/i.test(testPath)) testTier = "e2e";
        else if (/integrat/i.test(testPath)) testTier = "integration";
      }

      logLearningObservation(effectiveCwd, "test_pattern", {
        test_tier: testTier,
        test_path: testPath,
        is_pytest: isPytest,
        command_flags: extractTestFlags(command),
      });
    } catch {}

    // Check if .env exists at the effective cwd (child repo or root)
    let envExists = false;
    try {
      envExists = fs.existsSync(path.join(effectiveCwd, ".env"));
    } catch {}

    if (envExists) {
      const loadsEnv =
        /dotenv/.test(command) ||
        /\.env/.test(command) ||
        /OPENAI_API_KEY=/.test(command) ||
        /--env-file/.test(command) ||
        /source\s+\.env/.test(command) ||
        /export\s+/.test(command) ||
        /env\s+/.test(command);

      if (!loadsEnv && isPytest) {
        return {
          continue: true,
          exitCode: 0,
          message:
            "REMINDER: .env exists but pytest may not load it. Consider: pytest-dotenv plugin OR prefix with env vars from .env.",
        };
      }
    }
  }

  // WARN: Long-running commands outside tmux/background
  const longRunningPatterns = [
    /npm\s+run\s+(dev|start|serve)/,
    /yarn\s+(dev|start|serve)/,
    /python\s+-m\s+http\.server/,
    /uvicorn/,
    /flask\s+run/,
    /node\s+.*server/,
    /docker\s+compose\s+up(?!\s+-d)/,
  ];

  const inTmux = process.env.TMUX || process.env.TERM_PROGRAM === "tmux";
  const isBackground =
    /&\s*$/.test(command) ||
    /--background/.test(command) ||
    /-d\s/.test(command);

  for (const pattern of longRunningPatterns) {
    if (pattern.test(command) && !inTmux && !isBackground) {
      return {
        continue: true,
        exitCode: 0,
        message:
          "WARNING: Long-running command. Consider using run_in_background or tmux.",
      };
    }
  }

  // WARN: Git push - reminder for security review
  if (/git\s+push/.test(command)) {
    return {
      continue: true,
      exitCode: 0,
      message: "REMINDER: Did you run security-reviewer before pushing?",
    };
  }

  // WARN: Git commit - reminder for review
  if (/git\s+commit/.test(command)) {
    return {
      continue: true,
      exitCode: 0,
      message:
        "REMINDER: Code review completed? Consider delegating to intermediate-reviewer.",
    };
  }

  // Log cargo test / cargo clippy / npm test observations
  const isCargoTest = /\bcargo\s+test\b/.test(command);
  const isCargoClippy = /\bcargo\s+clippy\b/.test(command);
  const isCargoBuild = /\bcargo\s+build\b/.test(command);
  const isNpmTest = /\bnpm\s+test\b/.test(command);

  if (isCargoTest || isCargoClippy || isCargoBuild) {
    try {
      const crateMatch = command.match(/-p\s+(\S+)/);
      logLearningObservation(cwd, "test_pattern", {
        test_tier: isCargoTest
          ? "cargo_test"
          : isCargoClippy
            ? "clippy"
            : "cargo_build",
        test_path: crateMatch ? crateMatch[1] : "workspace",
        is_rust: true,
        command_flags: extractTestFlags(command),
      });
    } catch {}
  }

  if (isNpmTest) {
    try {
      logLearningObservation(cwd, "test_pattern", {
        test_tier: "npm_test",
        is_node: true,
        command_flags: extractTestFlags(command),
      });
    } catch {}
  }

  return { continue: true, exitCode: 0, message: "Validated" };
}

/**
 * Resolve the effective working directory from a command.
 * Handles: cd <dir> && ..., git -C <dir> ..., etc.
 */
function resolveEffectiveCwd(command, cwd) {
  // Match: cd <dir> && ...
  const cdMatch = command.match(/^cd\s+([^\s;&|]+)/);
  if (cdMatch) {
    const target = cdMatch[1].replace(/^["']|["']$/g, "");
    const resolved = path.resolve(cwd, target);
    if (fs.existsSync(resolved)) return resolved;
  }

  // Match: git -C <dir> ...
  const gitCMatch = command.match(/git\s+-C\s+([^\s;&|]+)/);
  if (gitCMatch) {
    const target = gitCMatch[1].replace(/^["']|["']$/g, "");
    const resolved = path.resolve(cwd, target);
    if (fs.existsSync(resolved)) return resolved;
  }

  return cwd;
}

/**
 * Extract test-relevant flags from command for learning.
 */
function extractTestFlags(command) {
  const flags = [];
  if (/-x\b/.test(command)) flags.push("fail-fast");
  if (/--tb=/.test(command)) flags.push("traceback");
  if (/-v\b|--verbose\b/.test(command)) flags.push("verbose");
  if (/--cov\b/.test(command)) flags.push("coverage");
  if (/-k\s/.test(command)) flags.push("keyword-filter");
  if (/--workspace\b/.test(command)) flags.push("workspace");
  if (/--release\b/.test(command)) flags.push("release");
  return flags;
}
