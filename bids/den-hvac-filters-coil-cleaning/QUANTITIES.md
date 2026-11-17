# DEN RFP DEN-2026-020-10021: quantities (counts only, no prices)

Sources: `docs/Appendix III of Scope of Work - HVAC Assets_ Locations_ and filter Types.xlsx` (Appendix III),
`docs/Attachment 2 Exhibit B - Pricing Form.xlsx` (Pricing Form), RFP Exhibit A Section 3 (Exh A p.3-4 of 16, PDF p.32-33)
and Appendix II (Exh A p.14-15 of 16, PDF p.43-44). Counted 2026-11-17 by a parser over every Appendix III row (scratch
scripts, not tracked). Appendix III is free text typed by DEN techs, so filter counts are close, not exact; caveats below.

## 1. The four unit counts do not agree (ask DEN which governs: vendor-questions.md Q1)

| Unit type | Exh A Sec 3 "estimates" | Appendix II (service schedule) | Pricing Form "# of Units" | Appendix III rows |
|---|---|---|---|---|
| Ventilation smoke control fans (VSCF) | 40 | 40 | 40 | 38 |
| Air curtains | 150 | 148 | 150 | 80 |
| Air handling units (AHU) | 405 | 405 | 410 | 378 |
| MAU / DOAS | 125 | 125 | 125 | 86 |
| Rooftop units (RTU) | 95 | 91 | 120 | 66 |
| CRAC | 30 | 27 | 50 | 29 |
| Air conditioning units (ACU) | 200 | 197 | 200 | 115 |
| Fan coil units (FCU) | 430 | 426 (incl. about 15 baggage-tunnel FCUs) | 430 + 20 tunnel FCUs (separate line) | 349 (tunnel units not identifiable) |
| Fan-powered VAV | 225 | 225 | 250 | 146 |
| Passenger loading bridge PCA | 150, "not anticipated at this time" | 150, "not anticipated at this time" | 150, total cell "N/A" | 0 |
| Ad-hoc heat pump work order | | | | 1 |
| **Total (excl. PCA)** | **1,700** | **1,684** | **1,795** | **1,288** |

RFP text: "DEN has more than 1700 HVAC assets" (RFP p.3). Appendix III's only sheet is named "completed work orders": it
is a work-order export, not a full asset register (1,288 rows, 1,288 asset numbers, 1,287 WO numbers; WO 26-17644 is
used for two different assets).

## 2. Service frequency and annual workload

| Unit type | Appendix II filter changes/yr | Appendix II coil cleanings/yr | Pricing Form "Service/Year" filter | Pricing Form coil | Pricing Form units x filter services |
|---|---|---|---|---|---|
| VSCF | 160 (quarterly) | 40 | 4 | 1 | 160 |
| Air curtains | 444 ("every 4 months") | 148 | 3 | 1 | 450 |
| AHU | 1,620 (quarterly) | 405 | 4 | 1 | 1,640 |
| MAU / DOAS | 500 (quarterly) | 125 | 4 | 1 | 500 |
| RTU | 364 (quarterly) | 91 | 4 | 1 | 480 |
| CRAC | 108 (quarterly) | 27 | 4 | 1 | 200 |
| ACU | 394 (semi-annual) | 197 | 2 | 1 | 400 |
| FCU | 1,644 (quarterly, 411 units) | 411 | 4 | 1 | 1,720 |
| Tunnel FCU | 90 (bi-monthly, 15 units) | 30 (semi-annual) | 6 (20 units) | 1 | 120 |
| FP-VAV | 450 (semi-annual) | 225 | 2 | 1 | 500 |
| **Total** | **5,774** | **1,699** | | | **6,170 filter services; 1,795 coil cleanings** |

Appendix II states the totals itself: "5774 filter changes", "1699 coil cleanings" (Exh A p.15 of 16). Coil cleaning is
not automatic: "All Annual and Semi-Annual filter change work orders require coil cleaning inspection at the time of filter
replacement. Coil cleaning shall be completed at the discretion of the PM." (Appendix I item 8, Exh A p.13 of 16).

