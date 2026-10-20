"""Fill the Town of Parker's own price workbook (RFP 26-028, upload 6.1.3) from private/bid_inputs.json.

    python3 bids/town-of-parker-hvac-on-call/submission/build_price_workbook.py            # submission copy
    python3 bids/town-of-parker-hvac-on-call/submission/build_price_workbook.py --for-sub  # Rich's approval copy

Reads the Town's blank form (docs/2-HVAC-PM-Price-Sheet-Forms.xlsx), writes only the blue vendor-input cells, keeps the
Town's formulas, and saves into private/ (git-ignored: prices stay off the public repo until the bid closes). Dollar
numbers in bid_inputs.json are Rich's; the submission copy raises each by "markup", the --for-sub copy writes them
unchanged, paints every missing cell yellow (and every cell we filled on an assumption orange) and adds a "FOR RICH" sheet with the open questions, so it can never be
mistaken for the upload. Anything still null is listed at the end and the exit code is 1.
"""
from __future__ import annotations

import json
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill

BID = Path(__file__).resolve().parents[1]
FORM = BID / "docs" / "2-HVAC-PM-Price-Sheet-Forms.xlsx"
INPUTS = BID / "private" / "bid_inputs.json"
FACILITY_ROWS = {"Fieldhouse": 4, "Mots Bldg A": 5, "Pace Center": 6, "Police Department": 7, "Public Works": 8,
                 "Recreation Center": 9, "School House": 10, "Town Hall": 11, "Town Hall Addition": 12}
LABOR_ROWS = {"tech": 4, "senior": 5, "helper": 6, "other": 7}
LABOR_COLS = {"regular": "B", "after_hours": "C", "weekend": "D", "holiday": "E", "minimum": "F"}
CHARGE_ROWS = {"parts": 11, "consumables": 12, "refrigerant": 13, "subcontracted": 14, "shipping": 15,
               "emergency_callout": 16, "travel": 17, "disposal": 18, "lift": 19, "other": 20, "renewal": 21}
CHARGE_COLS = ("B", "C", "D", "E")  # basis, rate or markup, included/excluded, notes (E is merged E:F)


def money(x: float, markup: float) -> float:
    return float((Decimal(str(x)) * (Decimal(1) + Decimal(str(markup)))).quantize(Decimal("0.01"), ROUND_HALF_UP))


YELLOW = PatternFill("solid", fgColor="FFFF00")   # blank: the sub must fill it
ORANGE = PatternFill("solid", fgColor="FFC000")   # filled by us on an assumption: the sub must confirm it


