# SUBMISSION: La Plata County IFB Project #26-053-1215, On-Call Services – Various Trades

**Pre-bid / site visit: NONE, nothing mandatory.** No pre-bid meeting or site visit is stated in the IFB. Optional only: "Bidders
are invited to attend a public bid opening, which will be conducted through Microsoft Teams Meeting, at the date and time of the
bid submission deadline." (p.3, p.8). Nobody attends for Brown Bison.

Pre-built 2026-11-12 evening MT. No prices in this file. Quotes are from `docs/IFB - On-Call Services - Various Trades.pdf`
(printed page numbers; sample contract by PDF page); anything the IFB does not say is marked "not stated in the solicitation".

## How and where

| Item | Quoted from the IFB |
|---|---|
| Method | **Email only.** p.8: "Bids must be submitted electronically. Bids shall be emailed, with the subject line stating 'On-Call Services – Various Trades, Project #26-053-1215' to: KHightower@lpcgov.org and SIwanicki@lpcgov.org." Same on p.3. **Plan: one email to both addresses, one PDF attached.** |
| Subject line | IFB text: "On-Call Services – Various Trades, Project #26-053-1215". The humanize gate refuses the en dash in a subject ("dash other than '-' (U+2013 EN DASH)", tested 2026-11-12), so type it as **On-Call Services - Various Trades, Project #26-053-1215** (ASCII hyphen; same words, same project number). |
| Recipients | To: KHightower@lpcgov.org, SIwanicki@lpcgov.org (both, per p.8). No cc to subs. |
| Format | File type, size limit, page limit and number of copies: not stated in the solicitation. Plan: one PDF of the County's pages 10-15 filled in and signed, cover letter first. Keep it small (scans at 150-200 dpi) so neither County mailbox rejects it. |
| Responsive items | p.8: "Completed and signed Bid Sheet (pages 10-13); Completed Business Information Form (page 14); and, Completed Colorado Open Records Act Notice, Acknowledgment and Indemnification form (page 15)." |
| Deadline | **Tue 2026-11-17 10:00 MST.** p.1 and p.10: "Bid Deadline: November 17, 2026, 10:00 AM MST". p.8: "must be received by the staff of the La Plata County Procurement Division no later than November 17, 2026, 10:00 AM MST." (2026-11-17 is a Tuesday; MST = Mountain time in November.) |
| Late rule | p.8: "Bids received after the deadline will not be considered." (also p.3). |
| Questions | Closed. p.4 item 2: "no later than seven calendar days prior to the Submittal Deadline (November 10, 2026, 5:00 PM MST)". |
| Addenda | p.4 item 2: posted on BidNet; "Respondents shall acknowledge receipt of each Addendum in their submission ... Failure to acknowledge receipt of any Addendum issued may invalidate a submission as incomplete." p.12: "Please include signed Addenda, if applicable, in your submittal." |
| Bid opening | p.8: "Bidders are invited to attend a public bid opening, which will be conducted through Microsoft Teams Meeting, at the date and time of the bid submission deadline. Also, as soon as practical after the bid deadline, the bids shall be opened and tabulated. The tabulation sheet will be sent to all bidders." Optional; nobody attends. |
| Hold period | p.4 item 4: "All bids shall remain in force for a period of sixty (60) days after the date of the submittal deadline." p.10: "sixty (60) days after the date of the bid opening." Through 2027-01-16. |
| Award | p.8: "The bids shall be awarded by the Board of County Commissioners, County Manager, or Procurement Manager." p.3: "It is the bidder's responsibility to verify the exact date of the award." Award date: not stated in the solicitation. |
| After award | p.9: "execute the Agreement and submit it, along with the insurance certificate and W-9 within ten (10) calendar days from the date when the Notice of Award and Independent Contractor Agreement is delivered to the Bidder." Notice of Award (PDF p.16): return "by email to: SIwanicki@lpcgov.org" the Acceptance, signed contract, COI/endorsements naming La Plata County and the BOCC as additional insureds, and "Proof of Workers' Compensation coverage." |
| Public record | GC 6 (p.7): all documents "are subject to the Colorado Open Records Act"; confidential markings "may be disqualified or rejected". Nothing is marked. |

Who sends: CLAUDE.md says never submit a bid without asking. HQ emails Luke the final PDF; on **Luke's explicit written OK**, HQ
sends from luke@brownbisonco.com with `scripts/gmail_api.py send` (gate runs first), or Luke sends it himself. Attachment name:
`BrownBison_LaPlata_26-053-1215_OnCall-Trades.pdf` (PDF only; the gate refuses .txt/.html/.eml attachments). No links in the
body; no phone number anywhere in the email.

### Submission email body (humanize gate PASS 2026-11-12, re-run PASS 2026-11-13; re-run the gate after any edit)

Body file ends at the closer; gmail_api.py appends the four-line signature (Luke Adams / Operations Manager / Brown Bison
Holdings LLC / luke@brownbisonco.com). Edit the trades sentence to match the rows actually priced. If any addendum was issued,
add it to the list of what the PDF holds ("and signed Addendum No. __"), since p.12 asks for "signed Addenda, if applicable, in
your submittal".

