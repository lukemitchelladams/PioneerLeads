"""Amendment watch on GO bids: a new SAM.gov notice version, a moved due date or new attachments on a federal solicitation we bid.

Why (2026-11-21): Reclamation 140RR027Q0001, a GO bid, got Amendment 0003 on SAM.gov at 22:09Z; it moved the due date and
replaced the price schedule. SAM.gov gives each amendment version a new notice id, so the scanner listed it as one more "new"
notice row and nobody noticed for 7.5 hours.

Every scan (run.py, before the public search's own pass, so GO bids come first out of the shared request budget):
  * the pipeline.json rows whose decision starts GO / GO-IF (GO_DECISION_RX) and whose "sol", else "title", holds a federal
    solicitation number (FEDERAL_SOL_RX: 140RR027Q0001, 36C25927Q0048, 127EAX27Q0015, 1240LP27Q0008);
  * for each, the keyless public search (samgov_public) by that number, one request; the newest notice whose solicitationNumber
    is that number (latest modifiedDate) is compared with the last one seen, kept in bids/_watch/amendment_state.json (per
    solicitation: notice id, modifiedDate, responseDate, attachment names);
  * first sight records the state (and the attachment names, one more request), no alert;
  * a new notice id, a moved responseDate, or attachment names not seen before is an alert: "AMENDMENT: 140RR027Q0001 due
    2026-12-04T14:00-07:00 -> 2026-12-09T11:00-07:00 (new notice c07d00c2...)", which run.py puts first in REPORT.md's headline
    and under "## Amendments on GO bids";
  * when the row names a bid folder, the new "file" attachments are downloaded into <folder>/docs/, and so is a file replaced
    under a name already seen (new resource id, different size; saved beside the earlier one as "<name> (rev <date>)"): a name
    already there is skipped, at most MAX_FILES files / MAX_BYTES a run, every request out of the scan's samgov_public.Budget
    (BIDWATCH_SAM_PUBLIC_MAX). A file not fetched this run (cap, HTTP error) stays "pending" and is tried again next scan.
The attachment list is read only on first sight, on a change (notice id, modifiedDate, responseDate), or while files are pending,
so a quiet scan costs one request per solicitation. Never raises: a failure is a line in the result's "errors".
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
from pathlib import Path

from . import samgov, samgov_public
from .common import REPO, WATCH_DIR, load_json, save_json

STATE_FILE = WATCH_DIR / "amendment_state.json"
GO_DECISION_RX = re.compile(r"\s*(?:GO(?:[ -]?IF)?|SUBMITTED)\b", re.I)  # "GO", "GO (HQ ...)", "GO-IF (...)", "GO-IF BONDED", "SUBMITTED" (an amendment after submission must still be acknowledged); not "EVALUATE"
# A federal solicitation number written whole: 10-17 upper-case letters and digits, both present, not part of a longer word or
# of a hyphenated number (a Colorado VSS "DQ1-PMAA-2027000176-1", a BidNet "0000443963" or a 32-hex notice id never match).
FEDERAL_SOL_RX = re.compile(r"(?<![A-Za-z0-9-])(?=[A-Z0-9]*[A-Z])(?=[A-Z0-9]*\d)[A-Z0-9]{10,17}(?![A-Za-z0-9-])")
SEARCH_SIZE = 25
MAX_FILES = 10  # downloads a run, every GO solicitation together
MAX_BYTES = 25 * 1024 * 1024
ABOUT = ("Amendment watch (scripts/bidwatch/amendments.py): the newest SAM.gov notice seen per GO / GO-IF federal solicitation. "
         "Written by the scanner; a new notice id, a moved responseDate or new attachment names is an AMENDMENT alert in REPORT.md.")
_EPOCH = dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)


def federal_sol(text) -> str | None:
    """The first federal solicitation number in `text` (FEDERAL_SOL_RX), or None."""
    m = FEDERAL_SOL_RX.search(str(text or ""))
    return m.group(0) if m else None


def _sol_key(s) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(s or "").upper())


def _folder(f) -> str | None:
    """A pipeline row's "folder" as a repo-relative path under bids/ ("bids/x" or "x" -> "bids/x"), or None (blank, absolute, ..)."""
    f = str(f or "").strip().strip("/")
    if not f:
        return None
    p = Path(f)
    if p.is_absolute() or ".." in p.parts:
        return None
    return str(p if p.parts[0] == "bids" else Path("bids") / p)


