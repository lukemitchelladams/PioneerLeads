# Brown Bison — Project Memory

Append-only log plus a maintained "Current state" section. Read this first every session.

## Current state (updated 2026-10-15)

**Company:** Brown Bison — government contracting (HVAC / mechanical on-call, municipal facilities).
Owner/contact: Luke Mitchell Adams (lukemitchelladams@gmail.com).

**Active pursuits (priority order per Luke, 2026-10-15):**
1. **DCSD (Douglas County School District RE-1) HVAC bid.** Luke: "do everything we can to be as competitive
   as possible." Document NOT yet located (not in Drive; Gmail not connected). See bids/dcsd-hvac/.
2. **Town of Estes Park — 2027 HVAC Preventive Maintenance and Service RFP.** This is the RFP that was
   shared to Luke's Drive on 2026-09-18 ("RFP COMPLETE - HVAC Service.pdf"). 19 facilities, lump sum PM +
   hourly after-hours rates, mandatory pre-bid 2026-09-08, due 2026-09-24 11:00 MT (passed), Town Board
   award ~2026-11-10. Contact Robert Schumaker 970-577-3576 rschumaker@estes.org. Whether Brown Bison
   attended/submitted and at what price is UNKNOWN. See bids/town-of-estes-park-2027-hvac-pm/.
3. **Town of Parker, Colorado — HVAC On-Call Services.** Original pursuit from 2026-10-09. No document
   in hand. NOTE: on 2026-10-15 the only bid PDF found was Estes Park, not Parker. Luke may have conflated
   the two, or Parker is a separate bid still on BidNet. Confirm with Luke.

**Relationships / vendors:**
- **Alex Ditto** — sent "the bid and info" (per Luke 2026-10-15; Gmail not connected so the email is
  unread here). **DECISION (Luke, 2026-10-15): route ALL landscaping jobs to Alex Ditto** because of the
  relationship built. Contact info: not yet captured.
- **Rich @ York (JCI)** — chiller parts/support. Open questions on model numbers and response time (see below).

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

## Blockers
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

### 2026-10-15 — Session 2 (cloud)
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
