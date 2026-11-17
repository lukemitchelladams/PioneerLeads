# SAM.gov no-walk sweep, 2026-11-17

Read-only sweep of the SAM.gov Opportunities API v2 for federal work Brown Bison Holdings LLC can bid as a small
business prime with subs in the field, due 2026-11-20 to 2026-12-11, with no mandatory site visit.
Nothing was emailed or submitted. Every deadline and site-visit line below is quoted from the notice text or the
attached solicitation PDF/DOCX; nothing is from memory.

## How the sweep was run

| pull | filter | records |
|---|---|---|
| A. as specified | posted 10/18-11/17/2026, ptype o,k,p, `state`=CO/NM/WY/UT x 9 NAICS (238220, 238210, 561720, 561730, 561790, 238290, 561210, 811310, 238990) | CO 9, NM 6, WY 0, UT 6 (21) |
| B. same states, all NAICS | `state`=CO/NM/WY/UT, no NAICS filter | CO 98, NM 57, WY 2, UT 67 (224) |
| C. national, 9 NAICS | no state filter, then filtered locally on place of performance | 384 nationally; PoP CO 6, NM 6, UT 2, WY 0 |
| D. national, all NAICS, due in window | `rdlfrom` 11/20/2026 `rdlto` 12/11/2026 | 5,457 nationally; PoP CO 18, NM 15, UT 10, WY 4; blank PoP but office in-state CO 26, UT 21, NM 11, WY 1 |
| E. older postings due in window | posted 07/01-10/17/2026, due in window | 191; 3 tied to UT (all aircraft parts or a large MACC), none relevant |

Unique notices tied to each state (PoP, or office where PoP is blank) across all pulls: **CO 86, NM 59, UT 56,
WY 7** (5,788 unique records pulled in total).

Two API quirks found: the `state` parameter follows the contracting office more than the place of performance
(the CO pull is full of NPS/Reclamation Lakewood-office work in AZ, CA, WA, etc.), and `offset` is a page index,
not a record offset. Pulls C and D catch in-state work bought by out-of-state offices (they found the Zuni NM
cooling tower and the VA Pikes Peak notice that pull A missed). About 4,500 notices in pull D have a blank place of
performance; those were screened on office state, title keywords and park/forest unit names.

## Ranked candidates (best first)

