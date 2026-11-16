#!/usr/bin/env python3
"""READ-ONLY ledger view of an outbox manifest: which entries went out, whether anyone wrote back (--inbox), and which recipients to
drop from a chase before it goes out (--skip-list).

    python3 scripts/outbox_status.py ops/outbox/2026-11-16/outbox-chases.json [--inbox] [--days N]
    python3 scripts/outbox_status.py ops/outbox/2026-11-16/outbox-chases.json --skip-list [--days N] [--write-send-copy PATH]

Default (no --inbox, no --skip-list): no network at all. One row per manifest entry: key | recipients (count of to+cc+bcc) | sent
(Gmail id from sent.json beside the manifest, or "not sent") | bcc_count from sent.json | subject (60 chars), then "N entries, M sent,
K unsent".

--inbox: for each entry also asks Gmail, read-only, for inbound mail from the entry's recipient domains (the full address for
gmail.com / comcast.net / yahoo.com / hotmail.com / outlook.com) newer than N days (default 14), never from
luke@brownbisonco.com: one messages.list and, for the newest hit, one messages.get (format=metadata, headers From/Subject/Date).
It prints the count and the newest message's date, sender DOMAIN only (never a person's mailbox) and subject. An API error on one
entry prints "inbox: error ..." and the run goes on.

--skip-list: for every recipient address across all entries (to+cc+bcc, de-duplicated, case-insensitive) two read-only searches
decide skip or keep. replied = inbound mail newer than N days (default 14) from the address's domain (the full address for the
free-mail domains above), never from luke@brownbisonco.com, the same term logic as --inbox; one messages.list per distinct term, so
a domain shared by several addresses is asked once. bounced = `from:mailer-daemon newer_than:Nd "<address>"` (Gmail's full-text
search finds the failed address inside the delivery-status report); any hit = bounced. The newest hit's day comes from one
messages.get (format=metadata). stdout carries ONLY one JSON object, so it can be piped:
    {"days": N, "skip": [addresses, sorted], "reasons": {address: "replied YYYY-MM-DD" | "bounced YYYY-MM-DD" |
     "replied+bounced YYYY-MM-DD YYYY-MM-DD"}, "checked": <addresses looked at>, "errors": {term: message}}
Progress and errors go to stderr. An API error on one term does not end the run: the term lands in "errors" (keyed "from:<term>" or
"bounce:<address>"), the run goes on, and the exit code is 1 because the skip list may be incomplete (an && chain stops there);
otherwise 0. No Gmail token at all: message on stderr, nothing on stdout, exit 1.

--write-send-copy PATH (only with --skip-list): also writes a copy of the manifest to PATH with the skip addresses removed from
to/cc/bcc of every entry; an entry left with neither to nor bcc is dropped and its key listed under "dropped_entries" in the JSON.
The input manifest is never modified. PATH must be OUTSIDE the repo's tracked ops/ tree and must not be the input manifest (exit 2,
message on stderr, before any network call): the send-time copy names mailboxes and belongs in the session scratchpad; named
mailboxes stay out of tracked files. Then run send_outbox.py on PATH from the repo root, so the entries' relative body_file and
files paths still resolve.

This script never sends, drafts, labels, trashes or modifies anything. scripts/gmail_api.py is imported only for --inbox and
--skip-list; importing it sends nothing (only its send() sends, and nothing here calls it).
"""
import argparse
import copy
import datetime as dt
import email.utils
import json
import sys
import urllib.parse
from pathlib import Path

OWNER = "luke@brownbisonco.com"
FREEMAIL = {"gmail.com", "comcast.net", "yahoo.com", "hotmail.com", "outlook.com"}   # a domain says nothing: use the address
SUBJECT_WIDTH = 60
LIST_PATH = "/gmail/v1/users/me/messages?maxResults=40&q="
GET_PATH = "/gmail/v1/users/me/messages/{id}?format=metadata&metadataHeaders=From&metadataHeaders=Subject&metadataHeaders=Date"
REPO = Path(__file__).resolve().parent.parent
TRACKED_MAIL_DIR = "ops"                 # the tracked tree a send-time copy (named mailboxes) must never land in
ERROR = "error"                          # cache marker for a search term whose API call failed


def truncate(s, n=SUBJECT_WIDTH):
    s = " ".join(str(s or "").split())
    return s if len(s) <= n else s[: n - 3] + "..."


