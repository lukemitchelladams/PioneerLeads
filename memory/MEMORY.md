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
- **Email monitoring (2026-10-19):** Luke wants to be alerted on every inbound email, not periodic scans.
  Reality: Gmail connector is NOT connected (requires Luke to authorize in claude.ai connector settings).
  Per-email push into a Claude session does not exist. Closest available: once Gmail is connected, create
  a Routine (create_trigger, hourly, connectors ["Gmail"]) that checks the inbox, flags mail from Alex
  Ditto / Rich Carroll / DCSD / Town of Parker / BidNet, and files attachments into the bid folders.
  STATUS: blocked on Gmail authorization. Set up the Routine the moment the connector shows connected.
- Landscaping → Alex Ditto, always.
- Never state a bid requirement that is not quoted from the solicitation document.

## Blockers
- **Gmail not connected.** Blocks: reading the email Luke replied to on 2026-10-19, receiving Alex's DCSD
  bid and Rich Carroll's Parker bid docs by email, and the inbox-monitoring Routine.
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