def targets(rows) -> list[dict]:
    """[{sol, folder, title}] for the pipeline rows decided GO / GO-IF whose "sol" (else "title") holds a federal solicitation
    number, one per number (a later row of the same number lends its folder when the first has none)."""
    out: dict[str, dict] = {}
    for p in rows or []:
        if not isinstance(p, dict) or not GO_DECISION_RX.match(str(p.get("decision") or "")):
            continue
        sol = federal_sol(p.get("sol")) or federal_sol(p.get("title"))
        if not sol:
            continue
        t = out.setdefault(sol, {"sol": sol, "folder": None, "title": p.get("title") or ""})
        t["folder"] = t["folder"] or _folder(p.get("folder"))
    return list(out.values())


def search_notices(sol: str, budget, fetch=None) -> list[dict]:
    """The active notices the public search returns for `sol` whose solicitationNumber is `sol` (letters and digits compared, any
    case), raw. One budgeted request; raises on failure (samgov_public.CapReached included)."""
    params = {"index": "opp", "page": 0, "size": SEARCH_SIZE, "sort": "-modifiedDate", "is_active": "true", "q": sol}
    data = samgov_public._json(samgov_public._request(samgov_public._url(params), budget, fetch))
    want = _sol_key(sol)
    return [x for x in (data.get("_embedded") or {}).get("results") or []
            if isinstance(x, dict) and x.get("_id") and _sol_key(x.get("solicitationNumber")) == want]


def newest(results: list[dict]) -> dict | None:
    """The latest version: greatest modifiedDate, then publishDate."""
    def k(x):
        return (samgov_public._when(x.get("modifiedDate")) or _EPOCH, samgov_public._when(x.get("publishDate")) or _EPOCH)
    return max(results, key=k) if results else None


def _snapshot(x: dict) -> dict:
    return {"notice_id": str(x.get("_id") or ""), "modifiedDate": x.get("modifiedDate"), "responseDate": x.get("responseDate"),
            "responseDateActual": x.get("responseDateActual"), "title": x.get("title") or "",
            "type": x["type"].get("value") if isinstance(x.get("type"), dict) else x.get("type"),
            "canceled": bool(x.get("isCanceled"))}


def _due(s: dict):
    return s.get("responseDate") or s.get("responseDateActual")


def _same_time(a, b) -> bool:
    """Two response dates name the same moment (a format change, "Z" for "+00:00", is not a move)."""
    if a == b:
        return True
    ta, tb = samgov_public._when(a), samgov_public._when(b)
    return ta is not None and tb is not None and ta == tb


def due_text(s: dict) -> str:
    """A snapshot's response date to the minute in the notice's own zone (responseDateActual, else responseDate):
    '2026-12-04T14:00-07:00'; 'none' without one."""
    v = s.get("responseDateActual") or s.get("responseDate")
    if not v:
        return "none"
    try:
        return dt.datetime.fromisoformat(str(v).replace("Z", "+00:00")).isoformat(timespec="minutes")
    except ValueError:
        return str(v)


def alert_line(sol: str, old: dict, new: dict, new_id: bool, moved: bool, new_names: list, replaced: list) -> str:
    """'AMENDMENT: 140RR027Q0001 due 2026-12-04T14:00-07:00 -> 2026-12-09T11:00-07:00 (new notice c07d00c2...)': the due date
    when it moved, the notice id, the count of new / replaced attachments, CANCELLED when the newest notice cancels it."""
    nid = f"{str(new.get('notice_id'))[:8]}..."
    extra = ([f"{len(new_names)} new attachment{'s' if len(new_names) != 1 else ''}"] if new_names else []) \
        + ([f"{len(replaced)} replaced"] if replaced else [])
    if moved:
        tag = ("new notice " if new_id else "notice ") + nid
        line = f"AMENDMENT: {sol} due {due_text(old)} -> {due_text(new)} ({', '.join([tag] + extra)})"
    elif new_id:
        line = f"AMENDMENT: {sol} new notice {nid} ({', '.join([f'due {due_text(new)} unchanged'] + extra)})"
    else:
        line = f"AMENDMENT: {sol} {', '.join(extra)} on notice {nid} (due {due_text(new)} unchanged)"
    return line + (" CANCELLED" if new.get("canceled") else "")