| # | notice id | solicitation number | agency/office | title | place (city, state) | NAICS | set-aside | response deadline (quoted) | site visit (quoted) | scope in one line | attachments | why it fits / risks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 7afe087450dd48268559b2f751b40e4b | 140LL027Q0009 | DOI BLM, Utah State Office (UT952), Salt Lake City | S--BLM Utah - Paria River District HQ Janitorial | Kanab, UT (669 S Hwy 89A) | 561720 | Total Small Business ("SET-ASIDE: SB") | Amd 0001: "Quotes Due: 12:00PM MST on Wednesday, December 9, 2026" | none found (solicitation, Amd 0001, PWS, QASP, schedules and photos all searched) | Janitorial for the District HQ, PWS: "approximately 13,000 square feet"; base year 01/01/2027-12/31/2027 + 4 option years | 9 (Sol, Amd 0001, Bid Schedule, PWS, QASP, Cleaning Schedule, PRS, Inspection Sheet, Photos) | Best fit: recurring 5-year janitorial, core trade, 22 days of runway, no walk. Risks: best-value trade-off where "technical (non-price) factors ... combined, are considered more important than price"; past performance asks for "at least three (3) similar projects performed in remote or rural locations completed within the last three (3) years"; 10-page limit; Kanab is remote, so we need a Kane County / St. George area janitorial sub and a staffing/retention plan (that is the main technical factor). Questions due 11/25 12:00 MST to jsanborn@ios.doi.gov. |
| 2 | e022e329a81747a4b3119b645b6758de | 127EAX27Q0015 | USDA Forest Service, CSA Southwest 7, Albuquerque (Gila NF) | Electrical Upgrades to the GCAFB/Tanker Base/Fire Cache | Hurley, NM (Grant County Airport) | 238210 | Total Small Business | SF1442 block 13a: due "1200 (hour) local time 12/11/2026"; "email only to: Melissa Heckenlaible ... melissa.heckenlaible@usda.gov" | OPTIONAL organized visit: "A site visit will be held on Tuesday, November 24, 2026 ... In no event shall failure to inspect the site constitute grounds for a claim after contract award." / "(a) The Government is planning a pre-proposal conference (site visit), during which potential offerors may obtain a better understanding of the work required." 10:00 AM MT, RSVP 48 h ahead. No "mandatory" wording. | New service pole, electrical service to a concrete pad, and replacement of the retardant-pump motor-control panel; complete "within 21 calendar days" after NTP | 5 (Sol/SF1442, SOW, Schedule of Items, WD NM20260019, Sustainable Products) | Core electrical trade, small job, 24 days of runway, block 12a bonds marked NO. Risks: award to "highest technically rated" quote, with "State licensing, safety plan ... quality control plan" evaluated, so the sub must hold a NM electrical license; SOW 5.7 puts load/fault-current verification on the contractor; remote site (Silver City / Las Cruces sub). Questions due 12/03 12:00 MT. Visit is optional, so per Luke's rule it is declined unless a sub's own person attends. |
| 3 | 7390db3f3afa46d3a8424450ec68c329 | 75H70727Q00003 | HHS Indian Health Service, Albuquerque Area IHS | Fire Door Inspection, Assessment, and Maintenance at the Albuquerque Area IHS | Albuquerque, Mescalero, Santa Fe, Taos, NM (4 health centers) | 561210 | Total Small Business | Amd 0002: "To extend the submission date to Wednesday, November 25, 2026, at 3 PM MS." | OPTIONAL: Sol 6.12 "Interested offerors may coordinate site visits by contacting the following individuals"; notice: "Site visits must be completed by Thursday, November 19, 2026, at 12 PM MS." | NFPA 80/101 inspection and inventory of all fire/smoke door assemblies, assessment, then repair/replace, all within "90 calendar days after Notice to Proceed" | 27 (Sol, Amd 0001/0002, Appendix A, RFI logs, WDs, door schedules, life-safety plans, lead and asbestos reports, photos) | Facilities maintenance, single award, 8 days of runway. Risks: Amd 0002 says "payment bond will be required" and the RFI log says "Yes, a performance bond is required", plus certified payroll; lead inspectors must hold "Intertek Qualified Personnel (IQP)" or "DHI ... (FDAI)"; four sites spread across NM; lead and asbestos present (lead-safe practices required). Needs a certified fire-door sub fast. |
| 4 | 974f9b5eb51f4ade85b43f47c548e773 | 36C25927Q0048 | VA Network Contract Office 19 (36C259) | Radiant Heating Panel Replacement (RMR VAMC) | Aurora, CO (Rocky Mountain Regional VAMC) | 238220 | Total Small Business ("100% set-aside for Small Businesses") | "Quotes are to be provided to Christopher.Hollingsworth2@va.gov no later than 14:00pm ET, November 20, 2026." (12:00 MT) | none found (notice text, PWS docx, WD and VAAR form searched) | Remove and replace "roughly 238' of radiators" (hydronic radiant panels) at the Colfax, South and North entrances and the employee breezeway | 3 (PWS docx, WD 2015-5419, VAAR 852.219-75 certificate) | Denver-metro plumbing/hydronic job, many local subs, no walk. Risks: only 3 days left and the question period closed 11/13; Volume IV VAAR 852.219-75 limitations-on-subcontracting certificate, which says to "list any/all subcontractors (and their size standard IAW NAICS 238220)", so the sub must be a small business; up to 3 past-performance references. Go only if a hydronic sub can price by 11/19. |
| 5 | f4f30b194c4647159c676c5005dfba09 | 1240LR27Q0002 | USDA Forest Service, CSA Intermountain 6 (Ashley NF) | ANF Duchesne Bunkhouse AC Replacement | Duchesne, UT (250 S 400 W) | 238220 | Total Small Business | "This solicitation closes on November 20th, 2026, at 3:00 PM MST." (Amd 0001) | OPTIONAL: "No formal site visit is scheduled for this requirement. However, offerors may request an individual site visit for visual inspection of the work area." | Replace a 5-ton condenser and coil with a 2.5-ton condenser, new coil and new line set; 60 calendar days | 12 (Sol T&Cs revised, SOW, Schedule of Items, Q&A with photos, WD, Amd 0001, forms) | Small HVAC job, no walk. Risks: 3 days left, questions closed 11/06; the Q&A answers key pricing items with "Please perform site visit to ascertain approx. length" (line set) and "Please attend site visit to view electrical service information", so the price carries an allowance; Duchesne is about 2.5 h east of Salt Lake City. |
| 6 | 5ba7eaeb505c4db79656512be7538248 | 140RR027R0010 | DOI Reclamation (Provo Area Office buy, Denver contracting) | 56--PGMB Security Gate | Pleasant Grove, UT (Pleasant Grove Office) | 238990 | Total Small Business | "Quotes remain due on November 23, 2026, at 2:00 PM MST." | Held 10/26, not mandatory: "A site visit is scheduled for Monday, October 26, 2026, at 10:00 AM (MS). ... Attendance is not mandatory but is recommended." Amd 4: "At this time, the Government does not plan to schedule additional site visits." | Furnish and install an automated vehicle gate (about 25 ft) plus about 15 ft chain-link infill, integrate with existing card readers and exit loop, and add emergency key switches to 2 existing gates | 10 (combined synopsis + 3 revisions, SF30 Amds 1-4, Q&A, WD) | Electrical/low-voltage integration on a gate job; 6 days left. Risks: outside our core trades (needs a gate-operator/fence sub); supply-and-install. Lower priority. |
| 7 | c9a23b98a6c444779c58a615348ac337 | 140PP027Q0019 | DOI NPS, CONOPS Central | W--Portable Toilet Services - ZION National Park | Springdale, UT (Zion NP) | 562991 | Total Small Business | "Quotes are due by 10 December 2026 @ 12PM MT" (Amd 0002) | Held 11/12, not mandatory: "A site visit has been scheduled for 11/12/2026 at 10AM Mountain Time. If attending, please email the COR" | Rent, place, pump and clean portable toilets in the park; base CY2027 + 4 option years | 11 (Sol, Amds 0001/0002, revised SOW, price schedules, Q&A, WDs, subcontracting worksheet) | Adjacent only (sanitation, not one of our trades). Risks: Q&A says "Subcontractor coverage does not satisfy the requirement ... Insurance is a mandatory requirement", so the prime's own policy is needed and ours is not in force; the SOW wants the supplier's name on every unit. Listed for completeness. |

