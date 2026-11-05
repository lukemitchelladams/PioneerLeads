#!/usr/bin/env python3
"""Send every entry in an outbox manifest through scripts/gmail_api.py (the copy beside this file), once.

    python3 scripts/send_outbox.py ops/outbox/2026-10-28/outbox.json

Each entry: key, subject, to/cc/bcc (lists of addresses), body_file, files (list), optional thread (reply in that Gmail thread),
optional asks (whole number: questions in the email being answered) and asks_from (that email saved as a text file; asks above 1
count only with it). Relative paths resolve against the directory you run this from. Results go to sent.json next to the
manifest; entries already in sent.json are skipped, so a rerun never double-sends.

gmail_api.py refuses (exit 3, "HUMANIZE: ...") anything that does not pass the humanize gate (Luke's hard rule, 2026-11-05):
that entry prints "REFUSED <key>: ..." and is NOT written to sent.json. A malformed entry (a list that is not a list, a value
that starts with '-', an attachment that is not a file) prints "FAILED <key>: ..." and is not sent. The run ends with a summary
line and exits 3 when any entry was REFUSED, 1 when any FAILED, else 0, so a loop that checks the exit code sees it.
Importing this module sends nothing; only running it as a script does.
"""
import json
import subprocess
import sys
from pathlib import Path

HUMANIZE_EXIT = 3                                 # gmail_api.HUMANIZE_EXIT
SENDER = Path(__file__).resolve().with_name("gmail_api.py")
REPO = SENDER.parent.parent


def _abs(p):
    return str(Path(p).expanduser().resolve())


def entry_problem(e):
    """'' when the manifest entry is well formed, else what is wrong with it."""
    if not isinstance(e, dict):
        return "entry is not an object"
    for k in ("key", "subject", "body_file"):
        if not isinstance(e.get(k), str) or not e[k].strip():
            return f"'{k}' must be a non-empty string"
    for k in ("to", "cc", "bcc", "files"):
        v = e.get(k, [])
        if v is None:
            continue
        if not isinstance(v, list) or not all(isinstance(x, str) and x.strip() for x in v):
            return f"'{k}' must be a list of non-empty strings"
        if any(x.lstrip().startswith("-") for x in v):
            return f"'{k}' has a value starting with '-' (looks like a flag)"
    if not (e.get("to") or e.get("bcc")):
        return "needs 'to' or 'bcc'"
    for k in ("subject", "body_file", "thread", "asks_from"):
        if isinstance(e.get(k), str) and e[k].lstrip().startswith("-"):
            return f"'{k}' starts with '-' (looks like a flag)"
    if e.get("thread") is not None and not isinstance(e["thread"], str):
        return "'thread' must be a string"
    if e.get("asks") is not None and (isinstance(e["asks"], bool) or not isinstance(e["asks"], int)):
        return "'asks' must be a whole number"
    if e.get("asks_from") is not None and not isinstance(e["asks_from"], str):
        return "'asks_from' must be a path string"
    for f in e.get("files") or []:
        if not Path(f).is_file():
            return f"attachment {f!r} is not a file"
    return ""


def build_cmd(e):
    cmd = [sys.executable, str(SENDER), "send", "--subject", e["subject"], "--body-file", _abs(e["body_file"])]
    if e.get("asks") is not None:  # questions in the email being answered (humanize gate word budget)
        cmd += ["--asks", str(e["asks"])]
    if e.get("asks_from"):         # the email being answered: asks above 1 count only with it
        cmd += ["--asks-from", _abs(e["asks_from"])]
    if e.get("thread"):            # reply in an existing thread (gmail_api adds In-Reply-To/References)
        cmd += ["--thread", e["thread"]]
    for flag in ("to", "cc", "bcc"):
        if e.get(flag):
            cmd += [f"--{flag}", *e[flag]]
    return cmd + ["--", *[_abs(f) for f in e.get("files") or []]]   # after '--' every token is an attachment, never a flag


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        sys.exit("usage: python3 scripts/send_outbox.py <outbox manifest .json>")
    manifest = Path(argv[0])
    sent_path = manifest.with_name("sent.json")
    sent = json.loads(sent_path.read_text()) if sent_path.exists() else {}
    tally = {"sent": 0, "skipped": 0, "refused": 0, "failed": 0}
    for e in json.loads(manifest.read_text()):
        key = e.get("key") if isinstance(e, dict) else None
        if isinstance(key, str) and key in sent:
            print(f"skip {key} (already sent {sent[key]['id']})")
            tally["skipped"] += 1
            continue
        why = entry_problem(e)
        if why:
            print(f"FAILED {key}: bad manifest entry: {why}")
            tally["failed"] += 1
            continue
        r = subprocess.run(build_cmd(e), capture_output=True, text=True, cwd=str(REPO))
        if r.returncode != 0:
            err = r.stderr.strip() or r.stdout.strip()
            if r.returncode == HUMANIZE_EXIT or "HUMANIZE:" in err:
                print(f"REFUSED {key}: {err}")
                tally["refused"] += 1
            else:
                print(f"FAILED {key}: {err}")
                tally["failed"] += 1
            continue
        sent[key] = json.loads(r.stdout.strip().splitlines()[-1])
        sent_path.write_text(json.dumps(sent, indent=2))
        print(f"sent {key}: {sent[key]['id']}")
        tally["sent"] += 1
    print("outbox: " + ", ".join(f"{v} {k}" for k, v in tally.items()))
    return HUMANIZE_EXIT if tally["refused"] else (1 if tally["failed"] else 0)


if __name__ == "__main__":
    sys.exit(main())
