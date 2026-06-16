# Decisions

## 2026-06-16

- Date: 2026-06-16
- Decision: Pivot dashboard visual direction from fantasy/Stardew-inspired UI to sci-fi RSPS control panel.
- Why: User explicitly rejected the Stardew look and requested glowing sci-fi agent cores and modular control windows.
- Alternatives considered: Continue fantasy polish; rebuild as retro GBA; create fully separate app.
- Risk: Old fantasy assets may remain in repository and confuse future agents.
- Rollback plan: Revert commits `5f18309` and `7b3dc84` if the sci-fi direction is rejected.

- Date: 2026-06-16
- Decision: Initialize Markdown memory and orchestration docs before deeper implementation.
- Why: User requested Fable/Mythos-style long-horizon orchestration with persistent memory and specialist agents.
- Alternatives considered: Jump directly to implementation.
- Risk: Docs may drift if not maintained.
- Rollback plan: Remove or revise docs/memory files before orchestration code depends on them.

- Date: 2026-06-16
- Decision: Install the RSPS Java workflow as user-local toolchains instead of host rpm-ostree packages.
- Why: Fedora Atomic/Bazzite repositories did not provide `java-11-openjdk-devel`, while the configured 2009scape source explicitly requires JDK 11 and Maven.
- Alternatives considered: Layer host packages with rpm-ostree; use a toolbox/distrobox container; install a newer JDK.
- Risk: User-local tools depend on `~/.local/bin` being on PATH.
- Rollback plan: Remove `~/.local/share/daedalus-toolchains` and the symlinks/copy in `~/.local/bin`.

- Date: 2026-06-16
- Decision: Remove unlabelled mock dashboard fixture data and replace active queue fallbacks with explicit empty states.
- Why: User requested all mock data removed and the dashboard should reflect live operational state.
- Alternatives considered: Keep demo data behind a flag; leave visual backlog for aesthetics.
- Risk: Empty live queues look less populated until real work orders exist.
- Rollback plan: Reintroduce an explicit `demo_mode` API/UI flag with clearly labeled demo cards.

- Date: 2026-06-16
- Decision: Keep project skill sources in `/skills` and symlink them into `~/.codex/skills`.
- Why: The user wants the skills usable by Codex while preserving repo-versioned source files.
- Alternatives considered: Repo-local only; copy files into `~/.codex/skills`.
- Risk: Symlinks can break if the repository is moved.
- Rollback plan: Remove the symlinks from `~/.codex/skills` or replace them with copied skill folders.

- Date: 2026-06-16
- Decision: Add `[agents] max_threads = 6`, `max_depth = 1`, and `job_max_runtime_seconds = 1800` to `/var/home/Scaar/.codex/config.toml`.
- Why: The user requested parallel agent execution with bounded depth and runtime for this project.
- Alternatives considered: Document the snippet only; set a higher depth for recursive agents.
- Risk: The config is machine-local and not tracked in this repository.
- Rollback plan: Remove the `[agents]` section from `/var/home/Scaar/.codex/config.toml` or adjust the numeric limits.
