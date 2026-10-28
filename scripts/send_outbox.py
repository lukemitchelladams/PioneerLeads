#!/usr/bin/env python3
"""Send every entry in an outbox manifest through scripts/gmail_api.py, once.

    python3 scripts/send_outbox.py ops/outbox/2026-10-28/outbox.json

Each entry: key, subject, to/cc/bcc, body_file, files. Results go to sent.json next to the manifest; entries already
in sent.json are skipped, so a rerun never double-sends.
"""
import json
import subprocess
import sys
from pathlib import Path

manifest = Path(sys.argv[1])
sent_path = manifest.with_name("sent.json")
sent = json.loads(sent_path.read_text()) if sent_path.exists() else {}
for e in json.loads(manifest.read_text()):
    if e["key"] in sent:
        print(f"skip {e['key']} (already sent {sent[e['key']]['id']})")
        continue
    cmd = [sys.executable, "scripts/gmail_api.py", "send", "--subject", e["subject"], "--body-file", e["body_file"]]
    for flag in ("to", "cc", "bcc"):
        if e.get(flag):
            cmd += [f"--{flag}", *e[flag]]
    cmd += e["files"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"FAILED {e['key']}: {r.stderr.strip() or r.stdout.strip()}")
        continue
    sent[e["key"]] = json.loads(r.stdout.strip().splitlines()[-1])
    sent_path.write_text(json.dumps(sent, indent=2))
    print(f"sent {e['key']}: {sent[e['key']]['id']}")
