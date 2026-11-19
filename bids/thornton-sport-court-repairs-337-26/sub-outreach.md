# Thornton RFP 337-26 Sport Court Repairs On-Call: sub outreach (sport-court resurfacing / post-tension concrete)

Opened 2026-11-19 (CEO GO 11/18). **Drafted, nothing sent.** Two parallel lines per the CEO's 11/18 rule; the second goes out
48 h after the first if line 1 is silent. No walk to attend (the optional 11/17 Teams conference is past; no site visit in the
RFP). Brown Bison is the bidder and holds the contract; the sub prices for us and is listed on Exhibit B.

Ask: Exhibit C rates (labor regular and overtime, owned equipment), unit prices for the court items, five Colorado court
projects from the last three years with a contact each (the RFP's minimum qualification, see README gate 1), the firm's City of
Thornton contractor license if it holds one (gate 2), and a COI. Pricing by **Wed 2026-12-02** (7 days before the 12/09 17:00
due date). Attach docs/337-26-rfp-11-6-26.pdf (1.0 MB) to every email; no links.

Mailboxes are kept out of this public repo, in the operator's private sub list (newgo-subs.json, not committed). Each one is
printed on the firm's own website (page named below).

| Line | Firm | City | Where the email is printed | Fit | Status |
|---|---|---|---|---|---|
| 1 | Court Builders of the Rockies | Littleton, CO | its own site, Contact Us page | Tennis and pickleball court construction and resurfacing; site mentions post-tension pickleball complexes | not sent |
| 2 | Parkin Tennis Courts | Salt Lake City, UT (serves Colorado) | its own site, Contact page | Post-tension concrete court builder; "Serving clients throughout Utah, Colorado, Arizona, Wyoming and Idaho" | not sent |

Web form only (no email printed on their own site, 2026-11-19): Renner Sports Surfaces (Denver; post-tensioned court
specialist), Altitude Athletic Surfaces (Englewood; post-tension tennis and pickleball), Coatings, Inc. (Arvada; court
construction and resurfacing). Use the firm's web form if a third line is needed; nobody phones them (CLAUDE.md call rule).

## Email (send to each firm one at a time, or bcc). Subject: Thornton sport court repairs, RFP 337-26

`python3 scripts/humanize_gate.py check BODY --signature` = **PASS** (2026-11-19, no warnings). The same body cut at
"Thanks Team," (the gmail_api.py body file, which adds the signature itself) = **PASS** with the plain `check`. Subject = PASS.

```
Hi Team,

Brown Bison is bidding the City of Thornton's on-call sport court repair contract (RFP 337-26) and needs a court sub. RFP attached.

Work comes as task orders: crack repair, resurfacing and striping, post-tensioned concrete, nets, posts, fencing and lighting. Emergencies need a crew on site within 24 hours.

Labor: hourly rates, regular and overtime

Equipment: owned equipment hourly rates

Unit prices: crack repair, resurfacing, striping, nets and posts, fence repair

Experience: five Colorado court projects from the last three years, with a contact for each

License: your City of Thornton contractor license, if you hold one

Can you send those and a COI by Wed 12/02?

Thanks Team,
Luke Adams
Operations Manager
Brown Bison Holdings LLC
luke@brownbisonco.com
```

## Log
- 2026-11-19 (HQ worker): 2 lines found (own-site emails), 3 form-only firms noted; draft gate PASS; nothing sent.
