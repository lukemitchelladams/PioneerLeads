# Town of Parker RFP 26-021-1 Generator Maintenance & Repair Services: submittal checklist

Prepared 2026-11-05. Due **Fri 2026-11-06 14:00 MT** (RFP §1.2: "November 6, 2026 @ 2:00pm"; BidNet reminder 2026-11-05: "Closing Date: 11/06/2026 02:00 PM MST").
Bidder and contract holder: **Brown Bison Holdings LLC**. Field work: **Colorado Standby** (Brad Orgill, 719-624-8100) as our subcontractor.
No prices, rates, markups or sub costs in this file or anywhere in this public repo. Filled pricing lives in `bids/parker-generator-maintenance/private/` (git-ignored).

## READ FIRST: the Town's pricing sheet is NOT in docs/

- `docs/` holds only the 8-page RFP PDF (downloaded from GovTribe 2026-10-20). `docs/MANIFEST.md` lists no attachments.
- RFP §7 says: "Complete all applicable fields in attached pricing sheets & proposal forms." Those sheets are **not in docs/**.
- They ARE in Luke's sent mail. The 2026-10-30 09:10 MT email to Brad Orgill (Gmail message `1a18d5cc8082418f`, thread `1a17912791bd5d12`) carries two attachments:
  1. `RFP 26-021-1 Town of Parker Generator Maintenance - Revised.pdf` (sha256 `e21c1dcf…5008583`, byte-identical to the docs/ PDF: no text change despite the "Revised" name).
  2. `Town of Parker Generator Maintenance Services Price Sheet _ Forms - Revised.xlsx` (4 sheets: Instructions, Scheduled Services, Labor & Charges, Proposal Forms). Structure is mapped in `pricing-map.md`.
- To put them in docs/ (worktree-safe, read-only mailbox use): `python3 scripts/gmail_api.py save 1a18d5cc8082418f bids/parker-generator-maintenance/docs/` then `python3 scripts/doc_manifest.py parker-generator`.
- Still unknown: whether Bonfire lists 26-021-1 at all (the Town's Bonfire open-opportunities feed captured 2026-10-20 showed 26-018, 26-020, 26-027 and 26-028 only), whether Bonfire has required text fields or acknowledgements for this RFP (26-028 did: cover sheet 7.1.1-7.1.4, acknowledgements 8.1.1-8.1.2), and whether any addendum has been issued. Luke checks both portals with his logins before upload.

## Status legend

IN HAND = we have it. BB WRITES = Brown Bison (agent) drafts it. CS SUPPLIES = Colorado Standby must send it. LUKE SIGNS = only Luke can sign or submit it. LUKE DECIDES = a choice only Luke can make. DOWNLOAD = get it from BidNet 0000440494 or Bonfire (parkeronline.bonfirehub.com) with Luke's login.

## A. Submission mechanics

| # | Item | RFP wording (quoted) | Section | Status |
|---|---|---|---|---|
| A1 | Upload to BOTH portals | "Submit proposals electronically through the Rocky Mountain E-Purchasing System and Bonfire before the date and time stated in the official posting." | §1.3 | LUKE SIGNS (uploads). BidNet 0000440494 is live. Bonfire listing unconfirmed: check; if a 26-021-1 project exists there, upload there too. |
| A2 | No email, no late | "Late submissions, emailed proposals, or submissions delivered by another method may be rejected unless the official posting expressly permits them." | §1.3 | LUKE SIGNS. Target upload complete by 12:00 MT Friday. |
| A3 | Confirm upload | "Offerors are responsible for confirming successful upload of all proposal files before the deadline." | §1.3 | LUKE SIGNS. Save the portal receipt to docs/. |
| A4 | Pricing validity | "Proposal pricing shall remain valid for at least 120 calendar days after the proposal deadline unless the official posting states otherwise." | §1.3 | BB WRITES (statement in the cover letter and on the pricing assumptions page). |
| A5 | Addenda check | "Only written addenda issued through the official procurement process modify this RFP." / "the latest written addendum issued by the Town controls." | §8; §1.2 | DOWNLOAD. None in hand as of 2026-11-05. Check BidNet and Bonfire Friday morning. |
| A6 | Searchable, concise, in order | "proposals should be concise, searchable, and organized in the following order" | §1.4 | BB WRITES. One text PDF (not scanned images) in the §1.4 order below, plus the Excel workbook. |
| A7 | Portal form fields, if any | Not in the RFP PDF. Bonfire RFP 26-028 required cover-sheet text fields and Yes/No acknowledgements. | n/a | DOWNLOAD / LUKE SIGNS. Unknown for 26-021-1 until Luke opens the Bonfire project (if it exists). |

## B. Proposal contents in the §1.4 order

| # | Item | RFP wording (quoted) | Section | Status |
|---|---|---|---|---|
| B1 | Cover letter | "Cover letter signed by an authorized representative, including legal company name, address, primary contact, email, and telephone number." | §1.4 item 1 | BB WRITES (draft in `technical-proposal-draft.md` §1). **LUKE SIGNS.** Luke's title to confirm (recent emails say "Operations Manager"; memory says Owner). |
| B2 | Executive summary | "Executive summary and acknowledgment of all addenda." | §1.4 item 2 | BB WRITES. Addenda list filled at assembly (A5). |
| B3 | Technical response to the Scope | "Technical response to the Scope of Services and the eight Vendor Response Questions in Section 5." | §1.4 item 3; §4 | BB WRITES (draft §3.1). CS SUPPLIES: load-bank capacity and procedure, lab name and turnaround, consumables basis, warranty period. |
| B4 | Eight Vendor Response Questions, in order, labeled | "Respond to each question in the order presented. Restate the question or clearly label each response by question number. Cross-references shall identify the exact proposal section and page. 'See website' responses are not sufficient." | §5 | BB WRITES (draft §3.2). CS SUPPLIES Q1 references, Q2 technicians, Q5 response time, Q7 sample report. LUKE DECIDES Q8 exceptions. |
| B5 | Team, certifications, authorizations, coverage | "Project team, technician qualifications, certifications, manufacturer authorizations, and local service coverage." | §1.4 item 4 | BB WRITES (draft §4). **CS SUPPLIES** technician names/qualifications, certifications, factory training or authorization by brand (Onan/Cummins, Kohler, Detroit, MTU/Rolls-Royce), dispatch location and drive time to Parker. |
| B6 | Implementation plan, inventory timeline, PM schedule | "Implementation plan, initial inventory timeline, and proposed preventive maintenance schedule." / inventory "within 30 calendar days after the notice to proceed" / "a coordinated annual schedule covering every generator and transfer switch ... planned month, scope, estimated outage or test duration, staffing, and coordination needs for each site." | §1.4 item 5; §4.2; §4.3 | BB WRITES (draft §5). CS SUPPLIES proposed months, outage/test durations, crew size per visit. |
| B7 | Emergency response plan + guaranteed times | "Emergency response plan and guaranteed response times." / "The contractor shall state and honor a guaranteed response time, prioritize critical public safety facilities, and dispatch qualified personnel with appropriate diagnostic equipment." | §1.4 item 6; §4.9 | BB WRITES (draft §6). **CS SUPPLIES** the guaranteed on-site time, the 24/7 number, staffing and escalation names. LUKE DECIDES the number we guarantee to the Town. |
| B8 | Sample completed service report | "Sample completed inspection and service report." / Q7: "Provide a sample completed service report and state the report turnaround time." | §1.4 item 7; §5 Q7 | **CS SUPPLIES** (a real completed report, client data redacted). BB checks it against §4.10 content list (draft §7). |
| B9 | Pricing schedules + assumptions/exclusions | "Completed pricing schedules in Section 7, including all assumptions and exclusions." / "Complete all applicable fields in attached pricing sheets & proposal forms" | §1.4 item 8; §7 | Workbook IN HAND (sent mail, see top). **CS SUPPLIES** items 1-7 of Luke's 10/26 ask. **LUKE DECIDES** markup, renewal method, inventory treatment, subcontractor-markup line. BB fills the workbook in private/ and writes the assumptions page (draft §8). |
| B10 | References | "References and required disclosures, exceptions, licenses, insurance evidence, and safety information." / workbook: "Provide at least three references for current or recently completed comparable municipal or commercial standby generator and transfer-switch service contracts." | §1.4 item 9; §5 Q1; workbook Proposal Forms | **CS SUPPLIES** three references with client/contact, email/phone, locations and equipment, scope, contract dates. Shown as Colorado Standby's work, never as Brown Bison's. |
| B11 | Required disclosures | "Offerors shall disclose actual or potential conflicts of interest" / "Offerors shall clearly identify information claimed confidential and provide the legal basis for the claim." | §8 | BB WRITES (draft §9). LUKE DECIDES: conflicts (expected none), confidential claim (recommend none). |
| B12 | Subcontracting approval request | "The selected contractor may not assign the agreement or subcontract material responsibilities without prior written Town approval." | §8 | BB WRITES (cover letter and §9 name Colorado Standby and ask for approval). CS SUPPLIES written confirmation it is not proposing on 26-021-1 itself (§8 collusion certification: "independently prepared without collusion, fraud, or improper coordination with another offeror"). |
| B13 | Exceptions | "Identify any exceptions to the scope of work or contract requirements." | §5 Q8; §1.4 item 9 | LUKE DECIDES. Recommend "No exceptions" plus stated assumptions. |
| B14 | Licenses | "licenses" (item 9); contractor provides "permits, licenses" (§2.3) | §1.4 item 9; §2.3 | BB WRITES: Colorado SOS good standing for Brown Bison (SOS ID 20261543928). CS SUPPLIES its licenses and certificates. Town business license is an award-time item in the Town's standard agreement (sample PSA attached to RFP 26-028, §12); not required with this proposal. |
| B15 | Insurance evidence | "insurance evidence" (item 9); "Before commencing work, the selected contractor shall provide certificates of insurance and endorsements meeting the Town's then-current requirements" | §1.4 item 9; §2.4 | LUKE DECIDES what to attach: Brown Bison policy binds 2026-11-13 (memory 2026-11-05), so a broker binder/letter from Trucordia is the "evidence" now. CS SUPPLIES its COI. Limits are not in this RFP; the Town's standard Exhibit C (sample PSA from RFP 26-028) is quoted in the draft §9 as the best indicator. |
| B16 | Safety information | "safety information" (item 9); "safety controls, and incident reporting" (§2.3) | §1.4 item 9; §2.3 | BB WRITES site rules (draft §9). CS SUPPLIES its safety program summary and incident-reporting practice. |
| B17 | Warranty period | "The contractor shall warrant parts and workmanship for the period stated in its proposal" | §4.11 | CS SUPPLIES its warranty period. LUKE DECIDES what Brown Bison states. |
| B18 | Report turnaround commitment | "within five business days after each scheduled visit or test, and within one business day after an emergency call" | §4.10 | BB WRITES (commit to the RFP numbers). |
| B19 | Consumables basis | "Routine service consumables shall be included as identified in the accepted pricing" | §4.8 | CS SUPPLIES what its PM price includes. BB states it on the assumptions page. |
| B20 | Background screening acceptance | "Personnel assigned to secure or sensitive facilities may be subject to access controls, identification requirements, escorts, or background screening established by the Town." | §2.4 | CS SUPPLIES confirmation its technicians will submit to Town screening (Police Department). BB states it in §4. |

## C. Workbook: "Town of Parker Generator Maintenance Services Price Sheet _ Forms - Revised.xlsx"

| # | Sheet / cells | Town wording (quoted) | Status |
|---|---|---|---|
| C1 | Scheduled Services C4:E9 | "Enter proposed annual pricing in the yellow cells on the Scheduled Services sheet." / "For facilities with more than one unit, enter the combined facility price for all listed units." | CS SUPPLIES items 1-4. LUKE sets markup. BB fills in private/. |
| C2 | Labor & Charges B5:F8 | "Enter labor rates, minimum charges, markups, fees, and pricing-adjustment terms on the Labor & Charges sheet." | CS SUPPLIES item 6. LUKE sets markup. |
| C3 | Labor & Charges B12:B18 | "Enter N/A or $0.00 when a charge does not apply; do not leave required fields unexplained." | CS SUPPLIES item 7 (parts) and any call-out/freight/disposal terms. LUKE DECIDES subcontractor-markup line and annual adjustment method. |
| C4 | Proposal Forms A5:C9 (subcontractors) | "Proposed Subcontractors: Firm / Work to Be Performed / Qualifications / Authorization" | BB WRITES the Colorado Standby row. CS SUPPLIES item 9 (authorizations). |
| C5 | Proposal Forms A12:E17 (references) | "Provide at least three references for current or recently completed comparable municipal or commercial standby generator and transfer-switch service contracts." | CS SUPPLIES item 10. |
| C6 | File name | Not stated for 26-021-1. RFP 26-028 asked "include company name in file name". | BB: name it `Brown Bison Holdings - Town of Parker Generator Maintenance Services Price Sheet & Forms.xlsx`. |

## D. What Luke must sign or do himself (summary)

1. Sign the cover letter (B1) and confirm his title.
2. Decide exceptions (B13), conflicts/confidentiality statements (B11), warranty statement (B17).
3. Set markup and the pricing decisions in `pricing-map.md` (B9, C3): work in private/.
4. Attach insurance evidence (B15): broker letter or binder; policy binds 2026-11-13.
5. Check BidNet and Bonfire for addenda and for a Bonfire 26-021-1 project (A5, A1); complete any portal fields (A7).
6. Upload the PDF and the workbook to BidNet 0000440494 (and Bonfire if listed) and save the receipts (A1-A3).

## E. Colorado Standby must send (Luke's ten items of 2026-10-26, plus what the RFP adds)

Items 1-10 as emailed: PM per unit (PD quarterly), ATS per switch, load bank per unit, oil/coolant per sample, initial inventory, labor rates and call-out, parts pricing, guaranteed response time, factory training/authorizations, three references + sample report + COI.
RFP adds: technician names and qualifications (§5 Q2), dispatch location and 24/7 number (§4.9), warranty period (§4.11), lab name and turnaround (§4.7), load-bank capacity for the 750 kW unit (§4.6), consumables included in PM (§4.8), proposed months and durations (§4.3), safety program (§1.4 item 9), screening acceptance (§2.4), written confirmation it is not proposing directly (§8), licenses (§1.4 item 9).

Ambiguities found in the RFP and workbook: see the final section of `technical-proposal-draft.md`.
