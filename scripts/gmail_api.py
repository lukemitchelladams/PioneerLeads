#!/usr/bin/env python3
"""Send mail with attachments, and save attachments, through the Gmail API (HTTPS), as luke@brownbisonco.com.

The Gmail connector cannot carry multi-MB attachments and SMTP is blocked in cloud sessions, so this talks to
gmail.googleapis.com directly. Credentials come from the environment only (set once in the cloud environment's
settings, never pasted in chat, never written to the repo):

    GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_REFRESH_TOKEN

Get the refresh token once on Luke's Mac with:  python3 scripts/gmail_api.py token <client_secret.json>

HUMANIZE GATE (Luke's hard rule, 2026-11-05): before attachments are read and before any token or network call, `send`
runs scripts/humanize_gate.py on the body file (hz.py lint from the /humanize skill plus the gate's own rules), the subject
and the attachment types, unless every recipient is Luke's own address. On a FAIL it prints "HUMANIZE: ..." to stderr and
exits 3; nothing is sent. There is no bypass flag. --no-signature is refused for anyone but Luke. A body file opens with
"Hi <FirstName>," ("Hi Team," for group mail) and ENDS at "Thanks <FirstName>," ("Thanks Team,"): this script appends
SIGNATURE (title Operations Manager, Luke 2026-10-18; four lines, no phone, Luke 2026-11-06). No links, no .txt/.html/.eml
attachments to outside recipients. PHONE (Luke 2026-11-06): no cell number in any format and no invitation to call ("call me",
"give us a call", "my cell", "hop on a call" ...) in the body, subject or signature; answer by email, at most adding "Email is
the best way to reach me during the day." Trade words (on-call, service call, call-out, callback time) are fine.
--asks N raises the word budget only with the email being answered: --asks-from INBOUND.txt (asks = min(N, its '?' count));
without it asks is capped at 1. Check a body first: python3 scripts/humanize_gate.py check body.txt --asks-from inbound.txt
call() refuses a POST to .../messages/send or .../drafts/send that send() did not build after the gate passed.

Usage (attachments go after a literal --):
    python3 scripts/gmail_api.py send --to a@x.com [--bcc b@y.com ...] --subject "..." --body-file body.txt -- FILE...
    python3 scripts/gmail_api.py send --thread <threadId> --to a@x.com --subject "Re: ..." --body-file b.txt \
        --asks-from inbound.txt -- FILE...
    python3 scripts/gmail_api.py save <messageId> <out_dir>      # download every attachment on a message
    python3 scripts/gmail_api.py check                           # verify the token works (prints the address only)
"""
import argparse
import base64
import hashlib
import importlib.util
import json
import mimetypes
import os
import re
import sys
import urllib.parse
import urllib.request
from email.message import EmailMessage
from pathlib import Path

API = "https://gmail.googleapis.com"
SENDER = "luke@brownbisonco.com"
SCOPES = "https://www.googleapis.com/auth/gmail.modify"
# Luke 2026-10-18: the title is Operations Manager on every email, never Owner/CEO/General Manager/Sales Manager.
# Luke 2026-11-06: no phone line in email ("i cant have all these ... guys calling me all ... day long"). Four lines: brand.py's
# NAME, TITLE, COMPANY, EMAIL (its PHONE stays for bid forms and proposals only), after one blank line.
SIGNATURE_LINES = ("Luke Adams", "Operations Manager", "Brown Bison Holdings LLC", "luke@brownbisonco.com")
SIGNATURE = "\n\n" + "\n".join(SIGNATURE_LINES) + "\n"
MAX_ASKS = 20                                   # same cap as humanize_gate.MAX_ASKS
GATE_FILE = Path(__file__).resolve().with_name("humanize_gate.py")
HUMANIZE_EXIT = 3
SEND_PATH = re.compile(r"/(?:messages|drafts)(?:/[^/]+)?/send$")   # the Gmail endpoints that send mail
_ARMED = set()                                  # sha256 of the payloads send() built after the gate passed (one use each)
_CTRL = re.compile(r"[\x00-\x1f\x7f\x85  ]")