Frequency words in the Appendix III work-order text: VSCF 38 "QUARTERLY"; MAU/DOAS 86 "QUARTERLY"; CRAC 27 "QUARTERLY"
(2 not stated); ACU 115 "SEMI-ANNUAL"; FP-VAV 146 "SEMI-ANNUAL"; air curtains 69 "SPRING SHUT-DOWN" + 11 "MID-WINTER";
AHU 378, FCU 349 and RTU 66 carry no frequency in the text.

## 3. Appendix III assets by location and type (rows)

Location groups come from the Location code prefix and the WO text (TML = "MTERM"; CCA/CCB/CCC = "ACON/BCON/CCON").

| Location group | Total | AHU | FCU | FP-VAV | ACU | MAU/DOAS | Air curtain | RTU | VSCF | CRAC | Other |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Main Terminal (TML) | 368 | 74 | 93 | 81 | 20 | 10 | 74 | 9 | | 7 | |
| Concourse B (CCB) | 201 | 104 | 45 | | 11 | 4 | 2 | 7 | 22 | 5 | 1 |
| Concourse C (CCC, incl. 1 C28 jet-bridge RTU) | 176 | 56 | 87 | | 8 | 17 | | 1 | 6 | 1 | |
| Concourse A (CCA) | 136 | 84 | 30 | | 2 | 7 | | 1 | 10 | 2 | |
| Airport Office Building (AOB) | 88 | | 10 | 65 | | | | | | 13 | |
| Hotel / Transit Center (PTC, SPTC) | 57 | 7 | 43 | | 2 | 1 | 4 | | | | |
| Maintenance Center / GT Holding Lot (MNC, MNA) | 35 | 17 | 7 | | 4 | 1 | | 6 | | | |
| "PKG" codes (WO text: MTERM level 3 MAUs) | 26 | | 3 | | 12 | 11 | | | | | |
| World Port (WP12, WPA, WPB) | 21 | 1 | 1 | | | | | 19 | | | |
| Fire stations (AR1, FS2, FS3, FS4, FS35) | 20 | 7 | 3 | | 3 | 7 | | | | | |
| Cargo A/B/C (CAA, CAB, CAC) | 19 | | 2 | | | 17 | | | | | |
| AGTS train / tunnel (AGT) | 15 | 11 | 3 | | | | | | | 1 | |
| Data Center (DTC) | 8 | | 8 | | | | | | | | |
| Other outlying buildings (44 codes) | 118 | 17 | 14 | | 53 | 11 | | 23 | | | |
| **Total** | **1,288** | **378** | **349** | **146** | **115** | **86** | **80** | **66** | **38** | **29** | **1** |

Outlying codes (rows): EST 11, PAB 7 ("B TURNSTILE"), VSB 6 (vehicle storage), DWA 6, CDL 6 (7198 N. Scottsburg St.),
L01 4 + L02 3 (lift stations), K9A 4 (DPD K9), BMS 4, ENV 4 (glycol recovery), LST 4 (snow trailers, south campus),
CRL 3 (rental car building), REV1/2/3 7 (electrical vaults), A1A-A4C 17 (antenna farm towers), COC 3 (26989 E 97th Ave
trailers), CHN 3 (north hut, gate 4), PNT 2 (paint storage), USD 2 (USDA / airside ops), PAA 2, TRF 2 (ARFF training),
CSE 2, OTA 2, OTB 2, GRR 1, CHS 1, toll plazas ECM/EEM/WCM/WEM/EE1/EC1 6, de-ice trailers DCS/DCN 2, CTS 1, MCS 1.

## 4. Filters (Appendix III "Filter Type" and "2nd Filter Type" columns)

Data quality, "Filter Type" column (1,288 rows): 1,021 give at least one size; 198 blank or "N/A"; 68 washable / metal /
mesh / reusable (FCU 26, air curtain 24, ACU 15, AHU 2, MAU 1); 1 "No Filter required on this unit". "2nd Filter Type"
holds a second size on 102 rows (92 AHUs: mostly 6-inch filters behind 2-inch pre-filters); the rest are blank, "N/A" or
dates typed into the wrong column.

