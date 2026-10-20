# Document packages: verified by hand 2026-10-19 20:10 MT, Littleton updated 2026-10-19 22:30 MT (CLAUDE.md rule 0c)

Checked each solicitation's attachment list / table of contents line by line against the files in
bids/<bid>/docs/, and against the PDF pages (an exhibit printed inside the main PDF counts as in hand).
Every MISSING item below lives only on the agency portal, which this cloud session cannot reach.

| Bid | Due | In hand | MISSING (download from) |
|---|---|---|---|
| Littleton RFQ 2126 (BidNet sol 21-26) on-call plumbing | 2026-10-28 14:00 | RFQ (12 pp); **Attachment A Contract Certification Form; Attachment B Sample Contract (18 pp); Attachment C RMEPS Bid Question Response Guide — all downloaded logged in 2026-10-20**; pricing = 6 RMEPS line items (Pricing-Items-RMEPS.md; there is no separate template file) | Q&A posting 10/21 (BidNet Q & A tab; the scanner re-checks it hourly) |
| Town of Parker RFP 26-028 HVAC PM | 2026-10-22 15:00 | RFP; Price Sheet workbook; Appendix A asset inventory; sample PSA incl. Exhibits A Scope, B Rate Sheet, C Insurance Requirements, D COI | Nothing listed is missing. Check the Euna portal for a Q&A addendum (questions closed 10/16). |
| RTD 126DM016 bus shelters | 2026-11-16 14:00 | RFP; Attachment A SOW; Attachment B Form of Contract; Attachment C Pricing Sheet; **SBE Required Enclosures + SBE Contract Requirements (downloaded 2026-10-20, public rtd-denver.com links)** | **W-9 (02.12_W9_updated_1822.pdf) and Key_Personnel.docx** (OpenGov portal, section 7.1.12-7.1.13; Cloudflare-blocked from cloud) |
| Brighton RFP 26-500209-MV2 as-needed GC | 2026-11-09 14:00 | RFP (10 pp); **downloaded logged in 2026-10-20: Required Solicitation Documents (Subcontractor & Material Supplier List, Qualification Statement, DBE Self-Certification, Affidavit of Residency, acknowledgement), Fee Schedule.xlsx, Addendum 1 (Q&A; MUST be acknowledged), Questions and Answers, Sample MPA Services Contract, Solicitation General Terms 2026** | Generative AI Usage Disclosure not found as a separate file: check whether it is in the RFP or Required Solicitation Documents before submitting |
| Adams County IFB-2026.766 street lights | 2026-11-12 15:00 | IFB (30 pp) incl. bid form and Appendix A sample agreement | **Exhibits B and C to the sample agreement**: BidNet lists only the IFB PDF (checked logged in 2026-10-20), so they are not posted. Ask Joe Lachermeier (jlachermeier@adcogov.org) via the BidNet Q&A or at the 10/21 walk |
| Metro Water RFP B26019 switchgear | 2026-11-12 14:00 | RFP (15 pp); **Attachment 1 Scope of Services, Attachment 2 Price Proposal (.xlsx, pricing goes here), Attachment 3 Sample Metro Agreement: downloaded logged in 2026-10-20** | Nothing listed is missing |
| Westminster PS RFP 26-002 facility improvements | 2026-12-01 14:00 | RFP incl. Attachments A-D; **Attachment E General Conditions, Attachments F-1..F-6 Drawings, G-1..G-6 Specifications (6 packages): downloaded logged in 2026-10-20** | Nothing listed is missing |
| Colorado Springs R26-077MZ parks on-call | 2026-10-20 14:00 | RFP (99 pp) incl. Appendices A-E text, Exhibits 1-4 | **Appendix A Specialty Submission EXCEL file** (Luke downloaded it on BidNet; not in repo) |
| Thornton RFP 324-26 on-call landscape | 2026-10-28 15:00 | RFP incl. Exhibits 1-3 and A-G | Nothing listed is missing. Check BidNet for addenda. |
| 27J 2021BRRHS speaker cabling | 2026-10-28 10:00 | Bid doc incl. Exhibit A drawings, B spec sheet, C install manual | Nothing listed is missing. Addenda are emailed to vendors who notify intent to bid (emorales@sd27j.net). |
| Arapahoe RFP 26-52 turfgrass | 2026-11-04 14:00 | RFP incl. Appendix A sample agreement, submittal forms | Appears complete; mandatory Teams meeting 10/19 decides whether we bid. |

## Live download attempt 2026-10-20 (cloud scanner session, full network, NO portal logins set)

- BidNet / RMEPS public detail pages show only location, publication date and closing date/time. Issuing
  organization, solicitation #, description, **Bid Documents** and buyer contact all read "Locked:
  Registered members only". BIDNET_USER/BIDNET_PASS are not set in this environment, so **no BidNet
  attachment could be downloaded**: Littleton Attachments A/B/C + pricing template + Q&A, Brighton forms,
  Adams Exhibits B/C, Metro Water Attachments 1-3, Westminster Attachments E/F/G, Colorado Springs Appendix A
  Excel all still need a logged-in BidNet download.
- GovTribe file search for these bids returns only the main "biddoc.pdf" already in hand; no attachments.
- RTD: SBE Required Enclosures and SBE Contract Requirements downloaded (public). W-9 and Key Personnel
  forms are inside OpenGov, which serves a Cloudflare bot challenge to this network.
- Euna/Bonfire (Parker) opportunity pages serve the same Cloudflare challenge; Parker's list is readable.

## 2026-10-20 04:26 UTC: first logged-in BidNet pull
Logged in to BidNet from the cloud scanner (no device code requested). Littleton's Documents & Items tab
lists exactly four files; all four are now in bids/littleton-on-call-plumbing/docs/ (the RFQ was identical to
the copy in hand). The "pricing template" is the RMEPS Items list (6 lines), copied to Pricing-Items-RMEPS.md.

## 2026-10-20 04:47 UTC: first hourly logged-in scan
BidNet logged in (saved session reused); documents for 15 watched bids downloaded to bids/_watch/downloads/bidnet/<id>/
and copied into the bid folders that exist: Brighton (6 files incl. Addendum 1 + city forms + Fee Schedule), Metro Water
(Attachments 1-3), Westminster (E, F-1..6, G-1..6). Thornton and Littleton already complete; Adams Exhibits B/C are not
posted on BidNet. Other watched (CRM-tracked) bids keep their files in bids/_watch/downloads/bidnet/<id>/.