ENV_FILE = Path.home() / ".brownbison" / "env"
REDIRECT = "http://localhost:8765/"


def _env_file():
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            k, _, v = line.partition("=")
            if k.strip() and v and k.strip() not in os.environ:
                os.environ[k.strip()] = v.strip()


def _env(name):
    _env_file()
    v = os.environ.get(name)
    if not v:
        sys.exit(f"{name} is not set. Add it in the cloud environment settings (never in chat or the repo).")
    return v


def access_token():
    data = urllib.parse.urlencode({
        "client_id": _env("GMAIL_CLIENT_ID"),
        "client_secret": _env("GMAIL_CLIENT_SECRET"),
        "refresh_token": _env("GMAIL_REFRESH_TOKEN"),
        "grant_type": "refresh_token",
    }).encode()
    with urllib.request.urlopen("https://oauth2.googleapis.com/token", data, timeout=30) as r:
        return json.load(r)["access_token"]


def call(method, path, token, body=None, ctype="application/json"):
    if str(method).upper() == "POST" and SEND_PATH.search(str(path).split("?")[0]):
        digest = hashlib.sha256(body or b"").hexdigest()
        if digest not in _ARMED:
            sys.exit(f"HUMANIZE: refused POST {path.split('?')[0]}: only send() calls the Gmail send endpoints, after the humanize "
                     "gate passes. Use: python3 scripts/gmail_api.py send ...")
        _ARMED.discard(digest)
    req = urllib.request.Request(API + path, data=body, method=method,
                                 headers={"Authorization": f"Bearer {token}", "Content-Type": ctype})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Gmail API {e.code} on {method} {path.split('?')[0]}: {e.read().decode(errors='replace')[:500]}")


def _gate():
    """scripts/humanize_gate.py, loaded by path from this folder (never some other module named humanize_gate)."""
    spec = importlib.util.spec_from_file_location("pioneerleads_humanize_gate", GATE_FILE)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {GATE_FILE}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def humanize_refusal(text, recipients, asks=None, inbound=None, subject=None, files=(), no_signature=False, threaded=False):
    """-> (refusal, asks used). refusal is '' when this mail may go to these recipients, else the problems. Owner-only mail is
    exempt; everything else needs the signature, text-free attachments, a clean subject and a body that passes
    humanize_gate.lint() (asks above 1 only with the inbound email). threaded (--thread): a "Re:" subject is the thread's own and
    skips the call-invite phrase check (Luke's cell is still refused); on a new message "Re:" skips nothing.
    Fails closed: a gate that cannot load or run refuses."""
    try:
        gate = _gate()
        if gate.owner_only(recipients):
            return "", None
        probs = []
        if no_signature:
            probs.append("--no-signature is only for mail to Luke's own addresses; outside mail carries the Operations Manager "
                         "signature")
        probs += gate.attachment_problems(list(files or []))
        if not no_signature:                     # what send() appends is checked too: a phone line put back here is refused
            probs += gate.phone_problems(SIGNATURE, "signature")
        ok, problems, _warns, n = gate.lint(text, asks=asks, inbound=inbound)
        probs += gate.subject_problems(subject, run_hz=not gate.hz_failed(problems), threaded=threaded) + problems
    except Exception as e:                       # noqa: BLE001  fail closed
        return f"the humanize gate could not run ({type(e).__name__}: {e}); nothing was sent", None
    if probs or not ok:
        return ("; ".join(probs) or "hz.py lint did not PASS"), n
    return "", n


def _asks_arg(v):
    if not re.fullmatch(r"[0-9]{1,3}", str(v)):
        raise argparse.ArgumentTypeError(f"--asks {v!r} is not a whole number")
    n = int(v)
    if not 0 <= n <= MAX_ASKS:
        raise argparse.ArgumentTypeError(f"--asks {n} is outside 0..{MAX_ASKS} (questions in the email being answered)")
    return n


