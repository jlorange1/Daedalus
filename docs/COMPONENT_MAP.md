# Component Map

## Runtime Surface

- Static frontend: `src/rsps_crewai_team/dashboard_static/index.html`
- Styling: `src/rsps_crewai_team/dashboard_static/styles.css`
- Client controller: `src/rsps_crewai_team/dashboard_static/app.js`
- HTTP server/API: `src/rsps_crewai_team/dashboard.py`

## Shell Regions

| Region | Selector | Purpose | Data Source |
|---|---|---|---|
| Sidebar | `.sidebar` | Navigation, status summary, version | `/api/status` |
| Topbar | `.topbar` | Sprint context and primary commands | static plus POST actions |
| Board | `.board` | Work-order lanes | `status.queue` |
| Agent mesh | `.studio-floor`, `#agentGrid` | Six autonomous department cores | `status.agents` |
| Schedule | `.schedule` | clock, timeline, cron shortcut | client clock plus static schedule |
| Inspector | `.inspector` | selected agent, diff, tests, branch | `status.agents`, `status.git`, `status.readiness` |
| Enqueue dialog | `#enqueueDialog` | create work order | `POST /api/enqueue` |
| Toast | `#toast` | transient feedback | client events/errors |

## Navigation

Current nav buttons are visual only except active styling:

- `.nav-studio`
- `.nav-queue`
- `.nav-builds`
- `.nav-github`
- `.nav-cron`
- `.nav-settings`

Future panel routing should use existing `data-panel` attributes. Do not remove buttons unless replacement views exist.

## Work Board

- Lanes: `inbox`, `running`, `failed`, `done`.
- DOM ids:
  - `#inboxList`, `#runningList`, `#failedList`, `#doneList`
  - `#inboxCount`, `#runningCount`, `#failedCount`, `#doneCount`
- Cards are rendered by `workCard(item, fallbackTag)`.
- Live queue items display newest from API.
- Empty lanes render explicit `.empty-card` operational states through `emptyLane(status)`.
- The old unlabelled visual fallback backlog and unused mock JSON fixtures were removed.

## Agent Floor

- `renderAgents(agents)` builds six `.agent-desk` elements.
- Role order is fixed by the client and inspector, but the visible labels use department names:
  1. Command
  2. Server
  3. Content
  4. QA
  5. Security
  6. Docs
- Agent core types map to the same order:
  1. neural mesh
  2. tesseract field
  3. liquid metal orb
  4. reactor core
  5. shield lattice
  6. archival prism
- The selected agent index is stored in `state.selectedAgent`; clicking a desk updates the inspector.
- Required agent fields: `role`, `name`, `task`, `model`, `status`, `progress`.
- Working state is `agent.status === "working"`.

## Module Windows

- `.module-window` marks movable dashboard sections.
- `wireModuleWindows()` injects `.window-grip` buttons for Work Queue, Agent Mesh, Automation Timeline, and System Telemetry.
- Dragging uses pointer events and inline `transform`; double-clicking a grip resets that module to its original grid position.
- Movement is intentionally local-only for now. Persist positions later with local storage or server profile settings.

## Inspector

- `#agentInspector`: selected agent portrait, status copy, current task, progress, focus, model.
- `#diffSummary`: RSPS git detail or empty-change placeholder.
- `#testList`: readiness checks for Java, Git LFS, OpenClaw, RSPS repo.
- `#branchState`: RSPS branch chip and clean/dirty text.

## Commands

| Control | Selector | Behavior |
|---|---|---|
| Enqueue Work | `#enqueueOpen` | opens dialog |
| Add to Queue | `#enqueueSubmit` | `POST /api/enqueue` with title/body |
| Run Duo | `#runDuo` | `POST /api/action` with `run-duo` |
| Build / Test | `#runBuild` | toast only until a safe execution gate is implemented |
| Push Branch | `#pushBranch` | toast only; pushing remains worker/env controlled |
| Open Cron View | `#cronTick` | `POST /api/action` with `cron-tick` |
| Pause Time | `#pauseTime` | toggles local clock updates |
