# DEN RFP DEN-2026-020-10021 HVAC filter replacement and coil cleaning: sub outreach

Brown Bison is the proposer and holds the contract; the HVAC service firm is our sub and does the field work (filter
changes, coil cleaning, day and night crews at DEN). Proposal due **2026-12-04 14:00 MST** on BidNet. Pre-proposal
meeting is **OPTIONAL** (Teams, 2026-11-20 14:00 MST); there is no site walk, so subs price from the documents.
Ask: unit prices on every Pricing Form line, plus whether they hold City of Denver MWBE certification, by
**Mon 2026-11-30** (HQ date; rule 0b wants 7+ days before submission, and 11/30 leaves 4 because of Thanksgiving week).

Rules from the RFP that shape this outreach:
- 7% MWBE goal, met "with certified firms" in the City's directory "or through the demonstration of a sufficient good faith
  effort" (RFP p.3). The Good Faith Effort form (docs/DSBO Good Faith Effort Form.pdf, item 9) asks when outreach began,
  how long firms had to respond, the methods used and the follow-ups. **Log every send and chase below with date and time;
  that log becomes the GFE answer.** Item 15 asks how we used DSBO resources: the certified firms below came from the DSBO
  directory (denver.mwdbe.com), searched 2026-11-17.
- "Proposers who submit a proposal in response to this RFP are precluded from participating as a subcontractor with any
  other Proposers" (RFP p.16, III-13). A firm that proposes as prime cannot be our sub. Ask each firm that replies.
- The proposal must "describe the qualifications of each subcontractor ... and the percentage and scope of the work" and
  include "Resumes for the subcontractor's key personnel" (RFP p.16, III-13). The second ask, once a firm says yes, is
  1-page resumes for its supervisor and lead technician, 3 references, and its licenses.
- Each tech must be badged and pass DEN security; subs must carry insurance per DEN Rules Part 230 (Sample Contract 7.B).

## Firms (first touch: email published on the firm's own website, page loaded 2026-11-17)

| # | Firm | City | Email | Verified on | City of Denver MWBE | Fit | Status |
|---|---|---|---|---|---|---|---|
| 1 | UPM Mechanical, LLC | Henderson | info@upmmechanical.com | upmmechanical.com/contact/ | **Yes** (DSBO directory) | Strong: site lists "Periodic Planned Maintenance ... Quarterly Semi-Annually Annually", AHU/RTU/CRAC/CRAH, City & Government, Healthcare, Data Centers | not sent |
| 2 | Rasmussen Mechanical Services (Rocky Mountain branch) | Centennial | rockymountain@rasmech.com | rasmech.com/contact-us/ ("DENVER, COLORADO ... Email: rockymountain@rasmech.com") | No | Strong: commercial maintenance plans with filter changes and coil cleaning; universities | not sent |
| 3 | Tolin Mechanical Systems | Denver | customerservice@tolin.com | tolin.com (header and contact block) | No | Strong: Denver HQ; planned maintenance, IAQ, government and hospital clients | not sent |
| 4 | Mechanical Solutions, Inc. (MSI) | Englewood | info@msicolorado.com | msicolorado.com (contact markup) | No | Good: commercial HVAC service and preventative maintenance, hospital work | not sent |
| 5 | ACCO Engineered Systems, Denver office | Englewood | servicerequest@accoes.com | accoes.com/about/locations/ (company-wide 24/7 service mailbox) | No | Good, large: service page lists coil cleanings and maintenance agreements; campus, hospital, government | not sent |
| 6 | Aether Mechanical LLC | Aurora | info@aethermechanical.com | aethermechanical.com/contact-aether/ | **Yes** (DSBO directory) | Fair, small: residential and commercial; maintenance plan lists filter replacements and indoor/outdoor coil cleaning | not sent |
| 7 | Standard Mechanical Incorporated | Arvada | named address in HQ's private list | standardmechinc.com/contact/ | **Yes** (DSBO directory; own site: "DENVER CERTIFIED MBE-DBE-SBE-EBE") | Fair: commercial, industrial and institutional HVAC | not sent |

MWBE marks come only from the City's own DSBO certified directory (denver.mwdbe.com, detail pages read 2026-11-17).
Non-MWBE firms 2-5 bring airport-scale crews; MWBE firms 1, 6 and 7 count toward the 7% goal. The best result is a lead
sub plus a certified firm on a defined share of the units (for example a building group or the FCU/FP-VAV lines).

## Backups (not first touch)

