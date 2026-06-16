# Orchestration

Daedalus should emulate the useful public operating pattern of long-horizon AI software teams: decomposition, specialist routing, persistent memory, self-review, safety review, evaluation, and recovery.

## Loop

1. Capture the operator goal.
2. Convert the goal into `/memory/TASK_GRAPH.md`.
3. Classify tasks by dependency, risk, owner role, and approval requirements.
4. Run parallel specialists only when their write scopes do not conflict.
5. Merge findings through a parent synthesis.
6. Validate with tests, smoke checks, and documentation review.
7. Update memory.

## Specialist Roles

- `repo_cartographer`: read-only repository mapper.
- `architecture_planner`: target architecture and boundaries.
- `implementation_planner`: staged execution plan.
- `memory_system_designer`: memory design and update policy.
- `evals_and_benchmark_designer`: repeatable evaluation design.
- `safety_and_defensive_security_reviewer`: defensive safety/security review.
- `test_engineer`: test plan and safe smoke checks.
- `docs_and_operator_guide_writer`: operator documentation.

## Conflict Rule

When agents propose conflicting edits:

1. Pause implementation.
2. Inspect both proposals.
3. Merge manually.
4. Run tests.
5. Log the decision in `/memory/DECISIONS.md`.