Assets with a readable size, by type: AHU 358 of 378; FCU 275 of 349; FP-VAV 92 of 146; ACU 51 of 115; MAU/DOAS 79 of 86;
air curtain 47 of 80; RTU 61 of 66; VSCF 38 of 38; CRAC 21 of 29.

**Filter pieces for one service of every listed asset: about 8,403** (both columns; 98 distinct sizes, face dimensions
treated as one size in either order, so 20x25x2 = 25x20x2; 61 of 1,315 size entries give no count and are counted as 1;
one typo "24x24x26" read as 24x24x6). Assets with blank filter data add an unknown number on top.

| By unit type | Pieces per service |
|---|---|
| AHU | 5,547 (of which 1,253 in the 2nd-filter column) |
| MAU / DOAS | 1,313 |
| VSCF | 514 |
| FCU | 461 |
| RTU | 207 |
| Air curtain | 133 |
| FP-VAV | 92 |
| ACU | 84 |
| CRAC | 52 |

| By depth | Pieces per service |
|---|---|
| 2 inch | 6,656 |
| 6 inch | 1,299 |
| 1 inch | 315 |
| 4 inch | 127 |
| Other (1-3/4 in, 12 in) | 6 |

| Top sizes | Pieces per service | Main users |
|---|---|---|
| 24x24x2 | 3,097 | AHU 2,958 |
| 25x20x2 | 1,001 | VSCF 406, MAU 337, AHU 171, RTU 69 |
| 24x24x6 | 920 | AHU 888 |
| 20x20x2 | 845 | MAU 528, VSCF 108, FCU 47, ACU 33, RTU 28 |
| 24x20x2 | 543 | AHU 513 |
| 25x16x2 | 470 | MAU 234, air curtain 108, FCU 92 |
| 24x12x2 | 386 | AHU 376 |
| 24x20x6 | 227 | AHU 227 |
| 20x16x2 | 210 | FCU 90, AHU 71, CRAC 22, RTU 16, MAU 11 |
| 24x12x6 | 152 | AHU 152 |
| 25x16x1 | 86 | FP-VAV 46, FCU 16, air curtain 15 |
| 24x20x4 | 42 | AHU 40 |
| 25x20x4 | 31 | MAU 18, FCU 8, CRAC 4 |
| 25x15x1 | 27 | FP-VAV 25 |
| 25x16x4 | 18 | FCU 11, CRAC 7 |
| 20x20x4 | 16 | mixed |
| 82 other sizes | 332 | odd FCU / air-curtain / CRAC sizes (e.g., 43.5x10.5x1, 13.5x13.5x1, 60x10x1, 40x13x1) |

Annualized (derived, not a DEN figure): the 1,288 listed assets at the Appendix II frequency for their type (all FCUs at
4 per year) come to **4,547 filter-change visits and about 33,100 filter pieces a year** (24x24x2 about 12,400; 25x20x2
about 4,000; 24x24x6 about 3,650; 20x20x2 about 3,300). DEN supplies the filters (Exh A Sec 1(c): "materials (not
including filters)"), so these counts drive labor, handling and disposal, not purchasing.

MERV (column F): MERV 9 family (9, 9-A, 9A, 30/30 9) 600; MERV 8 family (8, 8-A) 316; MERV 13: 12; MERV 12: 5;
MERV 14: 4; blank 301; N/A 47; washable 2; "A" 1.

## 5. Coil-cleaning units

- Appendix II: **1,699 coil cleanings a year** (one per unit per year, except about 15 tunnel FCUs twice a year).
- Pricing Form: **1,795 units x 1 per year** (every line, including 20 tunnel FCUs at 1 per year, not 2).
- Appendix III has no coil-cleaning column. 13 rows carry the flag "Requires Coil Cleaning" (ACU 7, FCU 3, AHU 2, CRAC 1).
- Cleaning is "at the discretion of the PM" (Appendix I item 8), so the 1,699 / 1,795 are planning numbers, not a promise.

