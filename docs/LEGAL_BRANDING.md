# Legal And Branding Notes

## Project Identity

- Product name in the dashboard: `Daedalus Studio`.
- Current sidebar label: `Autonomous GuildOps Studio`.
- Version label: `Sprint Workshop v0.1.0`.
- Keep Daedalus branding visually distinct from RuneScape/Jagex branding. Use original studio/workshop art, not official game UI captures or logos.

## RuneScape / Jagex

- RuneScape and related marks belong to Jagex. Do not use official logos, icons, sprites, screenshots, music, or trade dress as Daedalus assets.
- Use descriptive text such as `RSPS`, `2009scape source`, or `RuneScape private server development` only where needed to describe compatibility or domain.
- Avoid implying endorsement, affiliation, or authorization by Jagex.

## 2009scape Source

- Recommended source: `https://gitlab.com/2009scape/2009scape`.
- Current local target: `/var/home/Scaar/Desktop/game project/2009scape`.
- 2009scape is documented as AGPL-3.0 in `docs/RSPS_SOURCE.md`.
- If modified and run as a network service, AGPL source-sharing obligations can apply. Treat deployment and distribution decisions as legal-sensitive.
- The upstream project states that they do not support people running their own copies; keep Daedalus docs clear that local use is independent.

## Daedalus Assets

- Current dashboard assets are local PNGs under `src/rsps_crewai_team/dashboard_static/assets/`.
- New GUI assets should be original, generated, or properly licensed for project use.
- Keep source sheets or generation notes when practical so assets can be revised consistently.
- Do not import third-party pixel-art packs unless their license allows the intended use and redistribution.

## Third-Party Tools

- CrewAI, OpenRouter, OpenClaw, GitHub CLI, Java, Git LFS, Docker/Podman, and 2009scape each have separate licenses and terms.
- Do not show API keys or provider account identifiers in UI, docs screenshots, logs, or test fixtures.
- If adding public screenshots, scrub paths, branch names, usernames, tokens, and private repo URLs.

## UI Copy Rules

- Safe: `Build / Test`, `Run Duo`, `Enqueue Work`, `GitHub Sync`, `Security Scan`, `Server Source`.
- Avoid: official game branding as a product name, claims of Jagex affiliation, or copy that encourages production deployment without license review.
- Warnings for autonomous actions should state practical risk: repository writes, commits, pushes, and network-service obligations.
