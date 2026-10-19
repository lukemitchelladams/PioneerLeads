# CLAUDE.md — Brown Bison

## What this repo is
Brown Bison's government-contracting workspace. Bids, proposals, vendor Q&A, and project memory.
It also hunts bids for Luke's dad's industrial bearings/conveyor/paper-mill business (profile
`dads-company` in bids/_watch/watch_profiles.json). Every scan covers both companies.
It is NOT a software product. Do not scaffold apps here unless asked.

## Operating rules (non-negotiable)
0. FIRST thing on any new bid: find the pre-bid meeting / site walk date and whether attendance is
   MANDATORY. Put it in the README status table and bids/_pipeline.md. If mandatory and <72h away or past,
   tell Luke in the first line of your reply. Missing a mandatory walk kills the bid (Estes Park, Lafayette,
   Arapahoe fire alarm, DOC fire protection all died this way).
0b. Sub outreach starts the day a bid goes GO, not 72 hours out (Luke, 2026-10-19). Subs need at least a
   week's notice before a site walk or our pricing deadline. Same day a bid is opened: find 5-8 local subs
   with public emails, write bids/<bid>/sub-outreach.md with the pricing-request email, and put it in front
   of Luke that day. Ask subs for answers 7+ days before our submission. If a mandatory walk is under 7
   days out, Luke attends for Brown Bison and subs price from our photos and notes. Every hourly check
   lists GO bids with no sub pricing in hand and the days remaining.
1. Correct misconceptions. If the user is wrong about a bid detail, say so with the source.
2. Never state a bid requirement (response time, due date, insurance limit, equipment model)
   unless it is quoted from the actual solicitation document. If we don't have the document,
   say "not in hand yet" and list how to get it.
3. Verify before claiming done. If a fetch failed or a host was blocked, report it as blocked.
4. Read `memory/MEMORY.md` at the start of every session. Append to it before ending.
5. One folder per bid under `bids/<agency>-<short-title>/`. Start from `bids/_template/`.
6. Keep the status table in each bid `README.md` current.
7. Dates: write ISO (2026-10-09). Money: write with units.
8. No excavation, earthwork, or heavy-civil bids (ponds, pump stations, roadwork, drainage). Our trades are
   HVAC, plumbing, electrical, facilities maintenance, landscaping/grounds/snow, janitorial. Keep it simple
   (Luke, 2026-10-19).
9. Supply/commodity bids: do not rank as GO unless the document states quantities or annual spend. Small-margin
   product supply (filters, parts) is not worth Brown Bison's time unless volume is proven (Luke, 2026-10-19).

## Standing rules from Luke
- **Never write or say "or if you already have a contract with the city" or any variant** (existing contract,
  already under contract, current provider) in any outreach, proposal, or vendor message. It invites the
  reader to tell us no and signals we expect to lose. We write as the bidder who will win. (Luke, 2026-10-19.)
- **BROWN BISON IS ALWAYS THE BIDDER.** Every bid, every trade. Subcontractors (Alex Ditto for landscaping,
  Jones Bearing for equipment, any HVAC/plumbing/electrical sub) give us their pricing; we add our markup
  and fees, we submit, we hold the contract, we manage the sub. NEVER describe a bid as "for" a sub, never
  suggest a sub bid directly, never offer a "sub primes" option. (Luke, 2026-10-19, emphatic.)
- All landscaping work is performed by Alex Ditto as OUR sub. Luke handles all communication with Alex;
  the agent only surfaces Alex's emails and flags landscaping bids worth getting his pricing on.
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
- Brown Bison Holdings LLC: UEI EV9QPAPM4C47, CAGE 20VU2, SAM active to 2027-05-21, NAICS 238220.
- GovTribe connector = bid search for BidNet/RMEPS + SAM.gov. Use it first, every session. State/local CO
  search covers Parker, DCSD, Estes Park, Douglas County and the whole Front Range.
- Town of Parker, CO posts solicitations on BidNet Direct (Rocky Mountain E-Purchasing System).
  Procurement: 303-805-3188. Bid docs usually require vendor login to download.
- Town of Parker is a Town, not a City. Use "Town of Parker" on all submittals.
