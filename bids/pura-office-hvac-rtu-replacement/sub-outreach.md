# PURA RFQ (Office HVAC Replacement + 125 Riverwalk Pl RTU): sub outreach

Brown Bison quotes as prime and holds the contract; a Pueblo-licensed mechanical contractor performs the work and pulls the permits.
Licensing question to PURA still open (asked 2026-11-17, msg 1a1eb3f530b9ebf1; follow-up drafted 2026-11-20 in pura-followup-body.txt):
RFQ p.4 "Contractors must be licensed to do mechanical work in Pueblo County and have at least three years of commercial HVAC experience."
**Under OVERDRIVE the sub lines go out now (rule 0b: they should have started 11/17); we do not wait on PURA's answer.** NO-BID only if PURA
says the license must be in the bidder's own name.

Mailboxes are NOT in this public repo: they are in the HQ private list (scratchpad pura-subs.json), each one printed on the firm's own
website. One email per company per day.

| # | Firm | City | Email | Fit (from the firm's own site unless noted) | Status |
|---|---|---|---|---|---|
| 1 | R & R Heating & Air Conditioning, Inc. | Pueblo | own-site address (private list) | Since 1981; commercial installs for office buildings, medical, churches, retail; has a commercial estimator for bids | not contacted |
| 2 | Industrial Plumbing & Heating Co. | Pueblo | own-site address (private list) | Commercial HVAC "Replacements or retrofits", maintenance programs; Carrier Factory Authorized Dealer | not contacted |
| 3 | Rial Heating & Air Conditioning, Inc. | Colorado Springs (serves Pueblo) | own-site address (private list) | Commercial design-build/install, office spaces; Pueblo page cites a commercial RTU repair; Carrier dealer | not contacted |
| 4 | Mike's Plumbing & Heating LLC | Colorado Springs (serves Pueblo County) | own-site address (private list) | Pueblo County service area; public Fremont County RTU proposal lists office RTU replacements and a Pueblo Housing Authority job | not contacted |
| backup | R Buck Heating, Cooling, Plumbing & Electrical | Pueblo / Colorado Springs | own-site address (private list) | Only firm found printing a Pueblo contractor license on its own site, but reads residential | hold |

Colorado Springs firms (lines 3-4) are second choice: each must confirm a Pueblo County mechanical license.
Not used: ACCO Engineered Systems (asked on DEN 11/17; large engineered-systems shop); Rocky Mechanical and Vision Mechanical (no own
website found); Clarks Mechanical (residential-focused); Alpine Electric & Refrigeration (no readable email); Fesmire Heating & Air,
Nielsen Mechanical, Pueblo Heating & Air (phone-only).

## Email
- Body: `sub-firsttouch-body.txt` (this folder). `python3 scripts/humanize_gate.py check` PASS 2026-11-20, no warnings. Ends at
  "Thanks Team,"; the sender appends the signature.
- Subject: Pueblo Urban Renewal Authority HVAC quote: licensed mechanical partner needed by 11/24 (gate `--subject` PASS).
- Attach: the RFQ PDF from docs/. No links.
- Asks, all due Tue 2026-11-24 (7 days before the 2026-12-01 16:00 MT due date): lump-sum pricing for either or both parts; Pueblo County
  mechanical license and EPA 608 confirmation; three similar commercial references from the last three years; whether their person can
  walk both sites for Brown Bison (optional walk, by appointment with PURA). Nothing is scheduled under Luke's name.
- Replaces the 11/17 draft (ops/outbox/2026-11-17/pura-sub-firsttouch.txt), which asked for pricing by 11/25 and no license/references.

## Log
- 2026-11-17 21:0xZ: first list built (5 own-site emails), email drafted and gated; NOT SENT (held for PURA's licensing answer).
- 2026-11-20 ~12:45Z: list re-verified on each firm's own site; 4 lines + 1 backup; new body gated PASS. NOT SENT (agent run with no
  mail access; HQ sends from luke@brownbisonco.com).

- 2026-11-20 20:46Z (Mac send run): follow-up to Chris DeLuca (1a1fab60b5861c28) + licensed-partner asks to Rial Heating (1a1fab65afd7f369) and R Buck Heating (office@callbuck.com, 1a1fab681d106ed5). **21:07Z REPLY from Chris DeLuca (msg 1a1fac93acad0eb8):** "I am sorry you were in my junk folder. We do prefer a local contractor. I am not sure if running it from up north would be cost effective to us. But you are more than welcome to submit" / "We will take a look and get back to you." No direct answer to the license question yet; not a disqualifier. A Pueblo-licensed sub doing the work answers the "local" preference.