class _Allowance:
    """The run's download allowance: MAX_FILES files, MAX_BYTES bytes, every solicitation together."""

    def __init__(self):
        self.files = 0
        self.bytes = 0


def _att_name(a: dict) -> str:
    return str(a.get("name") or a.get("resourceId") or "?")


def _pending(v) -> list[list[str]]:
    """The state's pending downloads as [[attachment name, file name], ...] (a bare name, from a hand edit, is its safe name)."""
    out = []
    for p in v or []:
        if isinstance(p, (list, tuple)) and len(p) == 2 and all(isinstance(x, str) for x in p):
            out.append([p[0], p[1]])
        elif isinstance(p, str):
            out.append([p, samgov_public.safe_name(p) or p])
    return out


def _download(nid: str, todo: list[tuple[dict, str]], dest: Path, budget, allow: _Allowance, fetch=None) -> dict:
    """Fetch each (attachment, file name) of `todo` into `dest`, skipping a file name already there (or, under its own name, the
    same file a person saved with a prefix: samgov_public.in_hand). Returns {"saved": [paths], "pending": [[name, file name]]
    to try next scan, "errors": [lines], "stopped": why the budget refused, or None}."""
    out = {"saved": [], "pending": [], "errors": [], "stopped": None}
    view = samgov_public.VIEW_URL.format(nid=nid)
    for i, (a, fn) in enumerate(todo):
        name = _att_name(a)
        if (dest / fn).exists() or (fn == samgov_public.safe_name(name) and samgov_public.in_hand(a, [dest])):
            continue  # in hand
        size = samgov_public._size(a)
        if size is not None and size > MAX_BYTES:
            out["errors"].append(f"{name}: {size} bytes, over the {MAX_BYTES // 2**20} MB a scan cap; download it from {view}")
            continue
        if allow.files >= MAX_FILES or (size is not None and allow.bytes + size > MAX_BYTES):
            out["pending"].append([name, fn])
            continue
        try:
            body = samgov_public._request(samgov_public.DOWNLOAD_API.format(rid=a.get("resourceId")), budget, fetch)
        except samgov_public.CapReached as e:
            out["stopped"] = str(e)
            out["pending"] += [[_att_name(x), f] for x, f in todo[i:]]
            break
        except Exception as e:  # noqa: BLE001 - this file only; tried again next scan
            out["errors"].append(f"{name}: {samgov._err_text(e)} (tried again next scan)")
            out["pending"].append([name, fn])
            continue
        why = samgov_public._bad_body(body, a)
        if not why:
            try:
                dest.mkdir(parents=True, exist_ok=True)
                tmp = dest / (fn + ".part")
                tmp.write_bytes(body)
                os.replace(tmp, dest / fn)
            except OSError as e:
                why = f"not saved: {type(e).__name__}: {str(e)[:120]}"
        if why:
            out["errors"].append(f"{name}: {why}")
            out["pending"].append([name, fn])
            continue
        allow.files += 1
        allow.bytes += len(body)
        out["saved"].append(dest / fn)
    return out


