#!/usr/bin/env node
/**
 * Hook: auto-format
 * Event: PostToolUse
 * Matcher: Edit|Write
 * Purpose: Auto-format Python, JavaScript, TypeScript files.
 *          For multi-repo orchestrators, resolves formatters relative to
 *          the file's own repo (child repo), not the orchestrator root.
 *
 * Exit Codes:
 *   0 = success (continue)
 *   2 = blocking error (stop tool execution)
 *   other = non-blocking error (warn and continue)
 */

const fs = require("fs");
const { execFileSync } = require("child_process");
const path = require("path");

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
    const result = autoFormat(data);
    console.log(
      JSON.stringify({
        continue: true,
        hookSpecificOutput: {
          hookEventName: "PostToolUse",
          formatted: result.formatted,
          formatter: result.formatter,
        },
      }),
    );
    process.exit(0);
  } catch (error) {
    console.error(`[HOOK ERROR] ${error.message}`);
    console.log(JSON.stringify({ continue: true }));
    process.exit(1);
  }
});

function autoFormat(data) {
  const filePath = data.tool_input?.file_path;
  const cwd = data.cwd || process.cwd();

  if (!filePath || !fs.existsSync(filePath)) {
    return { formatted: false, formatter: "none" };
  }

  // Validate file is within the project directory to prevent symlink attacks
  const resolvedPath = path.resolve(filePath);
  const resolvedCwd = path.resolve(cwd);
  if (!resolvedPath.startsWith(resolvedCwd)) {
    return { formatted: false, formatter: "path outside project" };
  }

  // Determine the formatting context directory.
  // For orchestrators, find the child repo root (nearest .git parent).
  // Formatters are resolved relative to this directory.
  const formatCwd = findRepoRoot(resolvedPath, resolvedCwd);

  const ext = path.extname(filePath).toLowerCase();

  try {
    // Python files: black or ruff
    if (ext === ".py") {
      try {
        execFileSync("black", [filePath], { cwd: formatCwd, stdio: "pipe" });
        return { formatted: true, formatter: "black" };
      } catch {
        try {
          execFileSync("ruff", ["format", filePath], {
            cwd: formatCwd,
            stdio: "pipe",
          });
          return { formatted: true, formatter: "ruff" };
        } catch {
          return { formatted: false, formatter: "none (black/ruff not found)" };
        }
      }
    }

    // JavaScript/TypeScript files: prettier (use local if available)
    if ([".js", ".jsx", ".ts", ".tsx", ".json"].includes(ext)) {
      return tryPrettier(filePath, formatCwd);
    }

    // YAML/Markdown: prettier
    if ([".yaml", ".yml", ".md"].includes(ext)) {
      return tryPrettier(filePath, formatCwd);
    }

    return { formatted: false, formatter: "unsupported file type" };
  } catch (error) {
    return { formatted: false, formatter: `error: ${error.message}` };
  }
}

/**
 * Try to format with prettier, preferring local installation over npx.
 */
function tryPrettier(filePath, formatCwd) {
  // First try local prettier binary (avoids npx network fetch)
  const localPrettier = path.join(
    formatCwd,
    "node_modules",
    ".bin",
    "prettier",
  );
  if (fs.existsSync(localPrettier)) {
    try {
      execFileSync(localPrettier, ["--write", filePath], {
        cwd: formatCwd,
        stdio: "pipe",
      });
      return { formatted: true, formatter: "prettier (local)" };
    } catch {}
  }

  // Fall back to npx (may auto-install)
  try {
    execFileSync("npx", ["--no-install", "prettier", "--write", filePath], {
      cwd: formatCwd,
      stdio: "pipe",
    });
    return { formatted: true, formatter: "prettier" };
  } catch {
    return { formatted: false, formatter: "none (prettier not found)" };
  }
}

/**
 * Find the nearest repo root for a file path.
 * Walks up from the file directory until it finds a .git, stopping at cwd.
 */
function findRepoRoot(filePath, projectRoot) {
  let dir = path.dirname(filePath);
  while (dir.startsWith(projectRoot) && dir !== projectRoot) {
    if (fs.existsSync(path.join(dir, ".git"))) {
      return dir;
    }
    dir = path.dirname(dir);
  }
  return projectRoot;
}
