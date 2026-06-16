---
name: daedalus-evals
description: Run and extend Daedalus evaluation workflows, including static evals, trace scoring, unittest smoke tests, dashboard asset and JSON checks, result reports, and failure logging.
---

# Daedalus Evals

Use this skill when validating Daedalus behavior, adding eval coverage, investigating eval failures, or preparing an eval report.

## Workflow

1. Start by locating the project's existing eval, test, dashboard, and report conventions. Prefer established scripts and output paths over new ones.
2. Run the narrowest relevant check first, then broaden only when the result affects shared behavior or release confidence.
3. Capture exact commands, result files, failing cases, and notable logs so failures can be reproduced.
4. When extending evals, add small fixtures or cases that isolate the behavior under test. Keep deterministic inputs, expected outputs, and scoring criteria close together.
5. Do not rewrite unrelated eval harnesses, dashboards, or reports while adding coverage.

## Eval Types

- **Static evals**: Verify prompt/config/schema/content rules without executing long workflows. Use for file presence, required fields, policy constraints, and deterministic lint-style checks.
- **Trace scoring**: Score run traces against explicit criteria such as task completion, tool choice, state transitions, latency, missing steps, and malformed outputs. Preserve raw traces or compact excerpts for debugging.
- **Unittest smoke tests**: Add or run lightweight `unittest` coverage for core paths, imports, CLI entrypoints, scoring helpers, and report generation. Keep smoke tests fast and non-networked unless the project already marks them otherwise.
- **Dashboard asset/JSON checks**: Validate dashboard manifests, JSON shape, referenced assets, file paths, chart data fields, and readable report metadata before visual review.
- **Result reports**: Summarize pass/fail counts, command lines, changed coverage, scored traces, dashboard checks, and any skipped tests with reasons.
- **Failure logging**: Record the failing command, exception or assertion, input fixture, expected behavior, observed behavior, and the next debugging lead.

## Implementation Guidance

- Prefer Python standard library tools such as `json`, `pathlib`, and `unittest` when the repo has no stronger local pattern.
- Keep eval runners composable: small functions for loading fixtures, running checks, scoring results, and writing reports.
- Make report output stable for diffs by sorting keys, ordering cases deterministically, and avoiding timestamps unless the existing format requires them.
- Treat missing assets, invalid JSON, skipped traces, and empty result sets as explicit outcomes rather than silent success.
- If a check depends on optional services, environment variables, or generated artifacts, fail with a clear setup message or mark the case skipped using the repo's existing convention.

## Reporting Back

Final responses should include the commands run, the files or reports produced, headline results, and unresolved failures. If tests could not be run, state the blocker and the most useful next command.
