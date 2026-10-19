# Brown Bison — Government Contracting Workspace

Bid tracking, proposal drafting, and vendor Q&A for Brown Bison's public-sector work
(municipal HVAC on-call, chillers, facilities maintenance, and whatever comes next).

This repo is built to be worked from a **Claude Code cloud session**: every bid lives in
`bids/<slug>/`, persistent context lives in `memory/MEMORY.md`, and `CLAUDE.md` tells the
agent how to behave here.

## Layout

```
CLAUDE.md                      Agent operating rules for this repo
memory/MEMORY.md               Persistent project memory (update every session)
bids/_template/                Copy this to start a new bid folder
bids/dcsd-hvac/                PRIORITY: DCSD HVAC bid (doc pending) + competitiveness playbook
bids/town-of-estes-park-2027-hvac-pm/
  README.md                    Full requirements pulled from the 89-page RFP + price-position status
  pricing.md                   Our price + competitor bid tab (fill in)
  docs/                        Extracted RFP text
bids/town-of-parker-hvac-on-call/
  README.md                    Bid brief: what we know, what we need, status
  vendor-questions-york.md     Rich @ York (JCI) questions + draft reply
  equipment-schedule.md        Chiller / mechanical equipment inventory (fill from bid docs)
  checklist.md                 Submission checklist
scripts/scan_bids.py           Run all portal watchers -> bids/_watch/REPORT.md
scripts/bidnet_watch.py        BidNet Direct scraper (6 CO agencies; login optional for docs)
scripts/samgov_watch.py        SAM.gov federal watcher with diffing
scripts/samgov_search.py       One-off SAM.gov search
docs/portal-access.md          What Luke must configure for always-on portal access
scripts/bid_lookup.md          Where to find Town of Parker bids (BidNet / RMEPS)
docs/cloud-env-setup.md        Network allowlist needed for the cloud session to reach bid portals
.claude/                       SessionStart hook + settings for cloud sessions
```

## Active bids

| Bid | Agency | Portal | Status |
|-----|--------|--------|--------|
| HVAC bid (title/number TBD) | Douglas County School District RE-1 | BidNet Direct | **PRIORITY.** Need the document |
| 2027 HVAC Preventive Maintenance and Service | Town of Estes Park, CO | BidNet Direct / email | No bid (missed mandatory pre-bid). Request bid tab as pricing intel |
| HVAC On-Call Services | Town of Parker, CO | BidNet Direct | Unconfirmed; may be conflated with Estes Park |

## Quick start (cloud session)

1. Open a cloud session on this repo.
2. Read `memory/MEMORY.md` first. It is the source of truth across sessions.
3. Work inside the bid folder. Keep the bid `README.md` status table current.
4. Before ending a session, append to `memory/MEMORY.md`.

## Network note

Cloud sessions cannot reach `bidnetdirect.com`, `sam.gov`, or `parkerco.gov` until those hosts
are added to the environment's allowed domains. See `docs/cloud-env-setup.md`.
