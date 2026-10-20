#!/usr/bin/env python3
"""Store a portal's one-time confirmation code for the next login attempt.

    python3 scripts/bidwatch/set_code.py 123456
    python3 scripts/bidwatch/set_code.py "Your confirmation code for BidNet Direct is: 123456"   # pasted email text

BidNet emails "Your BidNet Direct confirmation code" (from noreply@bidnet.com, 6 digits) after a password
login from a device it has not seen. The scanner stops at that prompt and reports it; whoever can read the
inbox (Luke, or the MAIN session with read-only Gmail) runs this, then re-runs the scan. The file is used
once and deleted; the confirmed-device cookie is kept with the saved session afterwards.
Written outside the repo (~/.brownbison/bidnet_code, mode 600). Never commit a code.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.bidwatch.common import CODE_FILE  # noqa: E402


def main(argv: list[str]) -> int:
    text = " ".join(argv).strip()
    m = re.search(r"\b(\d{6})\b", text)
    if not m:
        print("usage: set_code.py <6-digit code or the email text containing it>", file=sys.stderr)
        return 2
    CODE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CODE_FILE.write_text(m.group(1) + "\n")
    os.chmod(CODE_FILE, 0o600)
    print(f"code stored in {CODE_FILE} (single use); now re-run: python3 scripts/bidwatch/run.py")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
