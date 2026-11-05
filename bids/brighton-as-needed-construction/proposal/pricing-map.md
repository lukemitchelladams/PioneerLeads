# Brighton RFP 26500209M — Fee Schedule pricing map

Workbook: `Fee Schedule - Brown Bison DRAFT.xlsx` (copy of the City's `docs/26500209M Fee Schedule.xlsx`, sheet
"MPA Fee Schedule"). Every rate cell holds the text `[RATE]`. Terms 2-5 keep the City's formulas
(`=(C7*0.03)+C7` etc.): type the Term 1 number and the renewals calculate at the 3% cap. Row 39 "Equipment markup" is
the only line added to the City's form; the Q&A allows it: "Please enter the equipment markup on a line within the fee
schedule or include elsewhere it as part of your proposal."

**Markup is set by Luke in `bids/brighton-as-needed-construction/private/` (gitignored), never here.** This repo is
public: no rate, cost, markup or sub price goes in any tracked file. Every number in the workbook stays `[RATE]` until
Luke fills the copy he submits.

Rule from the RFP that shapes every line: p.7 "Pricing submitted by Contractor shall be fully burdened ... The City will
not pay trip charges or service call fees under this master price agreement." Ceres's trip charge has to be folded into
the hourly rate or dropped. p.3: the per-hour charge includes "all on-site visits, inspections, report preparation,
copies, travel time, meeting attendance, photographs, schedule reporting, final inspections, occupancy coordination,
etc." so there is no separate PM, travel or estimating line.

## Hourly labor lines (rows 7-18, UOM = Hour)

| Row | Description (as typed in column A) | Base cost comes from | Luke adds |
|-----|-------------------------------------|----------------------|-----------|
| 7 | Lead carpenter / working foreman, regular hours (Mon-Fri 7:00 am-5:00 pm) | [SUB: Ceres lead/foreman rate] | markup in private/ |
| 8 | Carpenter (journeyman), regular hours | [SUB: Ceres carpenter rate] | markup |
| 9 | General repair / handyman technician, regular hours | [SUB: Ceres general-repair rate] (the rate Monica promised) | markup |
| 10 | Drywall and finish technician, regular hours | [SUB: Ceres drywall/finish rate; if same person as row 9, same base] | markup |
| 11 | Painter, regular hours | [SUB: Ceres painter rate, or other sub] | markup |
| 12 | Flooring installer, regular hours | [SUB: Ceres flooring rate] | markup |
| 13 | Laborer / helper (demolition, hauling, cleanup), regular hours | [SUB: Ceres helper rate] | markup |
| 14 | Lead carpenter / working foreman, after-hours, weekend or holiday (City-requested) | [SUB: after-hours rate, or regular x factor the sub names] | markup |
| 15 | Carpenter / technician / painter / flooring installer, after-hours, weekend or holiday (City-requested) | [SUB: after-hours rate] | markup |
| 16 | Laborer / helper, after-hours, weekend or holiday (City-requested) | [SUB: after-hours rate] | markup |
| 17 | Emergency response, any trade, work begun within 3 hours of City notification, regular hours | [SUB: emergency rate; confirm the 3-hour start] | markup |
| 18 | Emergency response, any trade, after-hours, weekend or holiday | [SUB: emergency after-hours rate] | markup |

Rows 19-35 are left blank (City form, not altered). If Luke adds a fencing or masonry sub, use rows 19-20 with the same
pattern and name the sub in the Subcontractor list form.

## Markup lines (rows 37-39, UOM = %)

| Row | Description | Source | Note |
|-----|-------------|--------|------|
| 37 | Materials markup (City form) | Luke, private/ | On "actual wholesale cost" (RFP p.7); supplier invoices attached to every invoice. Same % all five terms unless Luke decides otherwise. |
| 38 | Subcontractor markup (City form) | Luke, private/ | Applies to specialty subs quoted per task order outside rows 7-18 (abatement, masonry, fencing, etc.). See submittal-checklist.md ambiguity 2 for the structure decision. |
| 39 | Equipment markup (rented equipment, on wholesale cost) — added per Q&A | Luke, private/ | Owned tools and small equipment are included in the hourly rates (narrative, proposal-draft.md §4). |

Row 42 (merged A42:G43, "Name of Firm submitting proposal"): Brown Bison Holdings LLC — filled.

## Structure note (Option A, as drafted)

Rows 7-18 are the fully burdened rates the City pays Brown Bison for each labor class, whoever performs the hour. Brown
Bison's management, insurance (including the $1M professional liability line the Q&A keeps), overhead and profit are
inside those rates. Row 38 is for subs beyond the standing crew. If Luke prefers Option B (sub's raw rate shown, row 38
applied on top), change the §4 narrative in proposal-draft.md to match before submitting.

## What the sub must send (ask Ceres today)

1. Hourly rate for each class in rows 7-13 they staff (regular hours) and the after-hours/emergency rates for rows 14-18.
2. Written yes/no on beginning emergency work within three (3) hours of notification, business hours and after hours.
3. Confirmation the trip charge can be folded into the hourly rate (the City will not pay it as a line).
4. COI showing current limits (the MPA wants WC, GL $1M/$1M, Auto $1M on subs).
5. Project list (6 fields per project), crew-lead resume, equipment list, EMR letter or loss runs if they have them.