def recipients(entry):
    """to + cc + bcc as listed in the manifest (strings only; anything malformed counts nothing)."""
    out = []
    for k in ("to", "cc", "bcc"):
        v = entry.get(k) if isinstance(entry, dict) else None
        if isinstance(v, list):
            out += [x.strip() for x in v if isinstance(x, str) and x.strip()]
    return out


def build_rows(manifest, sent):
    """One row per entry. sent is the sent.json mapping key -> {id, threadId, to, bcc_count, attachments}. Pure: no I/O."""
    rows = []
    for e in manifest:
        key = str(e.get("key") or "?") if isinstance(e, dict) else "?"
        rec = sent.get(key) if isinstance(sent, dict) else None
        rows.append({
            "key": key,
            "recipients": len(recipients(e)),
            "sent": str(rec.get("id") or "sent (no id)") if isinstance(rec, dict) else "not sent",
            "bcc_count": rec.get("bcc_count") if isinstance(rec, dict) else None,
            "subject": truncate(e.get("subject") if isinstance(e, dict) else ""),
        })
    return rows


def summary(rows):
    n_sent = sum(1 for r in rows if r["sent"] != "not sent")
    return f"{len(rows)} entries, {n_sent} sent, {len(rows) - n_sent} unsent"


def _address(s):
    """Bare lowercase address from 'Name <a@b>' or 'a@b'."""
    name, addr = email.utils.parseaddr(str(s))
    return (addr or str(s)).strip().lower()


def reply_term(address):
    """Gmail from: term for one address: its domain, or the whole address for a free-mail domain; '' when it is not an address."""
    a = _address(address)
    if "@" not in a:
        return ""
    domain = a.rpartition("@")[2]
    return a if domain in FREEMAIL else domain


def reply_terms(entry):
    """Gmail from: terms for an entry: the domain of each business address, the whole address for free-mail domains; no repeats."""
    terms = []
    for a in recipients(entry):
        t = reply_term(a)
        if t and t not in terms:
            terms.append(t)
    return terms


def reply_query(entry, days=14):
    """Gmail search for inbound mail answering this entry; '' when the entry names no recipient."""
    terms = reply_terms(entry)
    if not terms:
        return ""
    who = f"from:{terms[0]}" if len(terms) == 1 else "(" + " OR ".join(f"from:{t}" for t in terms) + ")"
    return f"{who} newer_than:{max(1, int(days))}d -from:{OWNER}"


def all_recipients(manifest):
    """Every recipient address across all entries (to+cc+bcc), bare, lower-cased, de-duplicated, sorted. Pure: no I/O."""
    seen = set()
    for e in manifest if isinstance(manifest, list) else []:
        for a in recipients(e):
            a = _address(a)
            if "@" in a:
                seen.add(a)
    return sorted(seen)


def bounce_query(address, days=14):
    """Gmail search for a delivery-status report naming this address: Gmail's full-text search matches the failed address in the
    body of the mailer-daemon message."""
    return f'from:mailer-daemon newer_than:{max(1, int(days))}d "{_address(address)}"'


def sender_domain(from_header):
    """The part after @ of a From header, and only that: 'Larry Moss <larry.moss@hoodz.us.com>' -> 'hoodz.us.com'."""
    addr = _address(from_header)
    return addr.rpartition("@")[2] if "@" in addr else "?"


def _short(e):
    msg = e.code if isinstance(e, SystemExit) else e
    return " ".join(str(msg).split())[:90] or type(e).__name__


