#!/usr/bin/env bash
# Launch one detached, logged-in bidwatch scan (run.py --push) in the background and return at once.
# Usage: bash scripts/bidwatch/launch_scan.sh <log file> [extra seconds to wait before starting]
# - refuses to start a second scan while one runs
# - clears a stale confirmation-code marker so the login is attempted while the operator watches the inbox
# - honours a BidNet cool-down of up to 15 minutes by sleeping until it lifts
# - writes "EXIT <code>" as the log's last line and (re)starts the session keepalive
# Credentials come from ~/.brownbison/env only; nothing is printed.
set -u
LOG="${1:?log file}"
EXTRA="${2:-0}"
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
STATE="${BROWNBISON_STATE:-$HOME/.brownbison}"
if pgrep -f 'bidwatch/run.py --push' >/dev/null 2>&1; then
  echo "scan already running; not launching"
  exit 0
fi
rm -f "$LOG" "$STATE/bidnet_code_needed"
WAIT="$EXTRA"
if [ -f "$STATE/bidnet_cooldown_until" ]; then
  T=$(date -d "$(cat "$STATE/bidnet_cooldown_until")" +%s 2>/dev/null || echo 0)
  D=$(( T - $(date +%s) + 20 ))
  if [ "$D" -gt 0 ] && [ "$D" -le 900 ] && [ "$D" -gt "$WAIT" ]; then WAIT="$D"; fi
fi
setsid nohup bash -c "sleep $WAIT; cd '$REPO' && BIDWATCH_BIDNET_LOGIN_GAP_H=\${BIDWATCH_BIDNET_LOGIN_GAP_H:-0.9} BIDNET_CODE_WAIT=\${BIDNET_CODE_WAIT:-420} timeout 1500 python3 scripts/bidwatch/run.py --push > '$LOG' 2>&1; echo EXIT \$? >> '$LOG'" >/dev/null 2>&1 &
sleep 2
python3 "$REPO/scripts/bidwatch/keepalive.py" --ensure 2>&1 | tail -1
echo "scan launched $(date -u +%H:%M:%SZ), wait ${WAIT}s, log $LOG"