## 6. Other counts from Appendix III worth pricing

- 56 work orders mention a roof; 14 mention a ladder ("need ladder", "extension ladder").
- 15 AGTS train/tunnel assets (AGTS tunnel AHUs, train-platform CRAC and FCUs).
- 12 work orders (the 12 rows shifted one column right) carry the text "TRUE CLEANING SOLUTIONS-" in the description,
  probably the vendor that did those jobs in DEN's work-order system (an inference, not a DEN statement).

## 7. Pricing Form structure (`Attachment 2 Exhibit B - Pricing Form.xlsx`)

One sheet, "Sheet 1" (B2:M57), header "Professional Services". No sheet protection, no data validation.

- Header block: Company Name (C4, prefilled "Sample HVAC Company"), Project Name (C5, "Filters Changes & Coil Cleaning"),
  Date (C6, prefilled 2026-11-01), **Service Total (E5 = K22 + K40)**: the evaluated total is the 5-year filter total
  plus the 5-year coil total. Hourly rates are not in it.
- Table 1, "Cost Per Unit Filter Change Only" (rows 9-19): Equipment Type | # of Units (DEN-filled) | Service/Year
  (DEN-filled) | **Cost Per ONE UNIT Filter Change (column F, bidder fills)** | Total Per Unit Type (G = D x E x F).
  11 lines: VSCF 40x4, air curtains 150x3, AHU 410x4, MAU/DOAS 125x4, RTU 120x4, CRAC 50x4, ACU 200x2, FCU 430x4,
  tunnel FCU 20x6, FP-VAV 250x2, PCA 150x4 (total "N/A"). Year 1 Total C22 = SUM(G9:G18). **Year 2-5 Total cells D22:G22
  are blank for the bidder.** K22 "Total 5 Year Filter Change Cost" = SUM(C22:G23).
- Table 2, "Cost Per Unit Coil Cleaning Only" (rows 28-38): same columns, Service/Year = 1 on every line, **Cost Per ONE
  Unit Coil Cleaning (column F, bidder fills)**. Same 11 lines and unit counts. **Only G28 has a formula; G29:G37 are
  empty**, so Year 1 Total C41 = SUM(G28:G37) picks up only the smoke-fan line unless the bidder (or an addendum) adds the
  formulas (vendor-questions.md Q3). Year 2-5 cells D41:G41 blank; K40 "Total 5 Year Coiling Cleaning Cost" =
  SUM(C41:G42).
- Table 3, "Hourly Rates for Additional Work as Requested by the PM" (rows 46-57): Staff Role/Title | Hourly Rate |
  Estimated # of Staff | Comments. Row 47 is DEN's example: "Ex. Air Filter Specialist", 65, 6, "Responsible for all air
  filter changes and coil cleaning work". Replace the example with our roles.
- Notes printed beside each table (I8, I27, H46), verbatim: "* All rates must include Prevailing Wage Rates where
  required. *All rates are fully burdened and the following items are assumed to be included in overhead cost, and will
  not be allowed under this contract: vehicle cost, fuel, parking, trip charges, mobilization, subsistence, per diem,
  travel expenses, insurance premiums, adminstrative costs, equipment and materials. **Total increase for years 2-5 must
  not exceed 5% per year".
- What the bidder fills: company name and date; F9:F18 (10 filter unit prices); F28:F37 (10 coil unit prices) and the
  missing G29:G37 formulas; D22:G22 and D41:G41 (Year 2-5 totals, at most 5% a year increase); the hourly table. Submit
  as a separate Excel file, not inside the PDF (RFP p.21, IV-2.B).
- Conflict to resolve: Exh A Sec 13(4) says "All pricing submitted by the Contractor shall be firm for the term of the
  Contract, unless otherwise approved by DEN", while the form allows up to 5% a year (vendor-questions.md Q4).
