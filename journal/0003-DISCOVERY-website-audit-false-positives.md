---
type: DISCOVERY
date: 2026-03-31
created_at: 2026-03-31T20:15:00+08:00
author: co-authored
session_turn: 12
project: terrene
topic: First website audit produced 25 false gaps; verified audit found 7 real ones
phase: analyze
tags: [website, content-audit, false-positives, methodology]
---

# Website Content Audit: False Positives from Shallow Exploration

## Finding

An initial content audit of the website claimed 25 major gaps including "architecture is completely missing from the website." The user immediately challenged this ("architecture is mentioned on the first page, are you sure?"). A second, more thorough audit using the website's own skills and agents as ground truth found only 7 real gaps, all narrower than claimed.

## What Went Wrong (First Audit)

The first audit agent searched for specific class names (e.g., "DataFlowEngine") and concluded content was missing when those exact strings weren't found. The website uses descriptive names ("DataFlow framework") rather than class names. The agent also failed to read the landing page's interactive architecture diagram, which clearly shows Specs, Primitives, Engines, and Entrypoints with Delegate/TAOD, D/T/R, and all governance concepts.

## What Worked (Second Audit)

Three parallel agents with distinct scopes:

1. Website skills/agents inventory (what the website "knows")
2. Every website content page read in full (what's published)
3. Actual SDK pyproject.toml files (ground truth versions)

Cross-referencing these three sources produced verified, actionable gaps.

## The 7 Real Gaps

1. Version numbers stale (all 5 frameworks: Core 2.0→2.3.4, PACT 0.2→0.5, etc.)
2. Missing reference verticals (Arbor v0.1.0, Astra v0.1.0)
3. PACT Platform L3 undocumented (v0.4.0 with 42+ endpoints)
4. Express API not on public pages (in skills but not content)
5. GovernedSupervisor not on public pages (in skills but not content)
6. Engine-first pattern not documented as developer strategy
7. Internal skills knowledge exceeds published content

## For Discussion

1. The first audit searched for "DataFlowEngine" as a string but the website calls it "DataFlow framework." Should website content use class names, descriptive names, or both?
2. If the first audit had read the landing page's architecture section before claiming it was missing, would any of the 25 "gaps" have survived? What does this say about audit methodology?
3. The website's Claude Code skills contain significantly more current architecture knowledge than the published pages. Should there be a mechanism to detect when skills outpace content?
