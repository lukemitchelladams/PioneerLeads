#!/usr/bin/env bash
# Brown Bison bid scan — runs on Luke's own computer (Mac/Linux) where BidNet, SAM.gov and DIBBS are reachable.
# Pulls the repo, runs every watcher, commits REPORT.md + state + downloaded docs, pushes. Schedule it every 4h.
set -euo pipefail
cd "$(dirname "$0")/.."
if [ -f .env ]; then set -a; . ./.env; set +a; fi
git pull --rebase --quiet origin "$(git rev-parse --abbrev-ref HEAD)" || true
if [ ! -d .venv ]; then python3 -m venv .venv; fi
. .venv/bin/activate
pip install --quiet -r requirements.txt
python -m playwright install chromium >/dev/null 2>&1 || true
python scripts/bidwatch/run.py > /tmp/brownbison-scan.log 2>&1 || true
tail -5 /tmp/brownbison-scan.log
git add bids/_watch/REPORT.md bids/_watch/open_bids.json bids/_watch/health.json bids/_watch/*_state.json memory 2>/dev/null || true
if ! git diff --cached --quiet; then
  git -c user.name="BrownBison Scanner" -c user.email="luke@brownbisonco.com" commit -q -m "scan: $(date -u +%Y-%m-%dT%H:%MZ) $(grep -m1 '^\*\*Headline' bids/_watch/REPORT.md | cut -c1-140)"
  for i in 1 2 3 4; do git push -q origin HEAD && break || sleep $((2**i)); done
fi
