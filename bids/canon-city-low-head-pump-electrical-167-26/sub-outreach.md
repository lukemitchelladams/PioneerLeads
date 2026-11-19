# Cañon City Bid 167-26 Electrical Work for Low Head Pump Station: sub outreach (commercial / industrial electrician)

Opened 2026-11-19 (CEO GO 11/18). **Drafted, nothing sent.** The bid set is not in hand (BidNet login needed), so the email
points the sub to BidNet Direct, where registration is free, instead of attaching files; when Luke pulls the documents, attach
them and keep the rest of the body. Two parallel lines; line 2 goes 48 h after line 1 if line 1 is silent. The walk status is
unknown, so the first email already asks for an attendee if the City holds one (CEO 11/18 rule 4). Brown Bison is the bidder;
the electrician prices for us.

Ask: a price on the electrical scope, the firm's Colorado electrical contractor license number, a COI, and an attendee if
there is a walk. Pricing by **Wed 2026-12-09** (8 days before the 12/17 11:00 closing).

Mailboxes are kept out of this public repo, in the operator's private sub list (newgo-subs.json, not committed). Each one is
printed on the firm's own website.

| Line | Firm | City | Where the email is printed | Fit | Status |
|---|---|---|---|---|---|
| 1 | J.R.B. Electric, LLC | Florence, CO (Fremont County, same county as Cañon City) | its own site, home page | Local family-owned electrical contractor; site lists "Commercial Electrical"; Royal Gorge chamber member | not sent |
| 2 | Main Electric | Pueblo, CO | its own site, Contact Us page | Commercial, industrial and utility electrical "Since 1945"; "Facility Shutdown Maintenance and Upgrades", "Industrial Electrical Installation and Modifications" | not sent |

Web form only (no email on their own site, 2026-11-19): I & C Power (Pueblo West; commercial and industrial, "heavy machinery,
control systems, and power distribution"), Adams Electric Inc. (Pueblo; serves "all of southeastern Colorado ... from Salida to
the Kansas border"). Use the web form if a third line is needed; nobody phones them.

## Email (one firm at a time, or bcc). Subject: Canon City Low Head Pump Station electrical, Bid 167-26

`python3 scripts/humanize_gate.py check BODY --signature` = **PASS** (2026-11-19, no warnings); the same body cut at
"Thanks Team," = **PASS** with the plain `check`; subject = PASS. When the documents are in hand, replace the second sentence
of paragraph 1 with "Bid documents attached." and re-run the gate.

```
Hi Team,

Brown Bison is bidding the City of Canon City's electrical work at the Low Head Pump Station (Bid 167-26, due Thu 12/17) and needs a local electrical sub. The bid set is on BidNet Direct under City of Canon City, free to register.

Can you price the electrical scope and send your number, your Colorado electrical contractor license number and a COI by Wed 12/09? If the City holds a site walk, can someone from your team attend for Brown Bison?

Thanks Team,
Luke Adams
Operations Manager
Brown Bison Holdings LLC
luke@brownbisonco.com
```

## Log
- 2026-11-19 (HQ worker): 2 lines found (own-site emails), 2 form-only firms noted; draft gate PASS; nothing sent.
