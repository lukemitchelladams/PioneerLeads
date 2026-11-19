# Westminster RFP-PWU-26-079 On-Call Roofing Services: sub outreach (licensed commercial roofer)

Opened 2026-11-19 (CEO GO 11/19 13:45 MT). **Drafted, nothing sent.** The RFP is not in hand (BidNet login needed), so the email
points the sub to BidNet Direct instead of attaching files; when Luke pulls the documents, attach them and change the second
sentence of paragraph 1 to "RFP attached." Re-run the gate after any edit. Brown Bison is the bidder and holds the contract;
the roofer prices for us and does the work under its own roofing license and insurance.

CEO rule: the first email asks for the roofer's own roofing license (number and issuing city or county) and its insurance
(COI). Both are in the draft. The walk status is unknown, so the first email also asks for an attendee if the City holds one.
Pricing by **Mon 2026-12-14** (8 days before the 12/22 16:00 closing). Line 1 and 2 go first; line 3 goes 48 h later if
both are silent.

Mailboxes are kept out of this public repo, in the operator's private sub list
(/tmp/claude-0/-home-user-PioneerLeads/9eba1390-a8c1-5755-a9f9-e6b40e48b070/scratchpad/newgo2-subs.json, not committed).
Each one is printed on the firm's own website (page named below).

| Line | Firm | City | Where the email is printed | Fit | Status |
|---|---|---|---|---|---|
| 1 | Bear Brothers Roofing | Denver, CO 80229 (north metro, next to Thornton and Northglenn) | its own site, Contact page | Commercial and low-slope roofing; EPDM and flat-roof pages; Broomfield commercial roofing page | not sent |
| 2 | Superior Roofing, Inc. | Aurora, CO | its own site, Contact page ("Send Bid Invitations") | Large commercial roofer: commercial, metal roofing, waterproofing, service and repair | not sent |
| 3 | Colorado Weather Coatings Inc. | Broomfield, CO (N. Federal Blvd) | its own site, header and footer | Commercial roofing, roof coatings, spray foam, flat and low-slope, repair; "Operating 40 years under the same name" | not sent |

Backup with an own-site email: Western Roofing Inc (Aurora; commercial since 1996, roofing maintenance contracts, 24/7
emergency service; Contact page). Checked, no email printed on their own site (2026-11-19): Front Range Roofing Systems,
Douglass Colony Group (placeholder only), Horizon Roofing, Colorado Commercial Roofing, Mile High Roofing Services (Westminster;
address only in page metadata). Nobody phones them (CLAUDE.md call rule).

## Email (one firm at a time, or bcc). Subject: Westminster on-call roofing, RFP-PWU-26-079

Body file for scripts/gmail_api.py: `bids/westminster-oncall-roofing-pwu-26-079/sub-outreach-body.txt` (ends at "Thanks Team,";
the sender adds the signature). `python3 scripts/humanize_gate.py check sub-outreach-body.txt --subject "Westminster on-call
roofing, RFP-PWU-26-079"` = **PASS** (2026-11-19, no warnings).

```
Hi Team,

Brown Bison is bidding the City of Westminster's on-call roofing services contract (RFP-PWU-26-079, due Tue 12/22) and needs a commercial roofing sub. The RFP is on BidNet Direct under City of Westminster.

Brown Bison holds the contract and your crews do the roof work on City buildings as jobs come in.

Rates: labor hourly, regular and after-hours

Unit prices: common repairs and replacement by roof type

Materials: your markup on materials

License: your roofing contractor license number and the city or county that issued it

Insurance: a COI showing your general liability and workers' comp

Can you send those by Mon 12/14? If the City holds a site walk, can someone from your team attend for Brown Bison?

Thanks Team,
```

## Log
- 2026-11-19 (HQ worker): 3 lines + 1 backup found (own-site emails), 5 no-email firms noted; draft gate PASS; nothing sent.
