# Daedalus Evals

This directory contains safe, repeatable local checks for Daedalus orchestration quality.

## Commands

Run the static suite:

```bash
python3 evals/run_static_evals.py
```

Save a static report:

```bash
python3 evals/run_static_evals.py --write-report
```

Score an agent transcript or work-order log:

```bash
python3 evals/score_agent_trace.py path/to/transcript.md
```

Save a trace score report:

```bash
python3 evals/score_agent_trace.py path/to/transcript.md --write-report
```

Reports are written to `evals/results/`.

## What These Evals Cover

- planning quality
- task completion
- regression prevention
- code quality
- latency
- hallucination control
- safety fallback
- recovery from failed attempts

The scripts do not call external APIs, install dependencies, run autonomous queued work, or modify project source files.

## Adding Evals

New evals should be deterministic when possible, use only local fixtures or repository files, and document:

- the risk being measured
- the command to run
- the pass threshold
- where reports are written
- what a failure usually means
