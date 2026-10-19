#!/usr/bin/env python3
"""Run every bid-portal watcher and write bids/_watch/REPORT.md.

Usage: python3 scripts/scan_bids.py            # all sources
       python3 scripts/scan_bids.py --no-bidnet # skip Playwright
Exit code 0 always; the report carries the errors so a Routine can relay them.
"""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import samgov_watch  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
REPORT = REPO / "bids" / "_watch" / "REPORT.md"


def main() -> int:
    parts = [f"# Bid watch report — {dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')}\n"]
    headline = []

    if "--no-bidnet" not in sys.argv:
        try:
            import bidnet_watch
            r = bidnet_watch.run()
            parts.append(bidnet_watch.render(r))
            if r["new"]:
                headline.append(f"BidNet: {len(r['new'])} new ({sum(1 for v in r['new'].values() if v['match'])} keyword matches)")
            if r["errors"]:
                headline.append(f"BidNet: {len(r['errors'])} error(s)")
        except Exception as e:  # noqa: BLE001
            parts.append(f"## BidNet Direct\n**Failed to run:** {type(e).__name__}: {e}")
            headline.append("BidNet: failed to run")

    r = samgov_watch.run()
    parts.append(samgov_watch.render(r))
    if r.get("error"):
        headline.append(f"SAM.gov: {r['error']}")
    elif r["new"]:
        headline.append(f"SAM.gov: {len(r['new'])} new")

    parts.insert(1, "**Headline:** " + ("; ".join(headline) if headline else "no changes") + "\n")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n\n".join(parts) + "\n")
    print("\n\n".join(parts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
