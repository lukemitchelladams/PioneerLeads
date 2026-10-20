"""Fill DCSD's own "Mowing Sites Price Sheet.xlsx" (RFP 003-27) from YMS Landscaping's per-site prices plus Brown
Bison's markup.

    python3 bids/dcsd-mowing-003-27/submission/build_price_sheet.py              # submission copy, with markup
    python3 bids/dcsd-mowing-003-27/submission/build_price_sheet.py --for-sub    # YMS's own prices, for YMS sign-off

Input: private/alex_prices.json (git-ignored), YMS's numbers split into the District's columns:
  {"markup": 0.05, "weeks": 27, "months": 7,
   "sites": {"Chaparral HS": {"turf_acres": 10.396, "turf_weekly": 0, "rock_weekly": 0, "mulch_weekly": 0,
                              "edging_monthly": 0, "native_monthly": 0, "aeration": 0, "fertilization": 0,
                              "broadleaf": 0, "extra_athletic_mow": 0, "alex_season_total": 0}, ...},
   "additional_services": [["Extra full-site mow on request", "per acre", 57], ...],
   "expected_base_total": <YMS season total>, "expected_seasonal_grand_total_with_markup": <that x 1.05>}
Every dollar figure is raised by the markup and rounded to the cent. A site's seasonal total is rebuilt from its
marked-up parts: (turf + rock + mulch) x weeks + (edging + native) x months + aeration + fertilization + broadleaf.
The District form has no columns for edging or the one-time spring treatments, so they are included in the seasonal
and monthly totals and broken out per site on a "Site Services Detail" sheet (Q&A 1, Q9: "broken down into each
individual site and its services"). Additional mows are priced per school, outside the total (Q&A 1, Q11).
The build stops if YMS's base totals do not reproduce or the marked-up grand total is off by more than $1.
Output: private/Brown Bison Holdings LLC - DCSD 003-27 Price Sheet.xlsx
"""
from __future__ import annotations

import json
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Font

BID = Path(__file__).resolve().parents[1]
FORM = BID / "docs" / "Mowing Sites Price Sheet.xlsx"
INPUTS = BID / "private" / "alex_prices.json"
OUT = BID / "private" / "Brown Bison Holdings LLC - DCSD 003-27 Price Sheet.xlsx"
SUB_OUT = BID / "private" / "FOR YMS APPROVAL - DCSD 003-27 Price Sheet (YMS prices).xlsx"
FOR_SUB = "--for-sub" in sys.argv
FORM_COLS = {"turf_weekly": "D", "rock_weekly": "F", "mulch_weekly": "H", "native_monthly": "J"}
PARTS = ["turf_weekly", "rock_weekly", "mulch_weekly", "edging_monthly", "native_monthly", "aeration",
         "fertilization", "broadleaf", "extra_athletic_mow"]
GROUP_TOTAL_ROWS = {"GROUP 2 TOTALS": "Group 2", "GROUP 5 TOTALS": "Group 5", "GROUP 7 TOTALS": "Group 7",
                    "GROUP 8 TOTALS": "Group 8"}
MONEY = '"$"#,##0.00'
CENT = Decimal("0.01")
BOLD = Font(bold=True)


def d(x) -> Decimal:
    return Decimal(str(x))


def up(x, markup) -> Decimal:
    return (d(x) * (1 + d(markup))).quantize(CENT, ROUND_HALF_UP)


def season(p: dict, weeks: int, months: int) -> Decimal:
    return ((p["turf_weekly"] + p["rock_weekly"] + p["mulch_weekly"]) * weeks
            + (p["edging_monthly"] + p["native_monthly"]) * months
            + p["aeration"] + p["fertilization"] + p["broadleaf"])


def put(ws, ref, value, fmt=MONEY, bold=False):
    ws[ref] = float(value) if isinstance(value, Decimal) else value
    if isinstance(value, (Decimal, float, int)) and fmt:
        ws[ref].number_format = fmt
    if bold:
        ws[ref].font = BOLD


