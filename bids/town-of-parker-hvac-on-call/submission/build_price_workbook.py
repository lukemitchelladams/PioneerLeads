"""Fill the Town of Parker's own price workbook (RFP 26-028, upload 6.1.3) from private/bid_inputs.json.

    python3 bids/town-of-parker-hvac-on-call/submission/build_price_workbook.py

Reads the Town's blank form (docs/2-HVAC-PM-Price-Sheet-Forms.xlsx), writes only the blue vendor-input cells, keeps the
Town's formulas, and saves "<company> - Town of Parker HVAC PM Price Workbook.xlsx" into private/ (git-ignored: prices
stay off the public repo until the bid closes). Sub prices in bid_inputs.json are Rich's numbers; every dollar figure
marked "sub" is raised by the markup before it is written. Anything still null is left blank and listed at the end, so
an incomplete workbook is never mistaken for a finished one.
"""
from __future__ import annotations

import json
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import openpyxl

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


def main() -> int:
    cfg = json.loads(INPUTS.read_text())
    markup = cfg["markup"]
    wb = openpyxl.load_workbook(FORM)
    missing: list[str] = []

    ws = wb["Scheduled Services"]
    for fac, row in FACILITY_ROWS.items():
        for col, season in (("C", "cooling"), ("D", "heating")):
            v = cfg["scheduled"][fac][season]
            if v is None:
                missing.append(f"Scheduled Services {fac} {season}")
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
            elif isinstance(v, (int, float)):
                ws[f"{col}{row}"] = money(v, markup)
                ws[f"{col}{row}"].number_format = '"$"#,##0.00'
            else:
                ws[f"{col}{row}"] = v
    for item, row in CHARGE_ROWS.items():
        vals = cfg["charges"].get(item)
        if vals is None:
            missing.append(f"Charges {item}")
            continue
        for col, v in zip(CHARGE_COLS, vals):
            if v is None:
                missing.append(f"Charges {item} column {col}")
            else:
                ws[f"{col}{row}"] = v

    ws = wb["Proposal Forms"]
    for i, sub in enumerate(cfg["subs"][:4]):
        for col, v in zip("ABCDEF", sub):
            ws[f"{col}{5 + i}"] = v
    for i, ref in enumerate(cfg["references"][:3]):
        if not any(ref):
            missing.append(f"Reference {i + 1}")
        for col, v in zip("ABCDEF", ref):
            ws[f"{col}{12 + i}"] = v
    if cfg.get("assumptions"):
        ws["A17"] = cfg["assumptions"]
    else:
        missing.append("Assumptions, exceptions, and renewal terms")

    out = BID / "private" / f"{cfg['company']} - Town of Parker HVAC PM Price Workbook.xlsx"
    wb.save(out)
    print(f"wrote {out.relative_to(BID.parents[1])}")
    print("STILL MISSING:" if missing else "complete: every vendor cell filled")
    for m in missing:
        print(f"  - {m}")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
