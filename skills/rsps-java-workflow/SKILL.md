---
name: rsps-java-workflow
description: Use when working on Daedalus RSPS Java/Kotlin/Maven code based on the configured 2009scape source, including setup, build, test, and UI branding constraints.
---

# RSPS Java Workflow

Use this skill for Daedalus work that touches the configured 2009scape-derived Java/Kotlin/Maven source.

## Ground Rules

- Require JDK 11. Check `java -version` before diagnosing Maven failures.
- Use the Maven server POM for server builds; do not assume the repository root POM is the correct build target.
- Run `git lfs pull` before builds when assets, cache data, or binary resources may be missing.
- Run `mvn clean` before each build to avoid stale generated classes or resources.
- Keep Daedalus UI free of protected 2009scape branding, logos, and trade dress unless the user explicitly confirms they have rights to use it.

## Safe Commands

From the configured 2009scape server source directory:

```bash
git lfs pull
mvn -f server/pom.xml clean
mvn -f server/pom.xml test
mvn -f server/pom.xml package
```

If the server POM lives at a different local path, locate it first with `rg --files -g 'pom.xml'` and use that path with `mvn -f`.

## Workflow

1. Confirm the relevant source directory and server POM path before editing.
2. Prefer existing Java/Kotlin package structure, Maven plugins, and test patterns.
3. For build issues, check JDK version, LFS state, and clean build output before changing code.
4. Use focused Maven commands for verification; avoid broad install/deploy goals unless the user asks.
5. When editing Daedalus-facing UI text or assets, replace protected source branding with Daedalus-neutral naming.