```
Hi Team,

Attached is the Brown Bison Holdings LLC bid for On-Call Services - Various Trades, Project #26-053-1215. The PDF holds the signed Bid Sheet (pages 10-13), the Business Information Form (page 14), the signed CORA acknowledgment (page 15) and a one-page cover letter.

We are bidding HVAC, plumbing, electrical and general repairs.

Please email any questions. Email is the best way to reach me during the day.

Thanks Team,
```

Pre-check: `python3 scripts/humanize_gate.py check --subject "On-Call Services - Various Trades, Project #26-053-1215" BODY`
must print PASS. Send: `python3 scripts/gmail_api.py send --to KHightower@lpcgov.org SIwanicki@lpcgov.org --subject "On-Call
Services - Various Trades, Project #26-053-1215" --body-file BODY -- <final PDF>` (only after Luke's OK).

### Sub follow-up: references, license, COI (humanize gate PASS 2026-11-12; license line edited and re-run PASS 2026-11-13)

Send to the first sub in each trade that sends rates, the same hour, as a reply on its thread; one email per company per day.
The 11/12 ask covered rates and trip charge only.

Subject (if not a reply): `La Plata County on-call trades (project 26-053-1215): references`

```
Hi Team,

Thanks for the rates. To finish the County bid I need three references for similar commercial or public jobs you completed in the last three years. For each, send the entity, contact name, contact email and the contact's phone number (no La Plata County staff, per the IFB).

Please also send your trade license number (state or local) and a current certificate of insurance showing general liability and auto liability of $1,000,000 per occurrence.

I need these by Monday 11/16 at noon. The bid is due to the County Tuesday 11/17 at 10:00 AM.

Thanks Team,
```

Use "Hi <FirstName>," / "Thanks <FirstName>," instead when the reply came from a named person.

## Countdown, today to the deadline (today Thu 2026-11-12 evening MT)

Sub rates asked 2026-11-12 14:3x MT from seven firms, due Fri 2026-11-13 17:00 MT (sub-outreach.md). HQ default: NO-BID if no
Durango rate arrives by then (Luke may overrule).

| Date | Day | What happens | Owner |
|---|---|---|---|
| 2026-11-12 | Thu | Pre-build committed (README, FORMS-CHECKLIST, RESPONSE-DRAFT, SUBMISSION). Nothing sent. | HQ |
| 2026-11-13 | Fri | Inbox checks through the day. Each sub reply: rates into `private/` only; same hour, send that sub the references/license/COI follow-up above. BidNet 0000441130: addenda and any separate Local/Regional Preference form. **17:00 MT sub cutoff**: no rate in any trade = NO-BID (pipeline NO, README log, board line 7). Brown Bison insurance purchase day; nothing in this bid needs a COI before award. | HQ |
| 2026-11-14 | Sat | If GO: build `private/PRICING.md` (sub rate, markup, Year 1, Years 2-3 inside the 3% cap); fill Part 1 rows, delete unpriced trades; fill Parts 0, 2-8; draft PDF v1 (unsigned) emailed to Luke for approval with the HQ default list and the Mon 12:00 overrule window. | HQ -> LUKE |
| 2026-11-15 | Sun | Inbox watch for sub references. A rate that arrives after Fri 17:00 goes in only if HQ or Luke reopens the NO-BID default. | HQ |
| 2026-11-16 | Mon | 09:00 BidNet addenda check (sign and attach any addendum; re-run `python3 scripts/doc_manifest.py laplata`). 12:00 sub references/license due; Luke's overrule window closes. 12:30 HQ sends Luke the signature pages (p.12 initials x3, p.13 signature, p.14 phone, p.15 initials x3 + signature, cover letter, addenda). Luke signs and scans back by 15:00. HQ assembles the final PDF, sweeps for `[PRICE` / `[LUKE` / `[SUB` / `[HQ` markers, emails Luke the final. **On Luke's OK, send by 17:00 MT.** | HQ / LUKE |
| 2026-11-17 | Tue | If Monday slipped: last send 08:00 MT. By 09:00 confirm the sent copy in Sent and no bounce from either address; if one bounced, resend to the other address at once. **DUE 10:00 MST.** Bid opening on Teams 10:00 (optional, nobody attends). Log the message ID in the README. | HQ / LUKE |

After the deadline: tabulation emailed to all bidders (p.8); bids held through 2027-01-16; on a Notice of Award, ten calendar
days for the Acceptance (PDF p.17), the signed and notarized Agreement (PDF p.29), COI naming La Plata County and the BOCC as
additional insureds, proof of workers' comp and the W-9 (p.9, PDF p.16); proof of additional-insured status and subrogation
waivers before the first work order (Exhibit C3-C4, PDF pp.32-33); subcontracts flowing down the Agreement with the County as
third-party beneficiary (sec. 23, PDF p.27).
