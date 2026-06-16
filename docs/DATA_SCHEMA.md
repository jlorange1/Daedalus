# Dashboard Data Schema

## Endpoints

Base server: `uv run rsps-dashboard`, default `http://127.0.0.1:8765`.

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/status` | Full dashboard state |
| `POST` | `/api/enqueue` | Create an inbox work order |
| `POST` | `/api/action` | Spawn an allowed worker/cron action |

## `GET /api/status`

Response shape:

```json
{
  "project": {
    "name": "Daedalus Studio",
    "root": "/absolute/path/to/Daedalus",
    "server_source": "/absolute/path/to/open-source-server",
    "source": "configured_server_source"
  },
  "env": {
    "autonomy": false,
    "duo_mode": true,
    "push_after_work": false,
    "ponytail": "full",
    "coding_cli": "openclaw",
    "build_command": "cd Server && ./mvnw clean package -DskipTests",
    "test_command": "cd Server && ./mvnw test"
  },
  "readiness": {
    "java": true,
    "git_lfs": true,
    "openclaw": true,
    "server_source": true
  },
  "queue": {
    "inbox": { "count": 0, "items": [] },
    "running": { "count": 0, "items": [] },
    "done": { "count": 0, "items": [] },
    "failed": { "count": 0, "items": [] }
  },
  "agents": [],
  "git": {
    "daedalus": {},
    "rsps": {}
  },
  "logs": []
}
```

## Queue Item

```json
{
  "title": "Add starter studio readiness task",
  "file": "20260616T000000Z-add-starter-studio-readiness-task.md",
  "updated": 1781568000
}
```

- Queue files live under `work_orders/{inbox|running|done|failed}`.
- `title` comes from the first Markdown `# ` heading; fallback is file stem.
- API returns the last eight files per status, sorted by filename.

## Agent Item

```json
{
  "role": "Backend Developer",
  "name": "Borin",
  "task": "coding server systems",
  "model": "qwen/qwen3-coder:free",
  "status": "working",
  "progress": 59
}
```

- `status` is currently `ready` or `working`.
- `progress` is an integer percentage. Clamp client renderers to `0..100`.
- The frontend assumes exactly six agents in this order: Producer, Backend Developer, Content Developer, QA Tester, Security Reviewer, Documentation Writer.

## Git Summary

```json
{
  "available": true,
  "branch": "main",
  "clean": true,
  "detail": "clean",
  "remote": "git@github.com:owner/repo.git"
}
```

Missing repo fallback:

```json
{
  "available": false,
  "branch": "missing",
  "clean": false,
  "detail": "/missing/path"
}
```

## Logs

```json
{
  "name": "dashboard-actions.log",
  "tail": "last 900 chars of log file"
}
```

- Server returns up to six recent files from `logs/`.
- Never expose secrets or full `.env` contents in log tails.

## `POST /api/enqueue`

Request:

```json
{
  "title": "Work order title",
  "body": "Markdown body with implementation details"
}
```

Success `201`:

```json
{
  "ok": true,
  "path": "/absolute/path/to/work_orders/inbox/20260616T000000Z-work-order-title.md"
}
```

Validation error `400`:

```json
{
  "ok": false,
  "error": "title and body are required"
}
```

## `POST /api/action`

Request:

```json
{ "action": "run-duo" }
```

Allowed actions:

- `run-duo`
- `run-once`
- `cron-tick`
- `render-cron`

Success `200`:

```json
{
  "ok": true,
  "pid": 12345,
  "log": "/absolute/path/to/logs/dashboard-actions.log"
}
```

Unknown action `400`:

```json
{
  "ok": false,
  "error": "unknown action"
}
```
