#!/usr/bin/env python3
"""Back-compat entry point: runs the full bid watcher once (scripts/bidwatch/run.py).

  python3 scripts/scan_bids.py            # one full scan of every source, writes bids/_watch/REPORT.md
  python3 scripts/scan_bids.py --loop     # keep scanning every 60 minutes, re-login as needed
"""
import runpy
import sys
from pathlib import Path

sys.argv[0] = str(Path(__file__).resolve().parent / "bidwatch" / "run.py")
runpy.run_path(sys.argv[0], run_name="__main__")