def _when(msg, headers):
    try:
        return dt.datetime.fromtimestamp(int(msg["internalDate"]) / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%MZ")
    except (KeyError, TypeError, ValueError):
        return headers.get("date", "?")[:25]


def _day(msg, headers):
    """YYYY-MM-DD (UTC) of a message: internalDate first, else its Date header, else '?'."""
    try:
        return dt.datetime.fromtimestamp(int(msg["internalDate"]) / 1000, dt.timezone.utc).strftime("%Y-%m-%d")
    except (KeyError, TypeError, ValueError):
        pass
    try:
        return email.utils.parsedate_to_datetime(headers.get("date", "")).astimezone(dt.timezone.utc).strftime("%Y-%m-%d")
    except (TypeError, ValueError, AttributeError, OverflowError):
        return "?"


def _headers(detail):
    return {x["name"].lower(): x["value"] for x in (detail.get("payload") or {}).get("headers", [])}


def check_inbox(entry, days, token, call):
    """Read-only reply check through `call` (gmail_api.call or a stand-in): messages.list, then messages.get on the newest hit.
    -> {"count", "more", "newest": None | {"date", "domain", "subject"}} or {"error": str}. Never raises."""
    q = reply_query(entry, days)
    if not q:
        return {"error": "no recipients in entry"}
    try:
        res = call("GET", LIST_PATH + urllib.parse.quote(q), token) or {}
        msgs = res.get("messages") or []
        out = {"count": len(msgs), "more": bool(res.get("nextPageToken")), "newest": None}
        if msgs:                                                  # Gmail lists newest first
            d = call("GET", GET_PATH.format(id=msgs[0]["id"]), token) or {}
            h = _headers(d)
            out["newest"] = {"date": _when(d, h), "domain": sender_domain(h.get("from", "")), "subject": truncate(h.get("subject", ""))}
        return out
    except (Exception, SystemExit) as e:                          # gmail_api.call() exits on an HTTP error; one entry must not end the run
        return {"error": _short(e)}


def format_inbox(r, days):
    if "error" in r:
        return f"inbox: error {r['error']}"
    n = f"{r['count']}{'+' if r.get('more') else ''}"
    if not r.get("newest"):
        return f"inbox: {n} inbound in {days}d"
    w = r["newest"]
    return f"inbox: {n} inbound in {days}d; newest {w['date']} from {w['domain']}: {w['subject']}"


def decide_skips(manifest, days, call, token, log=None):
    """Skip/keep for every recipient address in the manifest, through read-only Gmail searches via `call` (gmail_api.call or a
    stand-in). One messages.list per distinct search term (cached, so a shared domain is asked once) and one messages.get for the
    newest hit's day. -> {"days", "skip": [sorted], "reasons": {address: why}, "checked": n, "errors": {term: msg}}. A failing term is
    recorded under errors and the run goes on; never raises. `log` (optional) gets progress lines for stderr."""
    days = max(1, int(days))
    addresses = all_recipients(manifest)
    cache, errors = {}, {}
    say = log or (lambda m: None)
    say(f"skip-list: {len(addresses)} addresses, {days}d window")

    def newest_day(label, q):
        """Day of the newest hit for the query, None for no hit, ERROR on an API failure; one lookup per label."""
        if label not in cache:
            try:
                res = call("GET", LIST_PATH + urllib.parse.quote(q), token) or {}
                msgs = res.get("messages") or []
                day = None
                if msgs:                                          # Gmail lists newest first
                    d = call("GET", GET_PATH.format(id=msgs[0]["id"]), token) or {}
                    day = _day(d, _headers(d))
                cache[label] = day
            except (Exception, SystemExit) as e:                  # gmail_api.call() exits on an HTTP error; one term must not end the run
                errors[label] = _short(e)
                cache[label] = ERROR
                say(f"skip-list: error on {label}: {errors[label]}")
        return cache[label]

    skip, reasons = [], {}
    for a in addresses:
        replied = newest_day(f"from:{reply_term(a)}", reply_query({"to": [a]}, days))
        bounced = newest_day(f"bounce:{a}", bounce_query(a, days))
        why = [(w, d) for w, d in (("replied", replied), ("bounced", bounced)) if d and d != ERROR]
        if why:
            skip.append(a)
            reasons[a] = "+".join(w for w, _ in why) + " " + " ".join(d for _, d in why)
    say(f"skip-list: skip {len(skip)} of {len(addresses)}, {len(errors)} term error(s)")
    return {"days": days, "skip": sorted(skip), "reasons": reasons, "checked": len(addresses), "errors": errors}


def apply_skips(manifest, skip):
    """A new manifest with the skip addresses (case-insensitive) removed from to/cc/bcc of every entry; a list emptied this way is
    dropped from the entry, and an entry left with neither to nor bcc is dropped. -> (new_manifest, dropped_keys). The input is not
    modified (deep copies). Pure: no I/O."""
    skipset = {_address(s) for s in skip}
    out, dropped = [], []
    for e in manifest:
        if not isinstance(e, dict):
            out.append(copy.deepcopy(e))
            continue
        n = copy.deepcopy(e)
        for k in ("to", "cc", "bcc"):
            if isinstance(n.get(k), list):
                n[k] = [x for x in n[k] if not (isinstance(x, str) and _address(x) in skipset)]
                if not n[k]:
                    del n[k]
        if n.get("to") or n.get("bcc"):
            out.append(n)
        else:
            dropped.append(str(e.get("key") or "?"))
    return out, dropped


def send_copy_problem(path, manifest_path=None, repo=REPO):
    """'' when PATH may hold the send-time copy, else why not: inside the repo's tracked ops/ tree (named mailboxes stay out of
    tracked files; the copy belongs in the session scratchpad), the input manifest itself, or a directory."""
    p = Path(str(path)).expanduser()
    try:
        r = p.resolve()
    except (OSError, RuntimeError):
        r = p.absolute()
    tracked = (Path(repo) / TRACKED_MAIL_DIR).resolve()
    if r == tracked or tracked in r.parents or (not p.is_absolute() and p.parts[:1] == (TRACKED_MAIL_DIR,)):
        return (f"refusing to write the send copy under {tracked}: it names mailboxes, and named mailboxes stay out of tracked files. "
                "Write it in the session scratchpad instead.")
    if manifest_path is not None and r == Path(str(manifest_path)).expanduser().resolve():
        return "refusing to overwrite the input manifest: the send copy goes to a different path"
    if r.is_dir():
        return f"{r} is a directory; give a file path"
    return ""


def _gmail():
    """scripts/gmail_api.py beside this file, loaded only for --inbox / --skip-list. Importing it sends nothing."""
    here = str(Path(__file__).resolve().parent)
    if here not in sys.path:
        sys.path.insert(0, here)
    import gmail_api                                               # noqa: WPS433  (deliberately lazy)
    return gmail_api


def _err(msg):
    print(f"outbox_status: {msg}", file=sys.stderr)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Read-only ledger view of an outbox manifest (never sends).")
    ap.add_argument("manifest", help="outbox manifest .json; sent.json is read from the same folder when present")
    ap.add_argument("--inbox", action="store_true", help="also look for inbound replies (read-only Gmail list/get)")
    ap.add_argument("--days", type=int, default=14, help="window in days for --inbox and --skip-list (default 14)")
    ap.add_argument("--skip-list", action="store_true",
                    help="JSON on stdout: recipients who replied or bounced within --days (read-only Gmail list/get), nothing else")
    ap.add_argument("--write-send-copy", metavar="PATH",
                    help="with --skip-list: write the manifest minus the skip addresses to PATH (outside ops/, e.g. the scratchpad)")
    a = ap.parse_args(argv)
    if a.write_send_copy and not a.skip_list:
        ap.error("--write-send-copy needs --skip-list")
    manifest_path = Path(a.manifest)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    if a.skip_list:
        if a.write_send_copy:
            why = send_copy_problem(a.write_send_copy, manifest_path)
            if why:
                _err(why)
                return 2
        gm = _gmail()
        try:
            token, call = gm.access_token(), gm.call
        except (Exception, SystemExit) as e:
            _err(f"no Gmail token, no skip list: {_short(e)}")
            return 1
        result = decide_skips(manifest, a.days, call, token, log=_err)
        if a.write_send_copy:
            new, dropped = apply_skips(manifest, result["skip"])
            p = Path(a.write_send_copy).expanduser()
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(new, indent=1) + "\n", encoding="utf-8")
            result["dropped_entries"] = dropped
            _err(f"send copy written: {p} ({len(new)} entries kept, {len(dropped)} dropped)")
        print(json.dumps(result, indent=1))
        if result["errors"]:
            _err(f"{len(result['errors'])} search term(s) failed; the skip list may be incomplete (exit 1)")
            return 1
        return 0

    sent_path = manifest_path.with_name("sent.json")
    sent = json.loads(sent_path.read_text(encoding="utf-8")) if sent_path.exists() else {}
    rows = build_rows(manifest, sent)

    token = call = None
    tok_err = ""
    if a.inbox:
        gm = _gmail()
        try:
            token, call = gm.access_token(), gm.call
        except (Exception, SystemExit) as e:
            tok_err = _short(e)

    kw = min(max([3] + [len(r["key"]) for r in rows]), 40)
    print(f"{'key':<{kw}} | rcpts | {'sent':<16} | bcc | subject")
    for e, r in zip(manifest, rows):
        bcc = "-" if r["bcc_count"] is None else str(r["bcc_count"])
        print(f"{r['key'][:kw]:<{kw}} | {r['recipients']:>5} | {r['sent']:<16} | {bcc:>3} | {r['subject']}")
        if a.inbox:
            res = {"error": tok_err} if tok_err else check_inbox(e, a.days, token, call)
            print(" " * 4 + format_inbox(res, max(1, a.days)))
    print(summary(rows) + ("" if sent_path.exists() else f"  (no {sent_path.name} beside the manifest)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
