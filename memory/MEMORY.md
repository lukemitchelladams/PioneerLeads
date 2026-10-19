# Brown Bison — Project Memory

Append-only log plus a maintained "Current state" section. Read this first every session.

## Current state (updated 2026-10-19)

**Company:** Brown Bison — government contracting (HVAC / mechanical on-call, municipal facilities).
Owner/contact: Luke Mitchell Adams (lukemitchelladams@gmail.com).

**Active pursuits (priority order per Luke, 2026-10-15):**
1. **DCSD (Douglas County School District RE-1) HVAC bid.** Luke: "do everything we can to be as competitive
   as possible." Document NOT yet located (not in Drive; Gmail not connected). See bids/dcsd-hvac/.
2. **Town of Estes Park — 2027 HVAC Preventive Maintenance and Service RFP.** This is the RFP that was
   shared to Luke's Drive on 2026-09-18 ("RFP COMPLETE - HVAC Service.pdf"). 19 facilities, lump sum PM +
   hourly after-hours rates, mandatory pre-bid 2026-09-08, due 2026-09-24 11:00 MT (passed), Town Board
   award ~2026-11-10. Contact Robert Schumaker 970-577-3576 rschumaker@estes.org. **NO BID: Brown Bison did
   not attend the mandatory pre-bid (Luke, 2026-10-15). Not eligible. Use its bid tab as pricing intel.** See bids/town-of-estes-park-2027-hvac-pm/.
3. **Town of Parker, Colorado — HVAC On-Call Services.** CONFIRMED real and separate from Estes Park
   (Luke, 2026-10-19). **Waiting on Rich Carroll, who told Luke he will send the bid docs Monday
   2026-10-20.** No document in hand yet. When it lands, answer the chiller model / response-time
   questions from it (see vendor-questions-york.md).

**Relationships / vendors:**
- **Alex Ditto** — per Luke (relayed from his portfolio-orchestrator session, 2026-10-18): Luke has spoken
  with Alex and **Alex is sending the DCSD HVAC bid on Monday 2026-10-20.** Gmail is no longer the blocker;
  the document simply has not been sent yet. When it lands in bids/dcsd-hvac/docs/ (or Luke pastes it),
  build the full requirements matrix + pricing model. Do not email anyone or touch any portal. **DECISION (Luke, 2026-10-15): route ALL landscaping jobs to Alex Ditto** because of the
  relationship built. Contact info: not yet captured.
- **Rich Carroll** — sending the Town of Parker on-call bid docs Monday 2026-10-20 (Luke, 2026-10-19).
  Likely the same "Rich from York" who called 2026-10-09 about chillers; not confirmed. If same person,
  he is both the York (JCI) vendor contact AND the source of the bid docs.
- **Alex Ditto** — landscaping. **Luke (2026-10-19): phone number NOT needed. All future landscaping
  contracts go through Alex because Luke likes him.** Alex is also sending the DCSD HVAC bid Mon 2026-10-20.

**Town of Parker detail (from 2026-10-09):**
- Portal: BidNet Direct / Rocky Mountain E-Purchasing System (RMEPS).
  Agency page: https://www.bidnetdirect.com/colorado/town-of-parker
  Town procurement page: https://www.parkerco.gov/262/Procurement
  Town "Current Projects Out For Bid": https://www.parkerco.gov/207/Current-Projects-Out-For-Bid
