#!/usr/bin/env node
/**
 * Hook: validate-hierarchy-grammar
 * Event: PostToolUse
 * Matcher: Edit|Write
 * Purpose: Enforce boundary-test blacklist and frozen dataclass pattern
 *          on governance and build files.
 *
 * Scoped to .py files under src/pact/governance/ and src/pact/build/.
 *
 * Exit Codes:
 *   0 = success (no violations)
 *   1 = warn (violations found, non-blocking)
 */

const fs = require("fs");
const path = require("path");

const TIMEOUT_MS = 4000;
const timeout = setTimeout(() => {
  console.error("[HOOK TIMEOUT] validate-hierarchy-grammar exceeded 4s limit");
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
    const result = validate(data);
    console.log(
      JSON.stringify({
        continue: true,
        hookSpecificOutput: {
          hookEventName: "PostToolUse",
          validation: result.messages,
        },
      }),
    );
    process.exit(result.exitCode);
  } catch (error) {
    console.error(`[HOOK ERROR] ${error.message}`);
    console.log(JSON.stringify({ continue: true }));
    process.exit(0);
  }
});

function validate(data) {
  const filePath = data.tool_input?.file_path || "";
  const ext = path.extname(filePath).toLowerCase();

  // Only .py files in src/pact/governance/ or src/pact/build/
  if (ext !== ".py") {
    return { exitCode: 0, messages: ["Not a Python file -- skipped"] };
  }
  const normalised = filePath.replace(/\\/g, "/");
  const inScope =
    normalised.includes("/src/pact/governance/") ||
    normalised.includes("/src/pact/build/");
  if (!inScope) {
    return {
      exitCode: 0,
      messages: ["Outside governance/build scope -- skipped"],
    };
  }

  let content;
  try {
    content = fs.readFileSync(filePath, "utf8");
  } catch {
    return { exitCode: 0, messages: ["Could not read file"] };
  }

  const messages = [];

  // --- Boundary-test blacklist (case-insensitive, whole-word) ---
  const blacklist = [
    [/\bTerrene\b/i, "Terrene"],
    [/\bAegis\b/i, "Aegis"],
    [/\bIntegrum\b/i, "Integrum"],
    [/\bAstra\b/i, "Astra"],
    [/\bArbor\b/i, "Arbor"],
    [/\btrading\b/i, "trading"],
    [/\badvisory\b/i, "advisory"],
    [/\bcompliance\b/i, "compliance"],
    [/\bMAS\b/, "MAS"],
    [/\bFINRA\b/, "FINRA"],
    [/\bFCA\b/, "FCA"],
    [/\bSFA\b/, "SFA"],
    [/\bDigital Marketing\b/i, "Digital Marketing"],
    [/\bAML\b/, "AML"],
    [/\bCFT\b/, "CFT"],
    [/\bKYC\b/, "KYC"],
    [/\btrader\b/i, "trader"],
    [/\badvisor\b/i, "advisor"],
    [/\bdm-team-lead\b/i, "dm-team-lead"],
    [/\bdm-content-creator\b/i, "dm-content-creator"],
  ];

  const lines = content.split("\n");
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line.trim().startsWith("#")) continue; // skip comments
    for (const [pattern, term] of blacklist) {
      if (pattern.test(line)) {
        messages.push(
          `WARNING: Domain term "${term}" at ${path.basename(filePath)}:${i + 1}. ` +
            `Framework code must be domain-agnostic (see rules/boundary-test.md).`,
        );
        break; // one warning per line is enough
      }
    }
  }

  // --- Frozen dataclass check (governance files only) ---
  if (normalised.includes("/src/pact/governance/")) {
    const dataclassRe = /@dataclass\b/g;
    let match;
    while ((match = dataclassRe.exec(content)) !== null) {
      const lineNum = content.substring(0, match.index).split("\n").length;
      const line = lines[lineNum - 1] || "";
      if (!line.includes("frozen=True") && !line.includes("frozen = True")) {
        messages.push(
          `WARNING: @dataclass without frozen=True at ${path.basename(filePath)}:${lineNum}. ` +
            `Governance dataclasses should be immutable.`,
        );
      }
    }
  }

  if (messages.length === 0) {
    return { exitCode: 0, messages: ["Hierarchy grammar checks passed"] };
  }

  return { exitCode: 1, messages };
}