def _attachments(sol: str, old: dict, new: dict, folder: str | None, repo: Path, budget, allow: _Allowance, now: str,
                 fetch=None) -> dict:
    """Read the newest notice's attachment list and download what is new (into `folder`/docs/ when the row names one). Returns
    {"listed": bool, "names", "files" (name -> [resource id, size]), "new_names", "replaced", "saved", "pending", "errors",
    "stopped"}. When the list cannot be read, "names" / "files" / "pending" are the earlier ones (read again next scan)."""
    names = old.get("attachments") if isinstance(old.get("attachments"), list) else None
    files = old.get("files") if isinstance(old.get("files"), dict) else {}
    out = {"listed": False, "names": names, "files": files, "new_names": [], "replaced": [], "saved": [],
           "pending": _pending(old.get("pending")), "errors": [], "stopped": None}
    try:
        live = [a for a in samgov_public.list_attachments(new["notice_id"], budget, fetch) if str(a.get("deletedFlag") or "0") != "1"]
    except samgov_public.CapReached as e:
        out["stopped"] = str(e)
        return out
    except Exception as e:  # noqa: BLE001
        out["errors"].append(f"attachment list: {samgov._err_text(e)} (read again next scan)")
        return out
    by_name: dict[str, dict] = {}
    for a in live:
        by_name.setdefault(_att_name(a), a)
    if names is not None:  # an earlier list is known: what it lacks is new
        out["new_names"] = [n for n in by_name if n not in names]
        for n, a in by_name.items():
            was = files.get(n) if isinstance(files.get(n), list) and len(files.get(n)) == 2 else None
            size = samgov_public._size(a)
            if n in names and was and was[0] and a.get("resourceId") and a["resourceId"] != was[0] \
                    and size is not None and was[1] is not None and size != was[1]:
                out["replaced"].append(n)  # the same name, another upload: a replaced document
    out.update(listed=True, names=list(by_name), files={n: [a.get("resourceId"), samgov_public._size(a)] for n, a in by_name.items()},
               pending=[])
    if not folder:
        return out
    if not (repo / folder).is_dir():
        if out["new_names"] or out["replaced"]:
            out["errors"].append(f"bid folder {folder} not found; new attachments not downloaded")
        return out
    docs = repo / folder / "docs"
    todo, seen = [], set()
    wanted = [(n, None) for n in out["new_names"] + out["replaced"]] + [(n, f) for n, f in _pending(old.get("pending"))]
    for n, fn in wanted:
        a = by_name.get(n)
        if a is None or n in seen:
            continue  # no longer posted, or listed twice
        seen.add(n)
        if a.get("type") != "file" or not a.get("resourceId"):
            continue  # a web link: nothing to fetch (the alert names it)
        if str(a.get("accessLevel") or "public").lower() != "public":
            out["errors"].append(f"{n}: not public on SAM.gov (request access on the notice page)")
            continue
        if not fn:
            fn = samgov_public.safe_name(n) or str(a["resourceId"])
            if n in out["replaced"] and (docs / fn).exists():  # the earlier file stays; the replacement goes beside it
                p = Path(fn)
                fn = f"{p.stem} (rev {now[:10]}){p.suffix}"
        todo.append((a, fn))
    got = _download(new["notice_id"], todo, docs, budget, allow, fetch)
    out.update(saved=got["saved"], pending=got["pending"], stopped=got["stopped"])
    out["errors"] += got["errors"]
    return out


