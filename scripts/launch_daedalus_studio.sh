#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="/var/home/Scaar/Desktop/game project/Daedalus"
LOG_DIR="$PROJECT_ROOT/logs"
PID_FILE="$LOG_DIR/dashboard.pid"
URL="http://127.0.0.1:8765"

mkdir -p "$LOG_DIR"
cd "$PROJECT_ROOT"

server_running=false
if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  pid="$(cat "$PID_FILE")"
  if [[ -r "/proc/$pid/cmdline" ]] && tr '\0' ' ' < "/proc/$pid/cmdline" | grep -q "rsps_crewai_team.dashboard"; then
    server_running=true
  fi
fi

if [[ "$server_running" == "true" ]]; then
  :
else
  nohup env PYTHONPATH=src python3 -m rsps_crewai_team.dashboard --host 127.0.0.1 --port 8765 \
    >> "$LOG_DIR/launcher-dashboard.log" 2>&1 &
  echo "$!" > "$PID_FILE"
fi

sleep 1
xdg-open "$URL" >/dev/null 2>&1 || true

echo "Daedalus Studio launched at $URL"