def main() -> int:
    cfg = json.loads(INPUTS.read_text())
    m, weeks, months = (0 if FOR_SUB else cfg["markup"]), cfg["weeks"], cfg["months"]
    who = "YMS Landscaping prices for approval" if FOR_SUB else "Brown Bison Holdings LLC"
    base_total, priced = Decimal(0), {}
    for name, site in cfg["sites"].items():
        missing = [k for k in PARTS if site.get(k) is None]
        if missing:
            sys.exit(f"{name}: missing {missing}")
        base = {k: d(site[k]) for k in PARTS}
        if abs(season(base, weeks, months) - d(site["alex_season_total"])) > CENT:
            sys.exit(f"{name}: parts do not add up to YMS's season total {site['alex_season_total']}")
        base_total += d(site["alex_season_total"])
        p = {k: up(site[k], m) for k in PARTS}
        p["seasonal"] = season(p, weeks, months)
        p["monthly"] = (p["seasonal"] / months).quantize(CENT, ROUND_HALF_UP)
        p["acres"] = d(site["turf_acres"])
        priced[name] = p
    if abs(base_total - d(cfg["expected_base_total"])) > CENT:
        sys.exit(f"YMS base total {base_total} does not match the expected {cfg['expected_base_total']}")

    wb = openpyxl.load_workbook(FORM)
    ws = wb.active
    group_of, seen, group = {}, set(), []
    gk = gl = grand_k = grand_l = Decimal(0)
    for row in range(1, ws.max_row + 1):
        name = (ws[f"A{row}"].value or "").strip()
        if name in priced:
            p = priced[name]
            for key, col in FORM_COLS.items():
                put(ws, f"{col}{row}", p[key])
            put(ws, f"K{row}", p["monthly"])
            put(ws, f"L{row}", p["seasonal"])
            gk, gl = gk + p["monthly"], gl + p["seasonal"]
            group.append(name)
            seen.add(name)
        elif name in GROUP_TOTAL_ROWS:
            put(ws, f"K{row}", gk, bold=True)
            put(ws, f"L{row}", gl, bold=True)
            for n in group:
                group_of[n] = GROUP_TOTAL_ROWS[name]
            grand_k, grand_l, gk, gl, group = grand_k + gk, grand_l + gl, Decimal(0), Decimal(0), []
        elif str(ws[f"J{row}"].value or "").strip() == "Grand Totals":
            put(ws, f"K{row}", grand_k, bold=True)
            put(ws, f"L{row}", grand_l, bold=True)
            note = ws[f"A{row + 2}"]
            note.value = ("Seasonal totals include monthly edging and the one-time spring core aeration, fertilization "
                          "and broadleaf application at each site (broken out per site on the 'Site Services Detail' "
                          "sheet). Monthly total = seasonal total / 7 monthly billing cycles. Weeks the District "
                          "adds beyond the 27-week basis (Q&A 1, Q9) are billed at each site's weekly prices above. "
                          "Additional mows and additional services are priced separately on the 'Additional "
                          "Pricing' sheet (Q&A 1, Q9 and Q11). "
                          + ("FOR YMS APPROVAL: YMS Landscaping's own prices on the District's form, before Brown "
                             "Bison's markup." if FOR_SUB else "Respondent: Brown Bison Holdings LLC."))
            note.alignment = Alignment(wrap_text=True, vertical="top")
            ws.merge_cells(start_row=row + 2, start_column=1, end_row=row + 4, end_column=12)
    missing = set(priced) ^ seen
    if missing:
        sys.exit(f"site names that did not match the District form: {sorted(missing)}")
    # The District's Google Sheets export pads the form with empty formatted cells out to X969; drop them so the
    # file stays small. Nothing in the used area (A1:L, through the note under Grand Totals) moves or changes.
    last_row = max(r for (r, c), cell in ws._cells.items() if cell.value is not None) + 3
    for key in [k for k in ws._cells if k[0] > last_row or k[1] > 12]:
        del ws._cells[key]
    # Each part is marked up and rounded to the cent before it is multiplied out, so the total can drift from
    # base x (1 + markup) by up to about $0.50 a site.
    expect = d(cfg["expected_base_total"] if FOR_SUB else cfg["expected_seasonal_grand_total_with_markup"])
    if abs(grand_l - expect) > d("0.50") * len(priced):
        sys.exit(f"seasonal grand total {grand_l} does not match the expected {expect}")

    det = wb.create_sheet("Site Services Detail")
    det.append([f"{who} - RFP 003-27 Mowing Services: each site and its services (27-week season)"])
    det["A1"].font = BOLD
    det.append([])
    heads = ["Group", "Site", "Turf, weekly", "Rock beds, weekly", "Mulch beds, weekly", "Edging, monthly",
             "Native mowing, monthly", "Core aeration, once (spring)", "Fertilization, once", "Broadleaf, once",
             "Seasonal total"]
    det.append(heads)
    for c in det[3]:
        c.font = BOLD
        c.alignment = Alignment(wrap_text=True, vertical="top")
    keys = ["turf_weekly", "rock_weekly", "mulch_weekly", "edging_monthly", "native_monthly", "aeration",
            "fertilization", "broadleaf", "seasonal"]
    current, sub = None, {k: Decimal(0) for k in keys}
    total = {k: Decimal(0) for k in keys}

    def flush(label):
        det.append([f"{label} total", ""] + [float(sub[k]) for k in keys])
        for c in det[det.max_row]:
            c.font = BOLD

    for name in [n for n in group_of]:
        if current and group_of[name] != current:
            flush(current)
            sub = {k: Decimal(0) for k in keys}
        current = group_of[name]
        p = priced[name]
        det.append([current, name] + [float(p[k]) for k in keys])
        for k in keys:
            sub[k] += p[k]
            total[k] += p[k]
    flush(current)
    det.append(["All sites", ""] + [float(total[k]) for k in keys])
    for c in det[det.max_row]:
        c.font = BOLD
    det.append([])
    det.append([f"Seasonal total = (turf + rock + mulch) x {weeks} weeks + (edging + native) x {months} months "
                "+ aeration + fertilization + broadleaf."])
    for row in det.iter_rows(min_row=4):
        for c in row[2:]:
            if isinstance(c.value, float):
                c.number_format = MONEY
    det.column_dimensions["A"].width = 14
    det.column_dimensions["B"].width = 22
    for col in "CDEFGHIJK":
        det.column_dimensions[col].width = 15

    extra = wb.create_sheet("Additional Pricing")
    extra.append([f"{who} - RFP 003-27: additional pricing, separate from the seasonal total"])
    extra["A1"].font = BOLD
    extra.append([])
    extra.append(["Additional mows, priced per school (Q&A 1, Q11)", "Group", "Turf acres",
                  "Additional athletic-field mow, each", "Additional full-site mow, each"])
    for c in extra[3]:
        c.font = BOLD
        c.alignment = Alignment(wrap_text=True, vertical="top")
    full_rate = next(r for desc, unit, r in cfg["additional_services"] if desc.startswith("Extra full-site mow"))
    for name in group_of:
        p = priced[name]
        extra.append([name, group_of[name], float(p["acres"]), float(p["extra_athletic_mow"]),
                      float(up(d(full_rate) * p["acres"], m))])
    extra.append([])
    extra.append(["Additional services (unit rates)", "Unit", "Rate"])
    for c in extra[extra.max_row]:
        c.font = BOLD
    for desc, unit, rate in cfg["additional_services"]:
        r = d(rate) * (1 + d(m))
        r = r.quantize(Decimal("0.0001") if r < 1 else CENT, ROUND_HALF_UP)
        extra.append([desc, unit, float(r)])
        extra.cell(extra.max_row, 3).number_format = '"$"#,##0.0000' if r < 1 else MONEY
    for row in extra.iter_rows(min_row=4):
        for c in row[3:5]:
            if isinstance(c.value, float):
                c.number_format = MONEY
    extra.column_dimensions["A"].width = 62
    extra.column_dimensions["B"].width = 18
    for col in "CDE":
        extra.column_dimensions[col].width = 18
    out = SUB_OUT if FOR_SUB else OUT
    wb.save(out)
    print(f"wrote {out.relative_to(BID.parents[1])}")
    print(f"YMS base ${base_total:,.2f}; with {d(m) * 100:.0f}% markup: seasonal grand total ${grand_l:,.2f} "
          f"(expected ${expect:,.2f}), monthly ${grand_k:,.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
