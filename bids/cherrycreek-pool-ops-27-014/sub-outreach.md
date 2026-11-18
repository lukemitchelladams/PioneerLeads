# CCSD RFP 27-014 District Pool Operations: sub outreach

**Subject (gate PASS 2026-11-18):** Pricing request: Cherry Creek Schools pool operations and maintenance, RFP 27-014

Brown Bison proposes and holds the contract; a commercial pool service company with CPO-certified techs is our sub and
does the field work at six high school pools. Proposal due **2026-12-18 14:00 MST** on BidNet EBS. Site visit
**2026-12-03 09:00 MST, optional** ("Not mandatory but recommended", RFP p.5), starting at Overland High School Pool,
12400 E Jewell Ave, Aurora. Ask: weekly price per pool, Additional Pricing rates and cleaning frequencies on the
District's workbook by **Wed 2026-12-09** (9 days before submission; rule 0b wants 7+), and an attendee name for the site
visit by **Tue 2026-12-01**. Only a sub's person attends, confirmed in writing and signing in for Brown Bison; never Luke.

Rules from the RFP that shape this outreach:
- Subs need "the prior written consent of CCSD" (MSA 2.7, p.12): name the sub in the proposal, with its resources shown
  separately (Sec 5.4, p.31).
- The sub's people carry the scoring: three references "of similar size and scope" (Sec 5.2, p.31), "Current Certified
  Pool Operator (CPO) certification" (Exh A 4, p.37). Second ask once a firm says yes: 3 school/HOA/commercial pool
  references, CPO cards for the techs, a 1-page resume for the account manager and alternate, its route plan for 18
  visits a day, and its COI (MSA 15.0 makes Brown Bison responsible for "similar Insurance" from subs).
- Capacity is the filter: "three separate onsite water-testing visits per day at each pool", seven days a week (Exh A 3,
  p.33). A firm without weekend routes and substitutes cannot carry this; ask about it in the second email.
- The District supplies the chemicals (Exh A 5, p.38); the sub prices labor, test reagents, transport and supervision.
- The RFP does not say whether a firm that proposes as prime may also sub for another proposer (not stated). Ask each
  firm that replies whether it plans to propose on its own; a firm that does is a competitor.

## Firms (first touch: business email printed on the firm's own website, page loaded 2026-11-18)

Mailboxes are kept out of this file: scratchpad pool/subs.json (session scratch) holds them for the sender.

| # | Firm | City | Website | Source page for the email | Fit | Status |
|---|---|---|---|---|---|---|
| 1 | CO Pool Doctor (Pool Doctor) | Lakewood | copooldoctor.com | copooldoctor.com/contact/ (also on the home page) | Strong: home page lists commercial pool and spa service, with clients named as apartment complexes, HOAs, aquatic facilities, fitness centers, clubs and schools; runs CPO classes (copooldoctor.com/cpo-classes/) | not sent |
| 2 | Front Range Recreation, Inc. | Parker | frontrangerecreation.com | frontrangerecreation.com (home page "Contact Us" block) | Strong: pool facility management and full-service maintenance since 1990; about page: "We have both Certified Pool Operators and Aquatic Facility Operators on staff". RISK: big enough to propose as prime; ask | not sent |
| 3 | Patriot Pool and Spa LLC | Arvada | patriotpoolspa.com | patriotpoolspa.com (home page contact section) | Good: "We work exclusively with commercial properties" (apartment complexes, HOAs, hotels, fitness facilities); "our team is fully certified" | not sent |
| 4 | Blue Mind Pool Works, LLC | Englewood / Denver metro | bluemindpoolworks.com | bluemindpoolworks.com (home page) | Good: "semi-public HOA, community, hotel, fitness center, or apartment pools"; CPO not stated on the page | not sent |
| 5 | Pyle's Pool & Spa Specialists | Centennial | pylespoolnspas.com | pylespoolnspas.com (home page; same address on the Centennial service-area page) | Fair: HOA and commercial pools, CPO-certified service; address is a free-mail mailbox, likely a small shop (capacity question) | not sent |
| 6 | Puddle Pool Services (Denver) | Denver (national network) | puddlepools.com | puddlepools.com/contact/ (company-wide mailbox) | Fair: its Denver commercial page lists HOA pool management and PHTA-certified techs (per search snippet; the page did not load for us); national brand, local crew size unknown | not sent |

