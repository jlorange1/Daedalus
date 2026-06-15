# Ponytail Layer

This project uses Ponytail-style lazy senior developer mode, adapted from
https://github.com/DietrichGebert/ponytail.

Lazy means efficient, not careless. Before adding code, stop at the first option
that works:

1. Do we need to build this at all?
2. Does the standard library already do it?
3. Does the platform, framework, or RSPS engine already provide it?
4. Does an installed dependency already solve it?
5. Can this be one line or a config/data change?
6. Only then, write the smallest correct implementation.

Rules:
- Prefer deletion over addition.
- Prefer data/config changes over new code when safe.
- Do not add abstractions, services, schedulers, or dependencies unless the work order requires them.
- Do not skip input validation, auth checks, permission checks, persistence safety, security, accessibility, or tests at trust boundaries.
- Mark intentional shortcuts with a `ponytail:` comment that names the ceiling and upgrade path.
- Non-trivial logic needs one small runnable check: a self-check, script, assertion, or focused test.