- Town procurement phone: 303-805-3188. RMEPS vendor support: 800-835-4603.
- Award method (per Town's "How to do Business" guide): a Request for Bid goes to the lowest
  responsive, responsible bidder; an RFP is scored by an evaluation committee.
- Solicitation number, due date, Q&A deadline, response-time requirement, and equipment list:
  **NOT IN HAND YET** (cloud session cannot reach the portals — see Blockers).

**Vendor contact:** Rich @ York (York is a Johnson Controls brand). Called 2026-10-09 asking:
  1. More information on the chillers in the bid, including model numbers.
  2. Whether the bid specifies a required response time for on-call service.
  Status: open. Answers must come from the solicitation documents. See
  bids/town-of-parker-hvac-on-call/vendor-questions-york.md.

**Town of Parker facilities likely in scope (from public sources, unconfirmed against bid):**
- Town Hall — 20120 E. Mainstreet, Parker, CO 80138
- Parker Recreation Center — 17301 E. Lincoln Ave (indoor pool; a 30-ton Innovent pool
  dehumidification RTU was replaced by Holbrook Service, so some mechanical is recent)
- Parker Fieldhouse — 18700 E. Plaza Dr (~100,000 sq ft)
- PACE Center (Parker Arts, Culture & Events) — 20000 Pikes Peak Ave (~50,000 sq ft, ~$16M build)
- Also plausible: Police HQ, Public Works shops, H2O'Brien pool, libraries (Douglas County, not Town).
  Chiller make/model/tonnage per building: unknown until the bid's equipment schedule is read.

## Standing instructions from Luke
- **Business email = luke@brownbisonco.com (Luke, 2026-10-19).** All business communications go through
  the Brown Bison Workspace mailbox from now on. Historical vendor mail is on lukemitchelladams@gmail.com,
  which is NOT connected; Luke suggested Chrome/computer-use connectors to read it (not available in this
  cloud session). Simplest fix: forward/import that Gmail into brownbisonco (see docs/inbox-monitor-routine.md).
- **Email monitoring (2026-10-19):** Gmail connector IS connected (luke@brownbisonco.com). Hourly Routine
  "Brown Bison inbox check" fires into this session 06:00–20:00 MT. A fresh-session Routine
  (trig_01AA1wwU52PmYHxm1UWHBozq) was created then DISABLED because this org cannot pass connectors to
  Routines, so its sessions have no Gmail. Per-email push does not exist; hourly is the floor. See
  docs/inbox-monitor-routine.md for limits and the prompt.
- **Signature feedback (Luke's reply 2026-10-19 on "Sender test 2"):** signature text renders pink; location
  should say Denver, CO, not Broomfield, CO; everything else looks good. Whoever owns the brownbisonco
  sending setup (another session) needs to fix those two things.
- Landscaping → Alex Ditto, always.
- Never state a bid requirement that is not quoted from the solicitation document.

- **Always-on portal access (Luke, 2026-10-19):** wants 24/7 login to SAM.gov + BidNet, scans for new bids,
  addenda tracking, docs for subs. Reality: SAM.gov has an API (federal only; never had access, host blocked,
  no key). BidNet has NO API/MCP. Built scripts/bidnet_watch.py (Playwright scraper), samgov_watch.py,
  scan_bids.py. Blocked on Luke: allow domains, set SAM_API_KEY/BIDNET_USER/BIDNET_PASS, register
  brownbisonco email on BidNet with notifications. GovTribe MCP exists for federal. See docs/portal-access.md.
  Create the scan Routine only after the hosts are allowed.

- **BidNet account (2026-10-19):** login email is lukeadams55@icloud.com. Luke pasted the password in chat;
  it is NOT stored here and must be rotated. Credentials belong in the cloud environment's Environment
  variables as BIDNET_USER / BIDNET_PASS, nowhere else. BidNet notifications currently go to the iCloud
  address, which no monitor sees: change the BidNet vendor contact email to luke@brownbisonco.com.

## Blockers
- **lukemitchelladams@gmail.com not connected.** Past vendor threads (Alex Ditto, Rich Carroll) are there.
  If Alex/Rich send Monday's bid docs to that address, the monitor will not see them unless Luke forwards
  that mailbox into brownbisonco or saves the files to Drive/repo.
- Cloud session network policy denies: bidnetdirect.com, rockymountainbidsystem.com, sam.gov,
  api.sam.gov, parkerco.gov. Fix: environment settings → Network access → add those hosts to
  Allowed domains. Until then, download the solicitation PDFs locally and commit them under
  bids/town-of-parker-hvac-on-call/docs/.
- GitHub token in cloud sessions is repo-scoped; cannot create new repos. This repo
  (originally "PioneerLeads", which was empty) is being repurposed as the BrownBison repo.
- No prior Brown Bison memory exists in this cloud environment, Google Drive, or HubSpot.
  Prior notes are on the user's other computer. HubSpot has a bare "Town of Parker" company
  record (id 17231012766, CO) with no contacts or notes attached.

## Log

### 2026-10-19 — Session 3 (cloud, check-in)
- Luke: 5+ new bids in work by Mon AM, due 7+ days out; find walkthrough people; hands-off portal access.
  Probed 39 CO procurement/aggregator hosts: ALL blocked. Web index yielded 3 live leads beyond Parker/DCSD
  (Boulder County BID-313-26 air filters due 10/29; Colorado Springs R26-032MZ + R26-034MZ landscaping).
  Wrote bids/_pipeline.md, team/walkthrough-roster.md, and the 10-minute setup at top of docs/portal-access.md.
- Built bid-portal watchers (BidNet scraper validated on fixture only; SAM.gov watcher). Live run blocked
  by network policy. Wrote docs/portal-access.md with Luke's to-do list.
- Gmail connected (luke@brownbisonco.com only; 6 test emails, nothing from vendors). Created hourly
  inbox-check Routine into this session; disabled the fresh-session variant (no Gmail there).
  Logged Luke's signature feedback (pink text, Denver not Broomfield).
- Luke: wants push-style email alerts; corrected him that Gmail is not connected at all and that true push
  is unavailable (hourly Routine is the closest). Alex Ditto phone not needed; landscaping goes through Alex.
  Town of Parker on-call bid is real; Rich Carroll sends docs Mon 2026-10-20.
- Cross-session message from Luke's orchestrator session: Alex Ditto sends the DCSD bid Mon 2026-10-20.
  Checked repo and Drive: nothing new yet. No outward action taken.

### 2026-10-15 — Session 2 (cloud)
- Luke confirmed we did NOT attend the Estes Park mandatory pre-bid → no bid, folder kept for intel/rebid.
- Luke asked for "the bid and info Alex Ditto sent" + price-position analysis. Gmail plugin not authorized;
  Gmail connector exists but is not connected. Searched Drive, HubSpot, web.
- Found "RFP COMPLETE - HVAC Service.pdf" in Drive: Town of **Estes Park** 2027 HVAC PM RFP (not Parker).
  Read all 89 pages. Attachment A (scope/19-facility list) is NOT in the PDF. No Brown Bison pricing anywhere.
  Price position: cannot be determined until our number + bid tab + Attachment A are in hand.
- Luke (mid-session): DCSD bid is the priority; go to Alex Ditto for all landscaping. No DCSD doc found
  anywhere reachable. Built bids/dcsd-hvac/ with a competitiveness playbook pending the document.
- Blocked hosts this session (in addition to earlier list): estes.org, estespark.colorado.gov,
  dms.estes.org, dcsdk12.org.

### 2026-10-09 — Session 1 (cloud)
- Searched local memory, Google Drive, HubSpot, and the web for Brown Bison + Parker HVAC bid.
  Nothing on Brown Bison anywhere reachable. HubSpot "York"/"Johnson Controls" contacts are all
  IT-vertical prospects, not Rich from York HVAC.
- Confirmed Town of Parker posts on BidNet Direct (RMEPS); details are login-gated.
- Could not fetch the solicitation: all bid portals blocked by network policy.
- Built this workspace: bid folder, York Q&A draft, equipment schedule template, SAM.gov
  search script, cloud-session hook.
