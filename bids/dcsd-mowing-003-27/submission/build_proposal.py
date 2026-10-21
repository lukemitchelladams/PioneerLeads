"""Assemble the DCSD RFP 003-27 proposal (proposal.md + scope table + Appendices A-C) into one Word file.

    python3 bids/dcsd-mowing-003-27/submission/build_proposal.py --draft   # review copy for YMS / Luke, markers highlighted
    python3 bids/dcsd-mowing-003-27/submission/build_proposal.py --draft --for-sub   # same, plus YMS's own prices
    python3 bids/dcsd-mowing-003-27/submission/build_proposal.py           # submission copy; refuses while markers remain

Markers: ⟦...⟧ = only YMS or Luke can supply (yellow), ⟪...⟫ = our proposed wording or number (green; accepted
and unmarked in the submission copy). {{DATE}} becomes the build date (Mountain Time).
Output goes to private/ (git-ignored).
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

import docx
from docx.enum.text import WD_COLOR_INDEX

HERE = Path(__file__).resolve().parent
BID = HERE.parent
PARTS = ["appendix-a-safety.md", "appendix-b-quality-control.md", "appendix-c-crews-route.md"]
PAGE_BREAK = '\n\n```{=openxml}\n<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n```\n\n'
DRAFT = "--draft" in sys.argv
FOR_SUB = "--for-sub" in sys.argv
OUT = BID / "private" / ("DRAFT for YMS review - DCSD 003-27 Proposal (your prices).docx" if FOR_SUB
                         else "DRAFT for YMS review - DCSD 003-27 Proposal.docx" if DRAFT
                         else "Brown Bison Holdings LLC - DCSD 003-27 Proposal.docx")
BANNER = ("**DRAFT for review, not yet submitted.** Yellow = information only YMS (or Luke) can supply. "
          "Green = our suggested wording or number; say if you want it changed. Prices are on the separate price sheet.\n\n")


def highlight(path: Path) -> dict:
    d = docx.Document(str(path))

    def paragraphs():
        yield from d.paragraphs
        for t in d.tables:
            for row in t.rows:
                for c in row.cells:
                    yield from c.paragraphs

    n = {"yellow": 0, "green": 0}
    for p in paragraphs():
        state = None
        for r in p.runs:
            t = r.text
            if state is None:
                state = "yellow" if "⟦" in t else "green" if "⟪" in t else None
            if state:
                r.font.highlight_color = WD_COLOR_INDEX.YELLOW if state == "yellow" else WD_COLOR_INDEX.BRIGHT_GREEN
                n[state] += 1
                close, opener = ("⟧", "⟦") if state == "yellow" else ("⟫", "⟪")
                if t.rfind(close) > t.rfind(opener):
                    state = None
    d.save(str(path))
    return n


def sub_prices() -> str:
    """YMS's own prices (no markup) from private/alex_prices.json, as markdown tables for YMS's sign-off copy."""
    import json
    cfg = json.loads((BID / "private" / "alex_prices.json").read_text())
    money = lambda x: f"${x:,.2f}"
    sites = cfg["sites"]
    a = ["| Site | Turf / week | Rock beds / week | Mulch beds / week | Edging / month | Native / month |",
         "|------------|-------|-------|-------|-------|-------|"]
    b = ["| Site | Aeration (once) | Fertilization (once) | Broadleaf (once) | Season total (27 weeks) | Extra athletic mow, each |",
         "|------------|-------|-------|-------|--------|-------|"]
    for name, s in sites.items():
        a.append(f"| {name} | {money(s['turf_weekly'])} | {money(s['rock_weekly'])} | {money(s['mulch_weekly'])} | "
                 f"{money(s['edging_monthly'])} | {money(s['native_monthly'])} |")
        b.append(f"| {name} | {money(s['aeration'])} | {money(s['fertilization'])} | {money(s['broadleaf'])} | "
                 f"{money(s['alex_season_total'])} | {money(s['extra_athletic_mow'])} |")
    total = sum(s["alex_season_total"] for s in sites.values())
    b.append(f"| **All 19 sites** | | | | **{money(total)}** | |")
    rates = ["| Additional service | Unit | Your rate |", "|--------------------|----------|------|"]
    for desc, unit, rate in cfg["additional_services"]:
        rates.append(f"| {desc} | {unit} | ${rate:,.4f} |" if rate < 1 and rate else f"| {desc} | {unit} | {money(rate)} |")
    return ("\n\n## Your prices for approval\n\n"
            "These are YMS's own prices exactly as you sent them on 2026-10-19, placed in the District's columns. "
            "Brown Bison's markup is added only on the copy we submit.\n\n"
            + "\n".join(a) + "\n\n" + "\n".join(b) + "\n\n" + "\n".join(rates) + "\n")


def main() -> int:
    body = (HERE / "proposal.md").read_text()
    if FOR_SUB:
        marker = "Prices exclude taxes from which DCSD is exempt."
        assert body.count(marker) == 1
        body = body.replace(marker, marker + sub_prices())
    body = re.sub(r"<!--.*?-->\n*", "", body, flags=re.S)
    body = body.replace("{{DATE}}", datetime.now(ZoneInfo("America/Denver")).strftime("%B %-d, %Y"))
    body = body.replace("SCOPE_RESPONSE_TABLE", (HERE / "scope_response_table.md").read_text().strip())
    for part in PARTS:
        body += PAGE_BREAK + (HERE / part).read_text().strip() + "\n"
    if DRAFT:
        head, sep, rest = body.partition("---\n\n")
        body = head + sep + BANNER + rest if sep and body.startswith("---") else BANNER + body
    else:
        left = re.findall(r"⟦[^⟧]*⟧", body)
        if left:
            print(f"{len(left)} open items still marked; not building the submission copy:")
            for x in left:
                print("  ", x)
            return 1
    if not DRAFT:
        body = body.replace("⟪", "").replace("⟫", "")  # our proposed wording, accepted
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(body)
    subprocess.run(["pandoc", f.name, "-f", "markdown", "-o", str(OUT)], check=True)
    n = highlight(OUT)
    print(f"wrote {OUT.relative_to(BID.parents[1])} ({OUT.stat().st_size:,} bytes; highlighted runs {n})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