def check(rows, state: dict, budget, repo: Path = REPO, fetch=None, now: str | None = None) -> dict:
    """The watch over pipeline `rows` against `state` ({sol: last seen}), updated in place. Returns {"alerts": [{sol, folder,
    title, line, old_notice, new_notice, old_due, new_due, new_attachments, replaced, saved, pending, url}], "errors": [lines],
    "saved": [repo-relative paths], "folders": [bid folders that got files], "stats": {...}}. An HTTP error is a line and the next
    solicitation goes on; a refused request (the budget's cap, or sam.gov down) ends the pass with one line."""
    now = now or dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    plan = targets(rows)
    stats = {"solicitations": len(plan), "checked": 0, "first_sight": 0, "not_found": [], "alerts": 0, "downloaded": 0}
    res = {"alerts": [], "errors": [], "saved": [], "folders": [], "stats": stats}
    allow = _Allowance()
    used0 = budget.used
    for i, t in enumerate(plan):
        sol, folder = t["sol"], t["folder"]
        try:
            x = newest(search_notices(sol, budget, fetch))
        except samgov_public.CapReached as e:
            res["errors"].append(f"amendment watch: {e}; {len(plan) - i} of {len(plan)} GO solicitations wait for the next scan")
            break
        except Exception as e:  # noqa: BLE001 - one line, then the next solicitation
            res["errors"].append(f"amendment watch {sol}: search: {samgov._err_text(e)}")
            continue
        if x is None:
            stats["not_found"].append(sol)
            continue
        stats["checked"] += 1
        new = _snapshot(x)
        old = state.get(sol) if isinstance(state.get(sol), dict) else {}
        first = not old.get("notice_id")
        stats["first_sight"] += first
        new_id = not first and new["notice_id"] != old["notice_id"]
        moved = not first and not _same_time(_due(old), _due(new))
        att = {"listed": False, "names": old.get("attachments"), "files": old.get("files") or {}, "new_names": [],
               "replaced": [], "saved": [], "pending": _pending(old.get("pending")), "errors": [], "stopped": None}
        if first or new_id or moved or new["modifiedDate"] != old.get("modifiedDate") or att["pending"] or old.get("relist") \
                or not isinstance(old.get("attachments"), list):
            att = _attachments(sol, old, new, folder, repo, budget, allow, now, fetch)
            if att["stopped"]:
                res["errors"].append(f"amendment watch {sol}: {att['stopped']}; attachments read again next scan")
        res["errors"] += [f"amendment watch {sol}: {e}" for e in att["errors"]]
        rel = [str(p.relative_to(repo)) if p.is_relative_to(repo) else str(p) for p in att["saved"]]
        res["saved"] += rel
        stats["downloaded"] += len(rel)
        if rel and folder not in res["folders"]:
            res["folders"].append(folder)
        rec = {**new, "attachments": att["names"], "files": att["files"], "pending": att["pending"],
               "relist": not att["listed"] and bool(att["stopped"] or att["errors"] or old.get("relist")), "folder": folder,
               "first_seen": old.get("first_seen") or now, "changed_at": old.get("changed_at"), "last_alert": old.get("last_alert")}
        if new_id or moved or att["new_names"] or att["replaced"]:
            a = {"sol": sol, "folder": folder, "title": new["title"] or t["title"],
                 "line": alert_line(sol, old, new, new_id, moved, att["new_names"], att["replaced"]),
                 "old_notice": old.get("notice_id"), "new_notice": new["notice_id"], "old_due": due_text(old),
                 "new_due": due_text(new), "new_attachments": att["new_names"], "replaced": att["replaced"], "saved": rel,
                 "pending": [n for n, _ in att["pending"]], "url": samgov_public.VIEW_URL.format(nid=new["notice_id"])}
            res["alerts"].append(a)
            stats["alerts"] += 1
            rec["changed_at"], rec["last_alert"] = now, a["line"]
        state[sol] = rec
    stats["requests"] = budget.used - used0
    return res


def watch(rows, budget, state_file: Path = STATE_FILE, repo: Path = REPO, fetch=None, now: str | None = None) -> dict:
    """check() with the state loaded from and saved to `state_file` (written only when it changed). Returns check()'s result
    plus "state_written" (bool). Never raises: anything unexpected is one line in "errors"."""
    out = {"alerts": [], "errors": [], "saved": [], "folders": [], "stats": {}, "state_written": False}
    try:
        data = load_json(Path(state_file), {})
        data = data if isinstance(data, dict) else {}
        sols = data.get("solicitations") if isinstance(data.get("solicitations"), dict) else {}
        before = json.dumps(sols, sort_keys=True, default=str)
        out.update(check(rows, sols, budget, repo=repo, fetch=fetch, now=now))
        if json.dumps(sols, sort_keys=True, default=str) != before:
            save_json(Path(state_file), {"_about": ABOUT, "solicitations": sols})
            out["state_written"] = True
    except Exception as e:  # noqa: BLE001 - never into the scan
        out["errors"].append(f"amendment watch: {type(e).__name__}: {str(e)[:150]}")
    return out
