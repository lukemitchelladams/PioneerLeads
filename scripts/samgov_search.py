#!/usr/bin/env python3
"""Search SAM.gov contract opportunities (federal only).

Usage:
  export SAM_API_KEY=...        # free key from https://sam.gov (Account Details -> API Key)
  python3 scripts/samgov_search.py --keyword "HVAC on-call" --state CO --days 60
  python3 scripts/samgov_search.py --naics 238220 --state CO

Prints notice title, solicitation number, agency, posted/response dates, and the link.
Uses the public Opportunities API v2. Needs outbound access to api.sam.gov (blocked in the
cloud session until allowlisted; runs fine on a laptop).
"""
import argparse
import datetime as dt
import json
import os
import sys
import urllib.parse
import urllib.request

API = "https://api.sam.gov/opportunities/v2/search"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--keyword", default="HVAC")
    p.add_argument("--naics", help="e.g. 238220 (plumbing/HVAC contractors)")
    p.add_argument("--state", help="place-of-performance state, e.g. CO")
    p.add_argument("--days", type=int, default=90, help="posted within last N days")
    p.add_argument("--limit", type=int, default=50)
    a = p.parse_args()

    key = os.environ.get("SAM_API_KEY")
    if not key:
        print("SAM_API_KEY not set. Get a free key at https://sam.gov (Account Details -> API Key).",
              file=sys.stderr)
        return 2

    today = dt.date.today()
    start = today - dt.timedelta(days=a.days)
    q = {
        "api_key": key,
        "postedFrom": start.strftime("%m/%d/%Y"),
        "postedTo": today.strftime("%m/%d/%Y"),
        "limit": a.limit,
        "ptype": "o,k,p",  # solicitation, combined synopsis, presolicitation
        "title": a.keyword,
    }
    if a.naics:
        q["ncode"] = a.naics
    if a.state:
        q["state"] = a.state

    url = f"{API}?{urllib.parse.urlencode(q)}"
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            data = json.load(r)
    except Exception as e:  # noqa: BLE001
        print(f"request failed: {e}", file=sys.stderr)
        return 1

    rows = data.get("opportunitiesData", [])
    print(f"{len(rows)} result(s) of {data.get('totalRecords', '?')}\n")
    for o in rows:
        print(f"- {o.get('title')}")
        print(f"  sol#: {o.get('solicitationNumber')}  agency: {o.get('fullParentPathName')}")
        print(f"  posted: {o.get('postedDate')}  due: {o.get('responseDeadLine')}  type: {o.get('type')}")
        print(f"  {o.get('uiLink')}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
