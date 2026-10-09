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
bids/town-of-parker-hvac-on-call/
  README.md                    Bid brief: what we know, what we need, status
  vendor-questions-york.md     Rich @ York (JCI) questions + draft reply
  equipment-schedule.md        Chiller / mechanical equipment inventory (fill from bid docs)
  checklist.md                 Submission checklist
scripts/samgov_search.py       Search SAM.gov opportunities API (needs free API key)
scripts/bid_lookup.md          Where to find Town of Parker bids (BidNet / RMEPS)
docs/cloud-env-setup.md        Network allowlist needed for the cloud session to reach bid portals
.claude/                       SessionStart hook + settings for cloud sessions
```

## Active bids

| Bid | Agency | Portal | Status |
|-----|--------|--------|--------|
| HVAC On-Call Services | Town of Parker, CO | BidNet Direct / Rocky Mountain E-Purchasing | Gathering docs; York Q&A open |

## Quick start (cloud session)

1. Open a cloud session on this repo.
2. Read `memory/MEMORY.md` first. It is the source of truth across sessions.
3. Work inside the bid folder. Keep the bid `README.md` status table current.
4. Before ending a session, append to `memory/MEMORY.md`.

## Network note

Cloud sessions cannot reach `bidnetdirect.com`, `sam.gov`, or `parkerco.gov` until those hosts
are added to the environment's allowed domains. See `docs/cloud-env-setup.md`.