def _recipients(values):
    """Each recipient stripped once; the gate and the headers see the same strings. Control characters are refused."""
    out = []
    for r in values or []:
        s = str(r).strip()
        if _CTRL.search(s):
            raise ValueError(f"recipient {s[:60]!r} contains a line break or control character")
        if s:
            out.append(s)
    return out


def _refuse(why):
    print(f"HUMANIZE: {why}. Write it with /humanize (hz.py lint to PASS) and resend.", file=sys.stderr)
    sys.exit(HUMANIZE_EXIT)


def send(a):
    # the humanize gate runs first: before attachments are read, before any token or network call
    try:
        to, cc, bcc = _recipients(a.to), _recipients(a.cc), _recipients(a.bcc)
    except ValueError as e:
        _refuse(str(e))
    if not (to or bcc):
        sys.exit("Need --to or --bcc")
    text = Path(a.body_file).read_text(encoding="utf-8")
    inbound = None
    if getattr(a, "asks_from", None):
        try:
            inbound = Path(a.asks_from).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            _refuse(f"cannot read --asks-from {a.asks_from}: {e}")
    refusal, asks_used = humanize_refusal(text, [*to, *cc, *bcc], getattr(a, "asks", None), inbound, a.subject, a.files,
                                          a.no_signature, threaded=bool(str(getattr(a, "thread", None) or "").strip()))
    if refusal:
        _refuse(refusal)
    msg = EmailMessage()
    msg["From"] = f"Luke Adams <{SENDER}>"
    if to:
        msg["To"] = ", ".join(to)
    if cc:
        msg["Cc"] = ", ".join(cc)
    if bcc:
        msg["Bcc"] = ", ".join(bcc)
    msg["Subject"] = a.subject
    body = text.rstrip() + ("" if a.no_signature else SIGNATURE)   # the exact text the gate linted, read once
    msg.set_content(body)
    total = 0
    for f in a.files:
        p = Path(f)
        total += p.stat().st_size
        ctype = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
        main, sub = ctype.split("/", 1)
        msg.add_attachment(p.read_bytes(), maintype=main, subtype=sub, filename=p.name)
    if total > 24 * 1024 * 1024:
        sys.exit(f"Attachments total {total / 1e6:.1f} MB; Gmail caps a message at 25 MB. Split the send.")
    token = access_token()
    if a.thread:
        # reply headers from the thread's last message, so Outlook/Apple Mail thread it too (threadId alone is Gmail-only)
        t = call("GET", f"/gmail/v1/users/me/threads/{a.thread}?format=metadata"
                        "&metadataHeaders=Message-ID&metadataHeaders=References", token)
        hdrs = {h["name"].lower(): h["value"] for h in t["messages"][-1]["payload"].get("headers", [])}
        if hdrs.get("message-id"):
            msg["In-Reply-To"] = hdrs["message-id"]
            msg["References"] = (hdrs.get("references", "") + " " + hdrs["message-id"]).strip()
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    payload = {"raw": raw}
    if a.thread:
        payload["threadId"] = a.thread
    data = json.dumps(payload).encode()
    _ARMED.add(hashlib.sha256(data).hexdigest())          # the one payload call() may POST to messages/send
    out = call("POST", "/gmail/v1/users/me/messages/send", token, data)
    rec = {"id": out.get("id"), "threadId": out.get("threadId"), "to": to, "bcc_count": len(bcc),
           "attachments": [Path(f).name for f in a.files]}
    if asks_used is not None:
        rec["asks"] = asks_used
    if getattr(a, "asks_from", None):
        rec["asks_from"] = a.asks_from
    print(json.dumps(rec))


def save(a):
    token = access_token()
    m = call("GET", f"/gmail/v1/users/me/messages/{a.message_id}", token)
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    def walk(part):
        yield part
        for p in part.get("parts", []) or []:
            yield from walk(p)

    for part in walk(m["payload"]):
        name, att = part.get("filename"), part.get("body", {}).get("attachmentId")
        if not name or not att:
            continue
        data = call("GET", f"/gmail/v1/users/me/messages/{a.message_id}/attachments/{att}", token)["data"]
        dest = out / Path(name).name
        dest.write_bytes(base64.urlsafe_b64decode(data))
        print(dest)


