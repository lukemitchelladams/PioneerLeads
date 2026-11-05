# Town of Parker RFP 26-021-1: pricing map (workbook line → Colorado Standby item → markup rule)

Prepared 2026-11-05. **No numbers in this file. Ever.** The filled workbook and Colorado Standby's quote live in `bids/parker-generator-maintenance/private/` (git-ignored by `bids/*/private/`).

Markup rule for every line: **[Luke sets %; apply in private/, never here]**.

Source workbook: "Town of Parker Generator Maintenance Services Price Sheet _ Forms - Revised.xlsx", four sheets (Instructions, Scheduled Services, Labor & Charges, Proposal Forms). It is in Luke's 2026-10-30 sent mail to Brad Orgill (Gmail message `1a18d5cc8082418f`), not in docs/. Yellow cells = offeror input; green = calculated (workbook Instructions, rows 14-16).

Colorado Standby items = the ten numbered items in Luke's 2026-10-26 email to Brad (thread `1a17912791bd5d12`):
1 annual PM per unit (PD quarterly: three inspections + one annual) · 2 ATS inspection/testing per switch · 3 annual resistive load bank per unit · 4 oil and coolant lab analysis per sample · 5 one-time initial inventory · 6 hourly labor (regular, after-hours, weekend/holiday) and emergency call-out · 7 parts and consumables (discount off list or markup) · 8 guaranteed 24/7 on-site response time in Parker · 9 factory training/authorizations by brand · 10 three references, sample service report, COI.

## A. Scheduled Services sheet (annual, per facility)

Town note on this sheet: "Pricing should include all labor, travel, routine materials, testing, reports, and disposal required for the listed scheduled service unless specifically identified as an exclusion." Instruction 2: "For facilities with more than one unit, enter the combined facility price for all listed units."

| Cell | Facility (units) | Town column label | Built from Colorado Standby item(s) | Basis | Markup rule | Assumption to state |
|---|---|---|---|---|---|---|
| C4 | Town Hall (1: Rolls-Royce LSA 49.3/L10) | Semiannual PM / ATS | CS 1 (PM, 1 unit) + CS 2 (ATS, 1 switch) | per facility per year | [Luke sets %; apply in private/, never here] | PM frequency (annual per RFP §4.4 vs "Semiannual" label); 1 ATS; unit rating unknown |
| C5 | PACE Center (1: Onan 125 kW) | Semiannual PM / ATS | CS 1 + CS 2 | per facility per year | [Luke sets %; apply in private/, never here] | PM frequency; 1 ATS |
| C6 | Fieldhouse (1: Onan 400 kW) | Semiannual PM / ATS | CS 1 + CS 2 | per facility per year | [Luke sets %; apply in private/, never here] | PM frequency; 1 ATS |
| C7 | MOTS Operations (2: Detroit 150 kW, Detroit 250 kW) | Semiannual PM / ATS | CS 1 × 2 units + CS 2 × 2 switches, combined | per facility per year (combined) | [Luke sets %; apply in private/, never here] | Combined price per instruction 2; 2 ATS assumed |
| C8 | Police Department (1: Cummins 750 kW) | Semiannual PM / ATS | CS 1 quarterly variant: 3 inspections + 1 annual service with oil change (RFP §4.3) + CS 2 (ATS test in the annual) | per facility per year | [Luke sets %; apply in private/, never here] | Quarterly per RFP §4.3 regardless of the column label; oil change included in the annual |
| C9 | Public Works Operations (1: Kohler 500 kW) | Semiannual PM / ATS | CS 1 + CS 2 | per facility per year | [Luke sets %; apply in private/, never here] | PM frequency; 1 ATS |
| D4-D9 | each facility (MOTS = 2 units combined) | Annual Load Bank | CS 3 (× units at the facility) | per facility per year | [Luke sets %; apply in private/, never here] | OEM-recommended capacity and duration (RFP §4.6); load bank for 750 kW confirmed by CS |
| E4-E9 | each facility (MOTS = 2 units combined) | Oil and Coolant Analysis | CS 4 × (samples per unit per year: oil + coolant) × units | per facility per year | [Luke sets %; apply in private/, never here] | Samples per unit per year; lab fee included |
| F4-F9 | each facility | Annual Total | calculated `=SUM(C:E)` | green | do not type | |
| C10:F10 | TOTAL ANNUAL SCHEDULED SERVICES | calculated | green | do not type | |
| G4-G9 | (no header) | `=SUM(C4:F4)` double-counts F | workbook quirk | do not type | Mention in assumptions only if the Town's totals look doubled |

Not on this sheet but required by the RFP: **CS 5, initial inventory (RFP §4.2)**. Options for Luke: (a) fold into year-one C4-C9 and say so in the assumptions; (b) add it under Labor & Charges row 8 "Other (describe)" as a one-time item. RFP §2.2: nothing is paid unless "specifically identified in the accepted pricing."

## B. Labor & Charges sheet

