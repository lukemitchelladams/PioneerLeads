# Hyland Hills 2027 Concrete Removal and Replacement On Call: sub outreach (commercial concrete flatwork)

Opened 2026-11-19 (CEO GO 11/19 13:45 MT). **Drafted, nothing sent.** The bid set is not in hand (BidNet login needed), so the
email points the sub to BidNet Direct instead of attaching files; when Luke pulls the three files, attach them (the .docx and
.xlsx are fine attachments) and change the second sentence of paragraph 1 to "Bid documents attached." Re-run the gate after
any edit. Brown Bison is the bidder and holds the contract; the concrete sub prices for us and does the work.

Rule 0b timing: the bid is due Mon 11/30 13:00, so pricing is asked by **Mon 2026-11-23** (7 days out). Line 1 and line 2 go
together today (11 days out, no time for a 48-hour stagger); line 3 goes Sat 11/21 if neither answers. The walk status is
unknown, so the first email already asks for an attendee if the District holds one.

Ask: unit prices for removal and replacement (the 2027 bid tab, once in hand), concrete and structural fill supply lines
(last year's bid priced them separately), years in business plus two recent flatwork jobs (in case the District sets an
experience bar the sub must carry), and a COI.

Mailboxes are kept out of this public repo, in the operator's private sub list
(/tmp/claude-0/-home-user-PioneerLeads/9eba1390-a8c1-5755-a9f9-e6b40e48b070/scratchpad/newgo2-subs.json, not committed).
Each one is printed on the firm's own website (page named below).

| Line | Firm | City | Where the email is printed | Fit | Status |
|---|---|---|---|---|---|
| 1 | Colorado Paving and Concrete | Northglenn, CO (next to Federal Heights) | its own site, home page ("EMAIL US") | Commercial pavement, parking lots, sidewalks and pathways; "Servicing the entire Colorado Front Range" | not sent |
| 2 | KRM Concrete LLC | Keenesburg, CO; "Colorado Statewide" | its own site, Contact section | Commercial flatwork, "Parking lots, curb & gutter, ADA sidewalks"; City of Northglenn awarded it the 2024 Residential Concrete Program (Northglenn CR-179) | not sent |
| 3 | Coloscapes Concrete | Loveland, CO | its own site, footer (Colorado Address) | Full-service commercial concrete: flatwork, site concrete, selective demolition; farther out, backup | not sent |

Checked, no email printed on their own site (2026-11-19): ABCO Contracting (Denver 80229, Thornton-prequalified concrete;
address only in page metadata, contact is a web form), Alpine Civil Construction (heavy civil; web form), Naranjo Civil,
Concrete Express, Fasick Concrete, Goodland Construction, Harper Brothers (web forms or no address). Use a web form if a fourth
line is needed; nobody phones them (CLAUDE.md call rule).

## Email (one firm at a time, or bcc). Subject: Hyland Hills concrete on-call pricing, due 11/30

Body file for scripts/gmail_api.py: `bids/hyland-hills-concrete-oncall-2027/sub-outreach-body.txt` (ends at "Thanks Team,";
the sender adds the signature). `python3 scripts/humanize_gate.py check sub-outreach-body.txt --subject "Hyland Hills concrete
on-call pricing, due 11/30"` = **PASS** (2026-11-19, no warnings).

```
Hi Team,

Brown Bison is bidding Hyland Hills Park and Recreation District's 2027 concrete removal and replacement on-call contract (due Mon 11/30) and needs a concrete sub. The bid set is on BidNet Direct under Hyland Hills Park and Recreation.

Work comes as unit-price jobs at District parks and facilities. Last year's contract covered sidewalks, pans, curb and gutter, floors and patios.

Unit prices: removal and replacement per square foot and per linear foot

Materials: concrete and structural fill supplied and delivered

Experience: years in business and two recent public or commercial flatwork jobs

Can you send those and a COI by Mon 11/23? If the District holds a site walk, can someone from your team attend for Brown Bison?

Thanks Team,
```

## Log
- 2026-11-19 (HQ worker): 3 lines found (own-site emails), 7 form-only or no-email firms noted; draft gate PASS; nothing sent.
