# Daedalus Test Plan

## Current Test Commands

Run commands from the repository root.

```bash
python3 evals/run_static_evals.py
python3 evals/score_agent_trace.py path/to/transcript.md
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests
```

Optional report-writing variants:

```bash
python3 evals/run_static_evals.py --write-report
python3 evals/score_agent_trace.py path/to/transcript.md --write-report
```

`uv run pytest` is referenced in planning docs, but this checkout does not currently define pytest configuration or a pytest dependency in `pyproject.toml`.

## Existing Coverage

- `evals/run_static_evals.py` checks required project paths, memory/task graph structure, safety boundary text, source syntax, JSON parseability, and worker status latency.
- `evals/score_agent_trace.py` scores saved transcripts for planning quality, task completion, regression prevention, code quality, latency, hallucination control, safety fallback, and recovery language.
- `tests/test_work_orders_smoke.py` covers the stable work-order queue lifecycle with a temporary work-order directory: slug generation, file creation, title/body extraction, status moves, and invalid status rejection.

## Missing Coverage

- CLI command smoke tests for `rsps-worker`, `rsps-cron`, `rsps-ponytail`, `rsps-git`, and `rsps-dashboard` help/status paths.
- Dashboard API schema tests for `/api/status`, `/api/enqueue`, and `/api/action`.
- Work-order edge cases such as duplicate timestamps, malformed Markdown titles, queue ordering with multiple files, and failed filesystem moves.
- Autonomy gate tests proving `run-once` and `run-duo` cannot execute when `RSPS_ALLOW_AUTONOMOUS` is false.
- Git/worktree behavior around branch naming, cleanup, commit failure handling, and remote push configuration.
- Asset pipeline tests for manifest shape, expected PNG outputs, and stale generated asset detection.
- CrewAI/model routing tests with mocked clients; no tests should call external model APIs by default.

## Smoke Test Policy

Keep smoke tests local, deterministic, and dependency-light. Prefer temporary directories and mocked environment variables over writing project state. Do not run autonomous workers, install cron, call model APIs, or modify the configured RSPS repository in the default suite.