def check(_a):
    print(call("GET", "/gmail/v1/users/me/profile", access_token())["emailAddress"])


def token_flow(a):
    """One-time, on Luke's own computer: prints the refresh token to paste into the environment settings."""
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        sys.exit("Run: python3 -m pip install google-auth-oauthlib")
    creds = InstalledAppFlow.from_client_secrets_file(a.client_json, [SCOPES]).run_local_server(port=0)
    print("\nAdd these three in the cloud environment settings (not in chat):")
    print("GMAIL_CLIENT_ID =", creds.client_id)
    print("GMAIL_CLIENT_SECRET = (the client_secret in your downloaded JSON)")
    print("GMAIL_REFRESH_TOKEN =", creds.refresh_token)


def auth_url(_a):
    """Cloud-side alternative to `token`: print the consent URL. Luke approves; the browser then shows a failed
    localhost page whose address holds a one-time code, which `exchange` turns into the refresh token."""
    q = urllib.parse.urlencode({"client_id": _env("GMAIL_CLIENT_ID"), "redirect_uri": REDIRECT, "response_type": "code",
                                "scope": SCOPES, "access_type": "offline", "prompt": "consent",
                                "login_hint": SENDER})
    print("https://accounts.google.com/o/oauth2/v2/auth?" + q)


def exchange(a):
    """Swap the one-time code (or the whole redirected localhost URL) for a refresh token; store it in ~/.brownbison/env."""
    code = a.code
    if code.startswith("http"):
        code = urllib.parse.parse_qs(urllib.parse.urlparse(code).query)["code"][0]
    data = urllib.parse.urlencode({"code": code, "client_id": _env("GMAIL_CLIENT_ID"),
                                   "client_secret": _env("GMAIL_CLIENT_SECRET"), "redirect_uri": REDIRECT,
                                   "grant_type": "authorization_code"}).encode()
    with urllib.request.urlopen("https://oauth2.googleapis.com/token", data, timeout=30) as r:
        tok = json.load(r)
    if "refresh_token" not in tok:
        sys.exit("No refresh token returned; run auth-url again (it forces the consent screen).")
    lines = [l for l in ENV_FILE.read_text().splitlines() if not l.startswith("GMAIL_REFRESH_TOKEN=")]
    lines.append("GMAIL_REFRESH_TOKEN=" + tok["refresh_token"])
    ENV_FILE.write_text("\n".join(lines) + "\n")
    ENV_FILE.chmod(0o600)
    os.environ["GMAIL_REFRESH_TOKEN"] = tok["refresh_token"]
    print("refresh token stored in ~/.brownbison/env")
    check(a)


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("auth-url").set_defaults(fn=auth_url)
    x = sp.add_parser("exchange")
    x.add_argument("code")
    x.set_defaults(fn=exchange)
    s = sp.add_parser("send")
    s.add_argument("--to", nargs="*", default=[])
    s.add_argument("--cc", nargs="*", default=[])
    s.add_argument("--bcc", nargs="*", default=[])
    s.add_argument("--subject", required=True)
    s.add_argument("--body-file", required=True)
    s.add_argument("--thread")
    s.add_argument("--no-signature", action="store_true", help="do not append SIGNATURE (only for mail to Luke's own addresses)")
    s.add_argument("--asks", type=_asks_arg, default=None,
                   help=f"questions in the email being answered, 0..{MAX_ASKS}; above 1 only with --asks-from")
    s.add_argument("--asks-from", help="the email being answered, saved as text: asks = min(--asks, its '?' count)")
    s.add_argument("files", nargs="*", help="attachments (put them after a literal --)")
    s.set_defaults(fn=send)
    v = sp.add_parser("save")
    v.add_argument("message_id")
    v.add_argument("out_dir")
    v.set_defaults(fn=save)
    sp.add_parser("check").set_defaults(fn=check)
    t = sp.add_parser("token")
    t.add_argument("client_json")
    t.set_defaults(fn=token_flow)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