Common to all of them: these are small-business set-asides, so the limitations-on-subcontracting rule applies
(stated in #4, #5 and #7; for #1, #2, #3 and #6, check the 52.212-5 clause list). Our field subs need to be small
businesses under the notice's NAICS. Insurance is pending (application signed 11/16, no certificate yet), so no
quote should claim coverage.

## Reviewed and excluded

| solicitation | title / place | due | why excluded |
|---|---|---|---|
| 1240LP27Q0008 | Pagosa RD janitorial, CO | 11/19 | already tracked (skip list) |
| 140RR027Q0001 | BGNDRF custodial, Alamogordo NM | 12/04 | already tracked (skip list) |
| 36C78627Q0040 | VA Pikes Peak janitorial, Colorado Springs CO | 12/01 | already tracked; SDVOSB set-aside |
| FA251727SS00 (Peterson sources sought) | - | - | already tracked; not returned by this o/k/p pull |
| 140P1426Q0113 | DINO replace swing arm gates, Jensen UT / Moffat Co CO | 12/01 13:00 MST | metal pipe gate fabrication, not our trade; organized visit held 11/05 |
| 36C25926Q0880_1 | Lightning protection B71N, Sheridan WY | 11/27 | SDVOSB set-aside |
| 36C25926Q0826 | Concrete and civil site repairs, Aurora CO | 11/20 | SDVOSB; civil |
| W519TC-27-R-A014 | EAGLE Ft. Carson CO | 2027-01-04 | 8(a); outside window |
| 75H70727Q00004 | IHS Albuquerque roof assessment/repair | 12/04 | Indian Small Business Economic Enterprise set-aside; roofing |
| 140A2327Q0300 | BIE pest control, NM | 11/20 | Indian Economic Enterprise set-aside |
| 140A2327Q0301 | Elevator inspection & PM | 11/27 | place is Belcourt, ND |
| 127EAT27Q0004 | Airport BAER weed treatment | 11/30 | API says Corona NM, but the SOW is the Cleveland NF, California |
| 127EAW27Q0002 | Solar batteries, Frenchman Work Center | 11/20 | California (WD CA20260007) |
| FA480127Q0006 | Holloman AFB vertical transportation | 11/17 11:17 | due today |
| FA822226Q3345, 70FB8027Q00000005, 117346, 140R4026Q0141 | Hill boiler; Las Vegas NM janitorial; Stove Prairie gate; SLV pumping plant roof | 11/12 to 11/16 | deadline already passed |
| 127EAX26Q0069 | Lookout tower restoration, Santa Fe NF | 11/25 | carpentry restoration, not our trades |
| 1240LT27Q0019, 1240LT27Q0022, 1240LT27Q0032, 140R4026R0025 | parking lot, waterline, well abandonment, canal (CO/UT) | 11/20 to 12/09 | heavy civil/earthwork (rule 8) |
| 1240LT27Q0017, 140PP027Q0014 | picnic tables/bear lockers; septic pump truck | 11/24, 12/01 | supply buys |
| 089495-27-A-0001, 47PB5427R0003, 140DWF27RL001, FA820126R0016 | USPS Denver roof; NNSA Lakewood; Rawlins barracks (presol); Hill MACC V | 11/20 to 12/09 | large construction |
| FA254327Q0003 | Buckley asbestos survey, Aurora CO | 12/07 | environmental consulting, not our trades |

## Watch list (outside this window)

- **75H70127R00002**, IHS Zuni Comprehensive Community Health Center cooling tower repair by replacement, Zuni NM,
  NAICS 238220, Total Small Business. A presolicitation; the API response date is 2027-01-05. Strong HVAC fit; watch
  for the RFP and its site-visit terms.
- Dad's company (bearings): **140RR027Q0034** "FOP Kingsbury Bearing Pump Repair", Reclamation, combined
  synopsis, API deadline 2026-11-19 10:00 PT, no set-aside listed, place blank. Outside this task's window and
  states; documents not pulled.

## Not read / limits

- IHS fire door (#3): 9 attachments are image-only PDFs (door schedules, life-safety and special-systems drawings,
  door photos) with no text layer. Site-visit terms come from the text solicitation, Amd 0002 and the notice, not
  from those drawings.
- Duchesne (#5): the Equipment List and Biobased Product List PDFs have almost no extractable text (forms).
- Notices with a blank place of performance were screened on title, office and unit names only. The descriptions
  of the about 4,500 blank-PoP notices nationwide were not read, so in-state work behind a generic title could be
  missed.
- Only notice types o, k and p were pulled. Sources-sought (r) and special notices were not.
