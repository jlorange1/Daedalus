# RSPS Source: 2009scape

Recommended source tree:

```text
/var/home/Scaar/Desktop/game project/2009scape
```

Upstream:

```text
https://gitlab.com/2009scape/2009scape
```

## Why This Source

2009scape is the best fit for Daedalus right now because it is a real playable open-source MMORPG emulation server, not just a small framework or abandoned base. It has an active upstream, Java/Kotlin server code, content data, database exports, Docker support, and a normal build/test surface for agents to inspect and improve.

## License And Caveats

- License: AGPL-3.0. If you modify and run it as a network service, source-sharing obligations can apply.
- The upstream project states that they do not support people running their own copies.
- Setup expects JDK 11.
- The repo uses Git LFS; run `git lfs pull` after installing Git LFS.
- Docker mode needs `mysql.env`, `config/default.conf`, and a working Docker or Podman Compose environment.

## Daedalus Settings

Local `.env` is configured with:

```text
RSPS_REPO_PATH=/var/home/Scaar/Desktop/game project/2009scape
RSPS_BUILD_COMMAND=cd Server && ./mvnw clean package -DskipTests
RSPS_TEST_COMMAND=cd Server && ./mvnw test
RSPS_ALLOW_AUTONOMOUS=false
```

Keep `RSPS_ALLOW_AUTONOMOUS=false` until Java 11 and Git LFS are installed and the first build/test pass has been verified manually.

## Other Candidates Considered

- `apollo-rsps/apollo`: cleaner ISC license and good framework shape, but older and less complete as a playable RSPS.
- `openrs2/openrs2`: strong preservation/tooling project, but not the quickest route to a directly playable private server.
- `RSPSApp/elvarg-rsps`: familiar RSPS base style, but licensing/maintenance is weaker, so it is a poorer default for long-term agent work.