def main() -> int:
    for_sub = "--for-sub" in sys.argv
    cfg = json.loads(INPUTS.read_text())
    markup = 0.0 if for_sub else cfg["markup"]
    wb = openpyxl.load_workbook(FORM)
    missing: list[str] = []
    holes: list[tuple[str, str]] = []  # (sheet, cell) left blank, painted yellow in the sub's copy
    assumed: list[tuple[str, str, str]] = []  # (sheet, cell, label) filled on an assumption, painted orange

    ws = wb["Scheduled Services"]
    for fac, row in FACILITY_ROWS.items():
        for col, season in (("C", "cooling"), ("D", "heating")):
            v = cfg["scheduled"][fac][season]
            if isinstance(v, dict):  # {"value": 1703.70, "assumed": "same as spring"}
                assumed.append(("Scheduled Services", f"{col}{row}", f"{fac} {season}: {v['assumed']}"))
                v = v["value"]
            if v is None:
                missing.append(f"Scheduled Services {fac} {season}")
                holes.append(("Scheduled Services", f"{col}{row}"))
            elif isinstance(v, (int, float)):
                ws[f"{col}{row}"] = money(v, markup)
                ws[f"{col}{row}"].number_format = '"$"#,##0.00'
            else:
                ws[f"{col}{row}"] = v  # e.g. 0 for no heating visit is written as a number; text stays text

    ws = wb["Labor & Charges"]
    for who, row in LABOR_ROWS.items():
        rates = cfg["labor"].get(who)
        if rates is None:
            continue
        for key, col in LABOR_COLS.items():
            v = rates.get(key) if isinstance(rates, dict) else rates
            if v is None:
                missing.append(f"Labor {who} {key}")
                holes.append(("Labor & Charges", f"{col}{row}"))
            elif isinstance(v, (int, float)):
                ws[f"{col}{row}"] = money(v, markup)
                ws[f"{col}{row}"].number_format = '"$"#,##0.00'
            else:
                ws[f"{col}{row}"] = v
    for item, row in CHARGE_ROWS.items():
        vals = cfg["charges"].get(item)
        if vals is None:
            missing.append(f"Charges {item}")
            holes.extend(("Labor & Charges", f"{c}{row}") for c in CHARGE_COLS)
            continue
        for col, v in zip(CHARGE_COLS, vals):
            if v is None:
                missing.append(f"Charges {item} column {col}")
                holes.append(("Labor & Charges", f"{col}{row}"))
            elif isinstance(v, dict):  # text carrying sub dollar amounts: {"fmt": "R-410A ${}/lb", "values": [70]}
                ws[f"{col}{row}"] = v["fmt"].format(*(f"{money(x, markup):,.2f}" for x in v["values"]))
            else:
                ws[f"{col}{row}"] = v

    ws = wb["Proposal Forms"]
    for i, sub in enumerate(cfg["subs"][:4]):
        for col, v in zip("ABCDEF", sub):
            ws[f"{col}{5 + i}"] = v
    for i, ref in enumerate(cfg["references"][:3]):
        if not any(ref):
            missing.append(f"Reference {i + 1}")
            holes.extend(("Proposal Forms", f"{c}{12 + i}") for c in "ABCDEF")
        for col, v in zip("ABCDEF", ref):
            ws[f"{col}{12 + i}"] = v
    if cfg.get("assumptions"):
        ws["A17"] = cfg["assumptions"]
    else:
        missing.append("Assumptions, exceptions, and renewal terms")
        holes.append(("Proposal Forms", "A17"))

    if for_sub:
        for sheet, cell in holes:
            wb[sheet][cell].fill = YELLOW
        for sheet, cell, _ in assumed:
            wb[sheet][cell].fill = ORANGE
        ws = wb.create_sheet("FOR RICH", 0)
        ws.column_dimensions["A"].width = 120
        ws["A1"] = "FOR RICH CARROLL TO REVIEW: NOT FOR SUBMISSION"
        ws["A1"].font = Font(bold=True, size=14)
        ws["A2"] = ("These are your prices exactly as you wrote them, with no Brown Bison markup, typed into the Town's own "
                    "form. Yellow cells are still blank. Please check every number, fill the yellow cells, answer the "
                    "questions below, and reply 'approved'.")
        ws["A2"].alignment = Alignment(wrap_text=True)
        for i, q in enumerate(cfg.get("questions_for_sub", []), start=4):
            ws[f"A{i}"] = f"{i - 3}. {q}"
            ws[f"A{i}"].alignment = Alignment(wrap_text=True)
        out = BID / "private" / f"FOR RICH REVIEW - {cfg['sub_company']} prices in Town of Parker form.xlsx"
    else:
        out = BID / "private" / f"{cfg['company']} - Town of Parker HVAC PM Price Workbook.xlsx"
    wb.save(out)
    print(f"wrote {out.relative_to(BID.parents[1])}")
    print("STILL MISSING:" if missing else "complete: every vendor cell filled")
    for m in missing:
        print(f"  - {m}")
    if assumed:
        print("ASSUMED, NOT YET CONFIRMED BY THE SUB (orange in the sub's copy):")
        for _, _, label in assumed:
            print(f"  - {label}")
    return 1 if missing or assumed else 0


if __name__ == "__main__":
    sys.exit(main())
