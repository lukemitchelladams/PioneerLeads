# SUBMISSION: USDA Forest Service RFQ 1240LP27Q0008, Janitorial Services, Pagosa Ranger District

**RULE 0: site visit NOT MANDATORY, none scheduled.** RFQ p.6: "There is no scheduled site visit for this solicitation.
Interested offerors who would like to tour the Pagosa Ranger District site shall contact: Email: brandon.caley@usda.gov."
The optional Fri 2026-11-13 13:00 MT tour was cancelled by HQ on 2026-11-12 (no attendee). No walk stands between us and
the deadline.

Pre-built 2026-11-12 (evening MT). No prices in this file. Quotes are from `docs/C04 1240LP27Q0008.pdf` (RFQ incl. SF-1449,
PDF pages of 19) and `docs/C04a Attachment 1 Janitorial PWS.pdf` (PWS, printed pages); anything the solicitation does not
say is marked "not stated in the solicitation". **NO-BID default: no sub price by Mon 2026-11-16 12:00 MT = nothing is sent.**

## How and where

| Item | Quoted from the solicitation |
|---|---|
| Deadline | **Thu 2026-11-19 10:00 MT.** SF-1449 block 8: "OFFER DUE DATE/LOCAL TIME 11/19/2026 1000 MT". RFQ p.11: "Quoters shall submit all required technical information, pricing, and past performance information by the solicitation closing date and time identified in the SF-1449." SAM.gov notice 1d1b8d72c87844289d3efb4990073ded closing 2026-11-19. |
| Method / address | **Not stated in the solicitation.** No email address, portal or mailing address is given for quotes. We asked the CO on 2026-11-05 (vendor-questions.md Q2); on 2026-11-09 he wrote that a Q&A amendment "will be posted in the near future". **Plan: email to the Contracting Officer, stephen.holly@usda.gov**, the address the RFQ gives for questions (p.16) for the officer named in SF-1449 blocks 7 and 31b. If the amendment names another address or a portal, follow the amendment. |
| Subject line | RFQ pp.16-17 (under Questions): "Offerors shall include the solicitation name and solicitation number in the subject line of the email." The sentence is written for question emails; a subject rule for the quote email is not stated in the solicitation, so HQ applies the same rule. Use: **Janitorial Services, Pagosa Ranger District, RFQ 1240LP27Q0008: quotation from Brown Bison Holdings LLC** |
| Formats | RFQ p.11: "Document types acceptable for submission are PDF, Microsoft Word-compatible files, and Microsoft Excel-compatible files." p.16 repeats PDF / Word / Excel. |
| Size limit / copies / page limit | Not stated in the solicitation (size asked in Q2). Keep the email to two files and a few MB. |
| Pricing form | RFQ p.5: "Offerors shall submit pricing for all Contract Line Item Numbers, including the base period and all option periods, using Attachment 2 - Schedule of Items." Send the Excel file itself. |
| Signatures | SF-1449 p.1: "OFFEROR TO COMPLETE BLOCKS 12, 17, 23, 24, & 30" (block 30a signature). Attachment 7 certification "SIGNATURE (Sign in ink)". Any SF-30 amendment per its own instructions. |
| Late rule | FAR 52.212-1 is incorporated by reference (p.16); its late-quotation text is not in the package (acquisition.gov is blocked from this session). Treat 10:00 MT as absolute. SF-1449 block 27a also says "FAR 52.212-3 AND 52.212-5 ARE ATTACHED"; neither is in the package (FORMS-CHECKLIST row 15a). |
| Price hold | RFQ p.16: "The offeror agrees to hold the prices in its offer firm for 90 calendar days from the date specified for receipt of offers." Through 2027-02-17. |
| Questions | Closed. RFQ p.16: "Questions are due no later than: November 10, 2026, at 10:00 AM Mountain Time". Ours went 2026-11-05. |
| Amendments | None posted as of the 2026-11-13 03:36Z SAM.gov scan (8 original files). Acknowledge each one in the cover letter and return its signed SF-30. |
| Award basis | RFQ p.7: "Award will be made to the responsible offeror whose quotation represents the lowest price technically acceptable offer with acceptable or neutral past performance." p.8: "Offerors are advised that the Government intends to award without discussions." p.10: "Only the lowest-priced quotation will be evaluated for technical acceptability and past performance." Award date: not stated in the solicitation. |
| SAM | RFQ p.16: "Quoters must have an active entity registration in the System for Award Management to submit a quotation and to be eligible for award." Active through 2027-05-21. NAICS 561720 on the entity record: not on record (Luke checks). |
| Contacts | CO Stephen D. Holly, stephen.holly@usda.gov (RFQ p.16; QASP p.3). PM/FSM Brandon Caley, brandon.caley@usda.gov (RFQ p.6; QASP p.2). Email only. |
| Public record / proprietary marking | Not stated in the solicitation. |

**Files to send (two, built in `private/` because Attachment 2 carries prices):**
1. `BrownBison_1240LP27Q0008_Quote.pdf`: RESPONSE-DRAFT Parts 0, 1 (signed SF-1449 pp.1-4), 2, 4-11, and 12 (signed SF-30s,
   if any), in that order.
