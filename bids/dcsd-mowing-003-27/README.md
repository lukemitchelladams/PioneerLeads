# Douglas County School District RE-1 — RFP 003-27 Mowing Services, Groups 2, 5, 7 & 8

| Item | Value (quoted from docs/RFP-003-27-Mowing-biddoc.pdf unless noted) |
|------|------|
| **Site walkthrough (sign-in required)** | **"Pre-proposal site walkthrough with James Korth - Grounds Manager — October 14, 2026, 9AM, Mountain Vista High School - 10585 Mountain Vista Ridge, Highlands Ranch". §2.1: "A Proposal from a Respondent that did not sign in at the walkthrough will be rejected as non-responsive." PASSED. Alex attended and signed in as Luke / Brown Bison (Luke, 2026-10-21): requirement met.** |
| **Proposals due** | **"October 23, 2026, at 2:00 PM Mountain Time" via Rocky Mountain e-Purchasing (BidNet).** BidNet's live listing (scan 2026-10-20) shows 10/29/2026 02:00 PM MDT → likely an extension addendum, **not in hand yet**. Treat 10/23 14:00 as controlling until the addendum is read. |
| Questions | Through BidNet; deadline not stated in the §2.0 table. Mowing-area questions: James Korth, jpkorth@dcsdk12.org |
| Scope | Weekly mowing at 3", trimming, monthly edging, cleanup, weed control, monthly native mow, annual spring aeration/fertilization/broadleaf spray; 19 HS/MS sites (Parker, Castle Rock, Highlands Ranch); ~6.58M sq ft turf (agent's sum of the site table) |
| Season / term | ~April to ~end of October; MSA until terminated; ≤3% increase on renewals |
| Insurance | CGL $1M/$2M; auto $1M CSL; WC; DCSD additional insured; A- VII carriers; subs equivalent |
| Other | Background checks (C.R.S. 22-32-109.8); 3 K-12 references 2024-2026; logo T-shirts; subs need DCSD written consent (MSA §7) |
| Evaluation | Price 40, qualifications 20, safety 20, QC 10, technical approach 5, staffing 5 |
| Attachments | A Master Services Agreement (in PDF), B Exceptions Form (in PDF), C Debarment Certification (in PDF). **Pricing schedule: RFP says "Provide pricing in the format required by this RFP" but no price sheet is in the PDF — check BidNet Documents tab + addenda.** |
| Contact | Rich Harley, Technology Procurement Strategist, rharley@dcsdk12.org |
| Performer | Brown Bison submits and holds the contract. Field work: **AWalk LLC d/b/a YMS Landscaping** (Colorado LLC 20241544949, formed 2024-05-21, good standing; 115 Wilcox St #220, Castle Rock; President & CEO Aaron Walker; our contact Alex Ditto, Commercial Accounts Manager, alex@ymslandscaping.com). Price = YMS's 10/19 revised sheet + 5%. |
| Status | **GO.** Walkthrough sign-in confirmed 2026-10-21. Final District price sheet built from YMS's 10/19 sheet + 5% (`submission/build_price_sheet.py`; figures only in `private/`). Sent to Alex 2026-10-20 11:54 MT with the scoring breakdown and 10 asks, answers due **Wed 10/21 5 PM**. |

## Open items from YMS (asked 2026-10-20, due Wed 10/21 5 PM)
1. **Walkthrough sign-in:** which company name Alex wrote on the 10/14 sheet, plus a photo. §2.1 rejects a Respondent that did not sign in.
2. **Pesticide license:** the Department of Agriculture's business-license search shows nothing for YMS or AWalk (research agent, 2026-10-20).
   Alex's sheet names Adam Perrigoue, license 34548. Need: who applies, under which business license, Turf category (206). A separate
   spraying company would need DCSD's written consent (MSA §7), and the proposal must say a licensed firm makes every application.
3. Signer for AWalk LLC (Aaron Walker?).
4. Safety: written program, experience-mod letter or "unrated", OSHA 300A summaries 2023-2025, products with EPA numbers and SDS,
   OK to add a CBI fingerprint check and a national sex-offender registry search on top of Checkr.
5. QC: crew software (time and photo stamps, weekly report); commit to a 2-business-hour acknowledgment and a 24-hour fix.
6. References 2-3 (address, phone, work, years); the 2-3 largest contracts of the last 3 years; one line of company history
   (the website says 2006; the LLC dates from 2024).
7. Resumes for Alex, Greg Hitchcock, Luis Chavez and Garrett Sission; headcount, trucks and trailers; mower years; rental backup.
8. Saturday route (Castle View, Castle Rock MS, Douglas County HS, Mesa) vs heavy weekend field use (Q&A 1, Q4).
9. Which phone (805-551-0539 or 719-748-6562) and which address go in the proposal.
10. Insurance at award: DCSD (officers, directors, Board, employees) and Brown Bison as additional insureds, primary and non-contributory, auto waiver of subrogation.

## Price-sheet mapping (no figures here; see private/)
- YMS's weekly price per site = a per-acre turf rate (lower on the six largest campuses), a flat weekly site charge (all sites but VALE),
  and a per-square-foot bed rate. Beds go to the District's rock and mulch columns by the District's own square footage; the turf rate plus
  the site charge goes to turf.
- Edging (monthly) and the one-time aeration, fertilization and broadleaf have no column on the District form. They are inside each site's
  seasonal total, broken out on the "Site Services Detail" sheet, and explained in a note under Grand Totals.
- Additional mows are priced per school, outside the total (Q&A 1, Q11), with YMS's unit rates + 5% on "Additional Pricing".
- The season basis is 27 weeks. Q&A 1, Q9 says this season ran 29. The sheet note bills added weeks at each site's weekly prices.

## Sends log
- 2026-10-20 11:54 MT: reply to Alex's 10/19 email: changes accepted, final price, scoring, 10 asks (figures only in private/).
  The attached price sheet already included Brown Bison's 5%. Its bytes could not be verified afterwards (see memory 2026-10-20).
- 2026-10-20 12:32 MT: bid package for Alex's sign-off, per Luke: one Word file, `private/DRAFT for YMS review - DCSD 003-27 Proposal
  (your prices).docx`, built by `submission/build_proposal.py --draft --for-sub`. It holds the full proposal with YMS's own prices
  (no markup) in Section 5, plus Appendix A (safety), B (quality control) and C (crews and route). The email carries 5 short safety/QC
  suggestions. Sent as a Gmail draft first; the attachment was checked byte-identical (sha256 089a85bd…) before and after sending.
  Asked for "approved" or changes, plus the sign-in name, by **Wed 10/21 5 PM**.

## 2026-10-21 (MAIN): YMS asks cut from 10 to 3 (Luke: "10 questions seems like a lot")
Filled ourselves from Alex's sheet and public records: Alex's address (AWalk LLC, SOS) and phone ((719) 748-6562, his
email signature), company history, credentials, short resumes, reference work descriptions, Castle Rock Water address
(175 Kellogg Ct, Castle Rock 80109, Town contact page), EMR (on request), QC app (dropped), trucks (one per crew),
native mowing equipment, rental source, Saturday sites (only with no games/events, else Friday after dismissal).
Third contracts row dropped. build_proposal.py now dates the cover letter at build time and accepts our green wording.
**Still needed from Alex (5 open blanks):** (1) OK on his prices; (2) who does the spraying + Colorado Dept of
Agriculture business license number (none found for YMS/AWalk); (3) Mountain Shadow HOA address and Patricia Tolini's
phone (RFP 8.4 requires both). Addenda acknowledged: Q&A Document 1; check BidNet for any later addendum before upload.
- 2026-10-21 ~12:15 MT: email to Alex (Luke's OK), reply in the 10/20 package thread: District scoring (RFP 13.2: price 40,
  qualifications 20, safety 20, QC 10, technical 5, staffing 5), the safety and QC commitments written under YMS's name
  for him to confirm, and 5 asks (prices OK, commitments OK, spraying license, Mountain Shadow HOA address/phone, 2-3
  biggest or public contracts). Gmail 1a15fa8b7a107e9c.
- 2026-10-21 ~12:20 MT: follow-up with "why we're asking" (strongest bid; 60 of 100 points are not price) and a Word
  fill-in sheet (private/DCSD 003-27 - YMS fill-in sheet.docx; attachment verified byte-identical in the draft before
  sending). Gmail 1a15fb5215046788. Answers requested by 5 PM today.