### B1. Hourly labor rates (rows 5-8; columns B Regular Hours, C After-Hours, D Weekend, E Holiday, F Minimum Charge / Travel)

| Cells | Town classification | Built from | Markup rule | Note |
|---|---|---|---|---|
| B5:F5 | Generator Technician | CS 6 (regular, after-hours, weekend, holiday; minimum/trip) | [Luke sets %; apply in private/, never here] | All-in rate the Town is billed; see ambiguity on row 13 |
| B6:F6 | Senior / Controls Technician | CS 6, if Colorado Standby has the class; else "N/A" | [Luke sets %; apply in private/, never here] | Instruction 5: "Enter N/A or $0.00 when a charge does not apply" |
| B7:F7 | Helper / Apprentice | CS 6, if offered; else "N/A" | [Luke sets %; apply in private/, never here] | |
| B8:F8 | Other (describe) | [LUKE: initial inventory as a one-time item, or load bank crew, or "N/A"] | [Luke sets %; apply in private/, never here] | Candidate home for CS 5 |

### B2. Parts, materials and other charges (rows 12-18, answer in column B; cells B12:F18 are merged)

| Cell | Town pricing element | Town prompt (quoted) | Built from | Markup rule | Note |
|---|---|---|---|---|---|
| B12 | Parts pricing / markup | "Cost plus ____%  or  List less ____%  \|  Other: ____" | CS 7 | [Luke sets %; apply in private/, never here] | Pick one form; "genuine or manufacturer-approved parts" (RFP §4.9) |
| B13 | Subcontractor markup | "________ %" | [LUKE decides] | [Luke sets %; apply in private/, never here] | Our structure is prime + one named sub. Recommend: labor rows are all-in; row 13 applies to third-party specialty work only. State it in the assumptions. |
| B14 | Shipping / expedited freight | (blank) | CS 7 terms, or "at cost" / "N/A" | [Luke sets %; apply in private/, never here] | |
| B15 | Emergency call-out fee | (blank) | CS 6 (call-out charge) | [Luke sets %; apply in private/, never here] | If none, write "None" (instruction 5) |
| B16 | Travel / mileage / fuel surcharge | (blank) | CS 6 ("build those in or list them", Luke's 10/26 ask) | [Luke sets %; apply in private/, never here] | RFP §2.2: not payable unless listed here. Recommend "Included" / "None" |
| B17 | Environmental / disposal fees | (blank) | CS 1 (disposal inside PM) | [Luke sets %; apply in private/, never here] | Scheduled Services note includes "disposal"; recommend "Included in scheduled services; None for repairs unless listed" |
| B18 | Annual price adjustment method | "Index / method, frequency, cap, and required notice: ____" | [LUKE decides] | n/a (a method, not a price) | RFP §2.2: adjustments "in writing with supporting documentation ... subject to Town approval" |

## C. Proposal Forms sheet

| Cells | Town section | Built from | Note |
|---|---|---|---|
| A5:C9 | Proposed Subcontractors: Firm / Work to Be Performed / Qualifications / Authorization | Row 1: Colorado Standby / all field service (inventory, PM, ATS, load bank, sampling, emergency, repairs) / CS 9 | Matches the §8 approval request in the proposal. Rows 2-5: "N/A" unless Colorado Standby uses a lab or load-bank partner it wants named |
| A12:E17 | References: Client / Contact, Email / Phone, Locations & Equipment, Scope, Contract Dates ("at least three") | CS 10 | Colorado Standby's contracts, shown as the subcontractor's |

## D. Colorado Standby items that go in the proposal PDF, not the workbook

| CS item | Where it lands |
|---|---|
| 5 initial inventory | Pricing decision above (A); timeline in proposal §5 |
| 8 guaranteed response time | Proposal §6.1 and §3.2 Q5 |
| 9 factory training / authorizations | Proposal §4.2 brand table; workbook Proposal Forms C5 |
| 10 sample service report | Proposal §7 |
| 10 certificate of insurance | Proposal §9.5 |
| warranty period (RFP §4.11, not in the ten) | Proposal §3.1.12, §8 item 13 |
| lab name and turnaround (RFP §4.7, not in the ten) | Proposal §3.1.8 |

## E. Build order the hour Brad's numbers land

1. Save Brad's email and any attachment to `private/` (never docs/, never this file).
2. Copy the Town workbook from Luke's sent mail into `private/` and rename it `Brown Bison Holdings - Town of Parker Generator Maintenance Services Price Sheet & Forms.xlsx`.
3. Fill yellow cells per sections A-C with CS items plus Luke's markup. Leave green cells and column G alone.
4. Write the assumptions page (proposal §8) with every bracket resolved, numbers only in the workbook.
5. Check every row has a value, "Included," "None" or "N/A" (instruction 5: "do not leave required fields unexplained").
6. Luke reviews totals in private/, signs the cover letter, uploads PDF + workbook on BidNet 0000440494 (and Bonfire if a 26-021-1 project exists).
