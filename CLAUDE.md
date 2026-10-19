# CLAUDE.md — Brown Bison

## What this repo is
Brown Bison's government-contracting workspace. Bids, proposals, vendor Q&A, and project memory.
It also hunts bids for Luke's dad's industrial bearings/conveyor/paper-mill business (profile
`dads-company` in bids/_watch/watch_profiles.json). Every scan covers both companies.
It is NOT a software product. Do not scaffold apps here unless asked.

## Operating rules (non-negotiable)
1. Correct misconceptions. If the user is wrong about a bid detail, say so with the source.
2. Never state a bid requirement (response time, due date, insurance limit, equipment model)
   unless it is quoted from the actual solicitation document. If we don't have the document,
   say "not in hand yet" and list how to get it.
3. Verify before claiming done. If a fetch failed or a host was blocked, report it as blocked.
4. Read `memory/MEMORY.md` at the start of every session. Append to it before ending.
5. One folder per bid under `bids/<agency>-<short-title>/`. Start from `bids/_template/`.
6. Keep the status table in each bid `README.md` current.
7. Dates: write ISO (2026-10-09). Money: write with units.

## Standing rules from Luke
- All landscaping work goes through Alex Ditto. No exceptions, no need for his phone number on file.
- All business email goes out from luke@brownbisonco.com. Never use lukemitchelladams@gmail.com for business.
- Inbox monitoring runs hourly via Routine into the main session; Gmail is read-only for the agent. Never
  send/reply/forward/trash/label email without Luke's explicit instruction in the moment.

## Portal access
- Bid-portal scanning = `python3 scripts/scan_bids.py` (BidNet scraper + SAM.gov API). Needs allowed
  domains + SAM_API_KEY/BIDNET_USER/BIDNET_PASS env vars. See docs/portal-access.md. Credentials come
  from the environment only; never ask Luke to paste them in chat, never write them to the repo.

## Known blocked hosts in cloud sessions
bidnetdirect.com, rockymountainbidsystem.com, sam.gov, api.sam.gov, parkerco.gov.
Ask the user to add them under Network access → Allowed domains (see docs/cloud-env-setup.md),
or ask the user to download the solicitation PDFs and drop them in the bid folder under `docs/`.

## Key facts (see memory/MEMORY.md for detail)
- Town of Parker, CO posts solicitations on BidNet Direct (Rocky Mountain E-Purchasing System).
  Procurement: 303-805-3188. Bid docs usually require vendor login to download.
- Town of Parker is a Town, not a City. Use "Town of Parker" on all submittals.
