#!/usr/bin/env bash
# Reads systemd credentials into the environment (never echoed), then runs one scan that pushes its results.
# Exit 0 = all sources fresh, 3 = degraded (a source blind or carried forward), 2 = nothing scanned, 4 = overlap.
set -euo pipefail
for n in BIDNET_USER BIDNET_PASS SAM_API_KEY BIDNET_CODE_IMAP_PASS; do
  if [ -n "${CREDENTIALS_DIRECTORY:-}" ] && [ -s "$CREDENTIALS_DIRECTORY/$n" ]; then
    export "$n=$(cat "$CREDENTIALS_DIRECTORY/$n")"
  fi
done
cd /opt/bidwatch/repo
exec python3 scripts/bidwatch/run.py --push