All six are Denver-metro firms (Lakewood, Parker, Arvada, Englewood, Centennial, Denver). The pools are in CCSD, which
spans parts of "Aurora, Centennial, Greenwood Village, Englewood, and Denver" (RFP p.4); drive time from Lakewood and
Arvada is a fair question for the second email.

## Backups (no public email on own site; not first touch)

| Firm | City | Why held |
|---|---|---|
| Integrity Pool Builders | Englewood | Commercial community-pool construction plus "Pool Maintenance & Service"; contact form only (integritypoolbuilders.com/contact/) |
| Poolwerx Denver | Arvada | Franchise with commercial clients per reviews; contact form only (poolwerx.com location page) |
| Wetworks Pool and Spa LLC | Littleton / Englewood | "RESIDENTIAL and COMMERCIAL" maintenance per Houzz; no website or email found |
| Metro Pools | Aurora | HOA and commercial service per directory listings; no website or email found |
| Hydro Pools LLC | statewide | CPO-certified, pump-room repair focus; small; no website or email found |

Not routed: H2 Global Solutions. CLAUDE.md names them for boiler / water-treatment mechanical jobs, but this is daily
on-site pool service, and their stated area is "anything east of Colorado Springs or throughout Kansas" (Silas,
2026-11-09). HQ may still add them.

## Pricing-request email (body; humanize gate PASS 2026-11-18, 141 words)

Body file: ops/outbox/2026-11-18/cherrycreek-pool-firsttouch.txt (ends at "Thanks Team,"; the sender adds the 4-line
signature). Send bcc, one message, from Luke's business mailbox, through scripts/send_outbox.py or scripts/gmail_api.py
(the gate runs again on send). Gate check run: `python3 scripts/humanize_gate.py check
ops/outbox/2026-11-18/cherrycreek-pool-firsttouch.txt --subject "Pricing request: Cherry Creek Schools pool operations and
maintenance, RFP 27-014"` -> "PASS with warnings" (only warning: 141 words vs 90 target).

```
Hi Team,

I'm Luke Adams with Brown Bison Holdings. We're bidding Cherry Creek School District's pool operations contract (RFP 27-014). Brown Bison is the prime, and we want a commercial pool company with CPO-certified techs as our sub.

The work covers six high school pools, seven days a week, with three separate water-testing visits per pool each day. The District supplies the pool chemicals, and every tech needs a background check.

Can you send a weekly price per pool, your Additional Pricing rates and your cleaning frequencies on the District's workbook by Wednesday, December 9?

There is an optional site visit Thursday, December 3 at 9:00 AM, starting at the Overland High School pool. Can someone from your team attend and sign in for Brown Bison? If so, please send the attendee's name by Tuesday, December 1.

The RFP, pricing workbook and insurance requirements are attached.

Thanks Team,
```

Attachments (about 0.8 MB): docs/RFP 27-014 District Pool Operations.pdf; docs/RFP_27-014_District_Pool_Pricing_Cleaning.xlsx;
docs/Insurance Requirements 06.15.26.pdf.

Facts in the email, with source: six high school pools (Exh A 2, p.32); seven days a week (Exh A 3, p.33); "three
separate onsite water-testing visits per day at each pool" (Exh A 3.A, p.33); District supplies routine pool chemicals
(Exh A 5, p.38); criminal background check for each employee (MSA 2.9.1, p.12); CPO (Exh A 4, p.37); site visit date,
time, start point and "Not mandatory" (Sec 2.1, p.5); workbook tabs Facility Pricing, Additional Pricing, Cleaning
Frequency Schedule (xlsx).

## Log
- 2026-11-18 (new-bid session, no sends allowed): 6 firms with a public email on their own site found and verified;
  5 backups held. Body written, gate PASS. Nothing sent, nothing posted, no RSVP.
- 2026-11-18 20:5xZ (HQ, gate PASS, skip list 0): first-touch pricing ask SENT bcc 6 (Front Range Recreation, CO Pool Doctor, Patriot Pool and Spa, Blue Mind Pool Works, Pyle's Pool & Spa, Puddle Pool Services), msg 1a1f0727d4878fb8; RFP + pricing workbook + insurance attached; pricing by Wed 12/09; optional 12/03 visit attendee name by Tue 12/01.