2. `BrownBison_1240LP27Q0008_Attachment2_Schedule_of_Items.xlsx`: the Government's workbook with column E filled, every
   CLIN priced, formulas intact (Part 3). A PDF print of it also goes inside file 1 as Part 3.

**Who sends.** CLAUDE.md: the agent never submits a bid without asking. Luke sends from luke@brownbisonco.com, or tells HQ in
writing to send through `scripts/gmail_api.py send` with the two attachments. Before the send: every `[PRICE]`, `[LUKE]`,
`[SUB]` and `[HQ]` marker is gone from file 1; the body passes `python3 scripts/humanize_gate.py check` (no phone, no links,
four-line signature appended by the sender).

**Email body** (gate result 2026-11-12: `PASS`, subject line included; 83 words). If no amendment is posted, replace the
acknowledgment sentence with "No amendments were posted." (that variant also PASS) and re-run the gate.

    Hi Stephen,

    Attached is Brown Bison Holdings LLC's quotation for RFQ 1240LP27Q0008, Janitorial Services, Pagosa Ranger District.

    The PDF holds the signed SF-1449, technical approach, key personnel, quality control plan and biobased product list.
    It also has the employee list, past performance, signed Experience Questionnaire and representations. The Excel file
    is Attachment 2, priced for the base year and all four option years.

    We acknowledge Amendment 0001. Prices are firm for 90 days from November 19.

    Please confirm you received it.

    Thanks Stephen,

## Countdown, today to the deadline (today Thu 2026-11-12, evening MT)

Seven sub asks open (sub-outreach.md): Mountain West Cleaning, 4 Ever Cleaning, PMI, Clean Rite Janitorial, Pagosa Cleaning
Co (sent 2026-11-11, price by Mon 11/16 12:00); CRC Janitorial and Evergreen Cleaning (re-asked 2026-11-11, yes/no by Fri).
Declined: B&K Cleaning, Tidy Team (do not contact). Sub pricing in hand: 0/1.

| Date | Day | What happens | Owner |
|---|---|---|---|
| 2026-11-12 | Thu | Pre-build written (FORMS-CHECKLIST, RESPONSE-DRAFT, SUBMISSION). Tour cancelled with Caley 11:5x MT. Price-from-documents worksheet in `private/` (HQ, 11/12). | HQ |
| 2026-11-13 | Fri | CRC / Evergreen yes/no due. Each hourly scan: SAM.gov notice for the Q&A amendment; file it in `docs/` the hour it lands. Any sub that says yes gets, the same hour by email, the list of what we need by Mon 12:00: base-year and option-year unit prices for the three lines, primary janitor name + resume + two references, On-Site QC Manager name, backup janitor, employee list with experience, product brands with biobased content and SDS, equipment list, years in business and three references. No insurance step: the solicitation requires none, and nothing on this bid waits on a policy. | HQ |
| 2026-11-14 | Sat | Inbox watch; answer sub questions by email. | HQ |
| 2026-11-15 | Sun | Inbox watch. | HQ |
| 2026-11-16 | Mon | **12:00 MT sub pricing cutoff.** No price: NO-BID logged in README, `bids/_pipeline.md`, pipeline.json; board line 7. Price in: HQ checks it against the `private/` worksheet and the WD floor, applies markup in `private/`, fills Attachment 2 in `private/`, fills every `[SUB]` field. **LUKE: SAM login check of NAICS 561720 and the EFT record, by 12:00** (portal login). | HQ / LUKE |
| 2026-11-17 | Tue | Last day to request an additional wage determination (RFQ p.6, "two calendar days before solicitation close"); not needed. HQ emails Luke the complete draft PDF + Attachment 2 for approval, with the SF-1449 and Attachment 7 pages marked for signature. HQ defaults (RESPONSE-DRAFT notes) stand unless Luke overrules by 17:00 MT. Chase any missing sub document by email. | HQ -> LUKE |
| 2026-11-18 | Wed | **LUKE: sign SF-1449 block 30, Attachment 7 certification and any SF-30; scan back by 12:00 MT.** HQ assembles the final PDF, confirms no marker is left, re-checks SAM for amendments, emails Luke the final by 15:00 MT. **LUKE: send the quote to stephen.holly@usda.gov (or tell HQ in writing to send) by 18:00 MT**, a day early so a bounce or size problem can be fixed. | LUKE / HQ |
| 2026-11-19 | Thu | **DUE 10:00 MT.** 07:00 MT: last amendment check. 08:00 MT: confirm the message is in Sent with both attachments and no bounce; if it bounced, resend at once. Record the Gmail message id and the CO's receipt reply in the README log. | HQ / LUKE |

After the deadline: award date not stated in the solicitation; prices held through 2027-02-17. On award (PWS): Contract
Manager name and contact to the COR within 7 calendar days (8.1); QCP to the CO, work plan to the COR, product list with SDS,
and the HSPD-12 employee list within 10 days (1.6.5, 1.6.6, 1.6.3 / 1.13, 1.11.6); return 1 signed SF-1449 (block 28);
first weekly service Sat 2027-01-02, first daily service Mon 2027-01-04. Monthly IPP invoices with the COR-signed
Inspection Checklist (PWS 5.0). No insurance certificate is required by the solicitation; if the CO asks: [LUKE: COI after
bind].
