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
| Studio floor | `.studio-floor`, `#agentGrid` | Six agent workstations | `status.agents` |
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
- Live queue items display newest from API; if a lane is empty, `app.js` uses visual demo backlog cards to keep the board populated.

## Agent Floor

- `renderAgents(agents)` builds six `.agent-desk` elements.
- Role order is fixed by the client and inspector:
  1. producer
  2. backend
  3. content
  4. qa
  5. security
  6. docs
- The selected agent index is stored in `state.selectedAgent`; clicking a desk updates the inspector.
- Required agent fields: `role`, `name`, `task`, `model`, `status`, `progress`.
- Working state is `agent.status === "working"`.

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

