#!/usr/bin/env python3
"""Send mail with attachments, and save attachments, through the Gmail API (HTTPS), as luke@brownbisonco.com.

The Gmail connector cannot carry multi-MB attachments and SMTP is blocked in cloud sessions, so this talks to
gmail.googleapis.com directly. Credentials come from the environment only (set once in the cloud environment's
settings, never pasted in chat, never written to the repo):

    GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_REFRESH_TOKEN

Get the refresh token once on Luke's Mac with:  python3 scripts/gmail_api.py token <client_secret.json>

Usage:
    python3 scripts/gmail_api.py send --to a@x.com [--bcc b@y.com ...] --subject "..." --body-file body.txt FILE...
    python3 scripts/gmail_api.py send --thread <threadId> --to a@x.com --subject "Re: ..." --body-file b.txt FILE...
    python3 scripts/gmail_api.py save <messageId> <out_dir>      # download every attachment on a message
    python3 scripts/gmail_api.py check                           # verify the token works (prints the address only)
"""
import argparse
import base64
import json
import mimetypes
import os
import sys
import urllib.parse
import urllib.request
from email.message import EmailMessage
from pathlib import Path

API = "https://gmail.googleapis.com"
SENDER = "luke@brownbisonco.com"
SCOPES = "https://www.googleapis.com/auth/gmail.modify"
SIGNATURE = "\n\nLuke Adams\nOwner, Brown Bison Holdings LLC\n(720) 275-1554 | luke@brownbisonco.com\n"


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
    req = urllib.request.Request(API + path, data=body, method=method,
                                 headers={"Authorization": f"Bearer {token}", "Content-Type": ctype})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)


def send(a):
    msg = EmailMessage()
    msg["From"] = f"Luke Adams <{SENDER}>"
    if a.to:
        msg["To"] = ", ".join(a.to)
    if a.cc:
        msg["Cc"] = ", ".join(a.cc)
    if a.bcc:
        msg["Bcc"] = ", ".join(a.bcc)
    msg["Subject"] = a.subject
    body = Path(a.body_file).read_text().rstrip() + ("" if a.no_signature else SIGNATURE)
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
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    payload = {"raw": raw}
    if a.thread:
        payload["threadId"] = a.thread
    out = call("POST", "/gmail/v1/users/me/messages/send", token, json.dumps(payload).encode())
    print(json.dumps({"id": out.get("id"), "threadId": out.get("threadId"),
                      "to": a.to, "bcc_count": len(a.bcc or []), "attachments": [Path(f).name for f in a.files]}))


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
    s.add_argument("--no-signature", action="store_true")
    s.add_argument("files", nargs="*")
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
    if a.cmd == "send" and not (a.to or a.bcc):
        sys.exit("Need --to or --bcc")
    a.fn(a)


if __name__ == "__main__":
    main()