| Firm | City | Why held | MWBE |
|---|---|---|---|
| Pacific Air Inc. dba Million Air Mechanical | Littleton | Own site cites "Denver International Airport" and UC Health projects (installation). No email on own site; DSBO-listed address in HQ's private list | Yes (DSBO) |
| Solutions Mechanical, LLC dba Solutions Contracting | Aurora | Own services page lists "Denver International Airport" and "City & County of Denver" as clients. No email on own site; named DSBO address in HQ's private list | Yes (DSBO) |
| Integrated Mechanical Solutions LLC | Wheat Ridge | integratedmechanical77@gmail.com (own contact page). Small plumbing/HVAC shop, "routine maintenance"; weak fit | Yes (DSBO) |
| Murphy Company (Denver) | Denver | Campus/university PM work, but no general email on its site (only a data-center mailbox) | No |

Other DSBO-certified "mechanical" firms checked and skipped: JCOR Mechanical (Golden; construction, no email on site),
Maize Mechanical (Thornton; residential heat pumps), Omni Elite Mechanical (Broomfield; sheet metal fabrication),
Enhanced Mechanical, M1 Mechanical and Rocky Mechanical (Colorado Springs / Pueblo; outside the metro), HBC Mechanical
(Frisco), Horizon Mechanical Solutions (Greeley; sheet metal manufacturing). Incumbent hint: 12 Appendix III work orders
carry "TRUE CLEANING SOLUTIONS" (a Denver duct/dryer-vent cleaning firm per its Angi listing); not contacted, since it may
propose itself.

## Pricing-request email (body only; humanize gate PASS 2026-11-17, 118 words)

Subject (gate PASS): Pricing request: DEN HVAC filter replacement and coil cleaning, RFP DEN-2026-020-10021

Send bcc, one email per firm, from luke@brownbisonco.com, through scripts/send_outbox.py or scripts/gmail_api.py (gate
runs on send; the sender adds the 4-line signature). Body file:
/tmp/claude-0/-home-user-PioneerLeads/9eba1390-a8c1-5755-a9f9-e6b40e48b070/scratchpad/den-body.txt (scratchpad; copy it
into ops/outbox/<date>/ before sending).

```
Hi Team,

Brown Bison Holdings is bidding the Denver International Airport HVAC filter replacement and coil cleaning contract (RFP DEN-2026-020-10021), a 5-year term. Brown Bison submits the proposal and holds the contract; the field crews would be yours.

DEN lists about 1,700 units: 5,774 filter changes and 1,699 coil cleanings a year. DEN supplies the filters.

Crews work day and night shifts, and every worker needs an airport badge. Rates must include Denver prevailing wage where required.

Can you send unit prices for each line of the attached Pricing Form by Monday, November 30? Please also tell us if your firm holds a City of Denver MWBE certification.

Attached: the RFP, the Appendix III asset list and the Pricing Form.

Thanks Team,
```

Attachments (about 3.3 MB total): docs/RFP_DEN-2026-020-10021.pdf; docs/Appendix III of Scope of Work - HVAC Assets_
Locations_ and filter Types.xlsx; docs/Attachment 2 Exhibit B - Pricing Form.xlsx.

Facts in the email, with source: 5-year term (Sample Contract 4.A); "1700 HVAC assets" (RFP p.3); 5,774 / 1,699 (Appendix
II totals); filters excluded from contractor materials (Exh A 1(c)); day and night crews (Exh A 1(l)); all onsite staff
badged (Exh A 1(k)); "All rates must include Prevailing Wage Rates where required" (Pricing Form).

## Log
- 2026-11-17 (research session, read-only): firms found and emails verified on their own sites; DSBO directory searched
  for certified mechanical firms. Nothing sent.

## Log
- 2026-11-17 18:1xZ (11:1x MT, HQ, gate PASS, send_outbox.py): pricing request (body above) sent bcc to 6 firms: UPM Mechanical (MWBE), Rasmussen Mechanical, Mechanical Solutions Inc, ACCO Engineered Systems, Aether Mechanical (MWBE), Standard Mechanical (MWBE) (msg 1a1eab143f3e83ba); RFP + Appendix III + Pricing Form attached; unit prices by Mon 11/30. Tolin was held back by the skip list (replied 11/13 on Canon City boiler/chiller, pricing still owed): add the DEN ask to Wednesday's Canon chase, one email. Not sent: Integrated Mechanical (weak), Million Air / Solutions Mechanical (no email on own site).
- 2026-11-18 15:36Z (HQ): Tolin Mechanical asked in the Canon City thread to price DEN too (RFP + Appendix III + Exhibit B attached), msg 1a1ef4d60da8a2c2; unit prices by Mon 11/30.
