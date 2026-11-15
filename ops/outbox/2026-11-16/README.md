# Mon 2026-11-16 08:30 MT chase batch (worker draft + HQ additions 2026-11-15 20:5xZ, nothing sent)

Four bids have a Mon 11/16 12:00 MT sub gate and no yes yet; HQ added four more sends (rows 5-8) on 2026-11-15, all second touches or open questions, manifest `outbox-chases.json` now 8 entries. Bodies below pass `python3 scripts/humanize_gate.py check` (body ends at the
closer; gmail_api.py adds the signature). HQ builds the manifest from its own sent records (named mailboxes stay out of tracked files),
skips any firm that has replied or declined by then, and respects each firm's touch count. Reply in the original thread where one exists.

| Body | Bid | Original sends to chase (thread / msg ids) | Skip |
|---|---|---|---|
| chase-cpw.txt | CPW DQ1-PMAA-2027000176 (Alamosa heater) | electrical bcc 1a1d66c90745e1e0 (delivered: Vemco, Power Pro, C-Squared, Billings); B tier 1a1d699c3400df4e; Torres 1a1d66c96ac41789; Surefire 1a1d5a2835ac51db; Flow Right 1a1d5a289f443c61 | Husmann (declined); Valley Electric, Royal (dead addresses) |
| chase-bgndrf.txt | Reclamation RFQ 140RR027Q0001 (Alamogordo custodial) | 1a1d6d8ae5a21e18 (delivered: SL Cleaning, Pristine, Chase N Dirt, L&L, Alamo); B tier 1a1d708c7a8ea2ad; Tigua retry 1a1d708ce49026c8 | K Clean (dead domain); Alamo Janitorial (permanently closed, 2026-11-14 reply 1a1dae7283ac34f3) |
| chase-pagosa.txt | USFS RFQ 1240LP27Q0008 (Pagosa janitorial) | 1a1ccfdb5b42ad67 (sweep group); 1a1ccfdadfba4085 (CRC, Evergreen) | B&K (declined); Tidy Team (DO NOT CONTACT) |
| chase-canon-hvac.txt | Canon City RFP 129-26 (boiler/chiller PM) | Friday backups bcc 1a1d5a25a31dfb5a (Haynes, Colorado Mechanical Systems); RFP 129-26 attached again | ACCO, Air Conditioning Plus, Rasmussen, Nielsen (touch limit 11/06 + 11/09); Tolin (said yes 11/13, pricing promised Mon/Tue: no chase until Wed); H2GS (declined) |
| chase-lafayette-cc.txt | Lafayette RFP-26-33-FM (citywide custodial) | reply in thread 1a1b38552d6f701a to Clean Conscience (shared mailbox, so "Hi Team"): Natalie signs in Thu 11/19 10:00 as Brown Bison Holdings LLC + photo of the sheet | KG, Teebs, CleanPro (touch limit 11/07 + 11/09); Kleen-Tech (incumbent, pricing by 12/07, no chase) |
| hoodz-ahj.txt | PSD IFB 27-701-002 (kitchen hoods) | reply in thread 1a1a878f8cda76a3 to Larry Moss cc Carlos Ahedo: the one open AHJ-registration question (PFA / LFRA / Wellington) | pricing-sheet answers (thread 1a1d0111ba12e68a) are due Mon anyway: not chased the same day |
| chase-psd-alternates.txt | PSD IFB 27-701-002 (kitchen hoods) | 11/12 bcc 1a1d17a710e4b459 (Aqua Strong, Elite, Brotherhood), answers were asked by Mon 11/16 | nobody |
| chase-bvcc.txt | CDOC DQ27-0132 (BVCC boiler chemicals) | tier 3 1a1d5a24d06ac325 (RK Water, Chem-Aqua, ISI); Hydrite + WEI 1a1d17a67fa91fb1 | TRS, Aqua-Chem (touch limit); H2GS, Summit, Reaction Eng. (declined) |

Facts used, all from the bid files: CPW pre-bid "Nov 18, 2026 10:00 AM MST", registration "Nov 17, 2026 5:00 PM MST" (DQ); BGNDRF monthly
price asked by 2026-11-25 in the 11/13 ask; Pagosa quotes due "11/19/2026 1000 MT" (SF-1449 block 8); BVCC "10:00am, Wednesday, November 18,
2026" mandatory, Exhibit G + photo ID per attendee (DQ sec. 4; README says by Mon 11/16).

Facts for rows 5-8, from the bid files: Canon City RFP 129-26 due Mon 12/07 11:00, pricing asked by Mon 11/30 (sub-outreach.md); Lafayette
mandatory pre-proposal "Thursday, November 19, 2026 | 10:00AM / Lafayette City Hall, Council Chambers / 1290 S. Public Rd" (RFP sec. 1),
pricing by 12/07; PSD IFB 27-701-002 due Fri 11/20 14:00 MST, 7.1 certification statement and 3.1 AHJ proof "before the first service"
(FORMS-CHECKLIST.md). Not chased: Lafayette KG/Teebs/CleanPro and Canon City ACCO/ACP/Rasmussen/Nielsen (both groups at two unanswered
touches), Tolin (yes in hand), Kleen-Tech (pricing 12/07). Replies checked 2026-11-15 20:4xZ: none from Haynes, Colorado Mechanical,
Clean Conscience (since 11/11), Aqua Strong, Elite or Brotherhood.

## Second manifest: `outbox-psfb.json` (HQ, 2026-11-15 21:4xZ, nothing sent)
Peterson SFB sources sought FA251727SS00 (Smart T Power): `psfb-response.txt` + the two-page response PDF (private/, dated 2026-11-16) to
William Bailey and Stephen Carr at 21 CONS/PKA, the two addresses the 10 November memo names. Due "no later than 18 November 2026 @ 09:00
A.M. Mountain Time" by email only (memo p.1). Approval copy went to Luke 2026-11-11 (msg 1a1cb4611365ef40); his overrule window closes Mon
11/16 12:00 MT; HQ sends that afternoon (`python3 scripts/send_outbox.py ops/outbox/2026-11-16/outbox-psfb.json`). Gate PASS; the email
body carries no phone, the attachment (a government response document) carries the one the memo's item 6 asks for.
