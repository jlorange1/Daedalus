# Failed Attempts

## 2026-06-16

- Attempt: Iterative fantasy/Stardew dashboard polish.
- Failure: User rejected the direction and reported broken graphics.
- Lesson: Do not keep layering old asset styles when the requested direction changes. Prefer a clean active skin and hard-disable obsolete assets.

- Attempt: Browser verification inside the default sandbox.
- Failure: Headless Chromium may fail with sandbox host shutdown errors.
- Lesson: Use the approved escalated Playwright command path for dashboard screenshot verification when sandboxed launch fails.
