#!/usr/bin/env python3
"""The humanize gate for the cloud sender (Luke's hard rule, 2026-11-05): every email to anyone other than Luke himself is written
with his /humanize skill and passes `hz.py lint` before it leaves. Stdlib only, Python 3.9+, self-contained: cloud containers do
not have the brown-bison-gov repo. It is a STRICTER PORT of the Mac's brown-bison-gov/data/humanize_gate.py, not a copy (the
differences are listed at the end of this docstring). hz.py runs as a subprocess and its rules are never copied here.

Two send paths, one gate:
  scripts/gmail_api.py send   runs humanize_refusal() -> lint() on the body file before attachments are read and before any token
                              or network call; refuses with exit 3 ("HUMANIZE: ..."). The body file ENDS at "Thanks <Name>,"
                              (gmail_api.py appends the Operations Manager signature itself).
  Gmail connector (MCP)       .claude/settings.json runs `humanize_gate.py hook` as a PreToolUse hook on send_message / reply /
                              forward (any mail server). The body must end with "Thanks <Name>," and then the five signature lines
                              (SIGNATURE_LINES), because the connector appends nothing. asks is always 0 here.

    ok, problems = check(body, asks=None, inbound=None)            what both paths call (lint() without the warnings)
    ok, problems, warnings, asks_used = lint(body, asks=None, inbound=None, tail="none"|"signature")
        Refuses on: hz.py ERROR lines (and any odd hz.py result: missing, crash, odd exit, timeout 20 s: fail closed);
        - no "Hi <Name>," greeting first, no message line, a closer that is not "Thanks <Name>," (capitalised, at most 3 names,
          every name in the greeting or "Team"), any text after the closer (tail "none") or anything but the signature (tail
          "signature");
        - the gate's OWN word count over the cap: every line between the greeting and the closer counts except short "Label:
          value" lines (18 words or fewer), so lines hz.py skips ("Hey ..." lines, extra greetings) still count; more than 12
          "Label: value" lines (SKILL.md: "stay at 12 or fewer");
        - invisible or look-alike characters (format characters such as soft hyphen / ZWSP / BOM, non-Latin letters, non-ASCII
          digits, dashes other than '-', typographic quotes, emoji and pictographs, bullets and arrows, odd spaces and controls);
        - links: http(s)://, www. or a domain with a path (Luke 2026-10-26: no links in outside mail; a bare name like SAM.gov is
          fine).
        hz.py's own warnings (adverbs, the 90-word target, long sentences, 3+ sentence paragraphs) are returned, printed by the
        CLI, and do not refuse: SKILL.md calls 150 the hard cap and 90 the target, and the adverb warns are discretionary.
    effective_asks(declared, inbound)   asks raise the word budget (cap max(150, 45 x asks)). Without the email being answered
                         (inbound text) asks is capped at 1; with it, asks = min(declared, '?' count in its unquoted lines), at
                         most MAX_ASKS. So an agent cannot lift the cap by typing a bigger number.
    subject_problems(subject)           invisible characters always; "Re:"/"Fwd:" subjects are the thread's own and stop there;
                         any other subject also passes `hz.py lint --chat` and the link rule.
    attachment_problems(files)          plain-text, HTML, Markdown, RTF and .eml/.msg attachments are refused for outside mail (an
                         unlinted "cover letter"); PDFs, Office files, CSV and images are fine.
    owner_only(rcpts)    True only when every recipient is exactly a bare ASCII address of Luke's own (OWN); that mail is exempt
    find_hz()            the hz.py that runs: ONLY the repo copy (.claude/skills/humanize/scripts/hz.py, reviewed and versioned);
                         a hand-made ~/.claude copy can be stale or edited, so it is never used; missing -> every check fails
    hook_decision(raw)   the PreToolUse decision for a Gmail connector send (None = no decision, else a deny payload)

CLI:
    python3 scripts/humanize_gate.py check BODYFILE [--asks N --asks-from INBOUND.txt] [--subject S] [--signature]
        prints the problems, hz.py's warnings, then PASS / PASS with warnings / FAIL; exit 0 pass, 1 fail.
        --signature = the body carries the signature after the closer (a Gmail connector send).
    python3 scripts/humanize_gate.py hook < hook-input.json     (what .claude/settings.json runs)

Stricter than the Mac gate, on purpose: the greeting must be a "Hi <Name>," style line; the closer is case-sensitive and checked
against the greeting; nothing (no signature, no quoted thread) may follow the closer in a body file; asks needs the inbound email;
there is no --long, no approvals file and no `approve` command (both are agent-writable ways to lift the cap).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
try:                                                          # the account's home, not $HOME: an environment cannot move the linter
    import pwd
    _USER_HOME = Path(pwd.getpwuid(os.getuid()).pw_dir)
except (ImportError, KeyError):                               # Windows: no pwd module
    _USER_HOME = Path.home()
REPO_HZ = REPO / ".claude" / "skills" / "humanize" / "scripts" / "hz.py"
# Only the reviewed, versioned repo copy runs. An account-home copy (~/.claude/skills/humanize) is hand-made in cloud containers
# and can be stale or edited, so it is never a fallback. Luke's own banned.local.txt still applies: hz.py reads its data home.
HZ_CANDIDATES = (REPO_HZ,)
REINSTALL = "restore it from git: git checkout -- .claude/skills/humanize"
HZ_FAILED = ("hz.py (the /humanize linter) not found", "hz.py lint timed out", "hz.py lint could not run",
             "hz.py lint gave an unexpected result")
TIMEOUT = 20
MAX_ASKS = 20
UNPROVEN_ASKS = 1                                             # asks without the inbound email
MAX_LABEL_LINES = 12
OWN = frozenset({"lukemitchelladams@gmail.com", "luke@brownbisonco.com"})   # Luke's own: mail only to these is exempt
# Luke 2026-10-18: title Operations Manager on every email. Same five lines as brown-bison-gov/data/brand.py SIGNATURE.
SIGNATURE_LINES = ("Luke Adams", "Operations Manager", "Brown Bison Holdings LLC", "(720) 275-1554", "luke@brownbisonco.com")

# hz.py's closer (case-insensitive): finds the cut. CLOSER is the shape this gate accepts on that line.
HZ_CLOSER = re.compile(r"^Thanks\s+(?P<who>[A-Za-z][\w.'-]*(?:\s*(?:,|and|&)\s*[A-Za-z][\w.'-]*)*),$", re.I)
_NAME = r"[A-Z][A-Za-z'.-]{0,30}"
_SEP = r"\s*,\s*|\s+and\s+|\s*&\s*"
CLOSER = re.compile(rf"^Thanks (?P<who>{_NAME}(?:(?:{_SEP}){_NAME}){{0,2}}),$")
GREETING = re.compile(r"^(?P<sal>hi|hey|hello|good (?:morning|afternoon|evening)|morning|afternoon)\s+"
                      r"(?P<name>[^\s?!:;,][^?!:;]{0,77}?)\s*[,!:]$", re.I)
LABEL = re.compile(r"^[A-Z0-9(][^:\n]{0,45}:\s+\S")         # hz.py's
WORD = re.compile(r"[A-Za-z][A-Za-z'’]*")                     # hz.py's
LINK = re.compile(r"(?i)(?:\b(?:https?|ftp)://|\bwww\.|(?<![@\w.-])[a-z0-9-]+(?:\.[a-z0-9-]+)*\.[a-z]{2,24}/)")
BARE_ADDRESS = re.compile(r"[a-z0-9._%+-]+@[a-z0-9-]+(?:\.[a-z0-9-]+)+")
REPLY_SUBJECT = re.compile(r"^\s*(?:re|fwd?|aw|sv)\s*:", re.I)
TEXT_ATTACH_EXT = frozenset({".txt", ".text", ".md", ".markdown", ".htm", ".html", ".xhtml", ".mht", ".mhtml", ".eml", ".msg",
                             ".rtf", ".log"})
TEXT_ATTACH_TYPES = ("text/plain", "text/html", "text/markdown", "text/x-markdown", "text/rtf", "application/rtf",
                     "application/xhtml+xml", "message/")

_DASHES = frozenset("֊־᐀᠆‐‑‒–—―⁃−⸗⸚⸺⸻⹀"
                    "〜〰゠︱︲﹘﹣－")
_QUOTES = frozenset("‘’‚‛“”„‟‹›«»「」『』＂＇")
_BULLETS = frozenset("•‣∙⁌⁍⁃")
_PICTO = ((0x1F000, 0x1FAFF), (0x2600, 0x27BF), (0x2B00, 0x2BFF), (0x2190, 0x21FF), (0x25A0, 0x25FF), (0x231A, 0x231B),
          (0x2328, 0x2328), (0x23CF, 0x23CF), (0x23E9, 0x23FA), (0x20E3, 0x20E3), (0x3297, 0x3297), (0x3299, 0x3299),
          (0x303D, 0x303D), (0xFE00, 0xFE0F))
_OK_SPACE = frozenset("  \t")
_OK_LETTER = frozenset("µ")                              # micro sign (uF capacitors)


# ---------------------------------------------------------------------------------------------------------------- text
def _lines(body):
    text = str(body or "").replace("\r\n", "\n").replace("\r", "\n")
    return (text[1:] if text.startswith("﻿") else text).split("\n")


def _closer_index(lines):
    return next((i for i, line in enumerate(lines) if HZ_CLOSER.match(line.strip())), None)


def prose(body):
    """Everything up to and including the first "Thanks <Name>," line; the whole body when there is none (which fails)."""
    lines = _lines(body)
    i = _closer_index(lines)
    return "\n".join(lines if i is None else lines[: i + 1])


def _picto(o):
    return any(a <= o <= b for a, b in _PICTO)


def char_problems(text, where="body"):
    """Characters that slip past hz.py's lexical checks or read as AI: one problem per kind, with the first example."""
    s = str(text or "")
    if s.startswith("﻿"):
        s = s[1:]
    found = {}

    def add(kind, ch):
        found.setdefault(kind, f"U+{ord(ch):04X} {unicodedata.name(ch, 'unnamed')}")
    if unicodedata.normalize("NFC", s) != s:
        found["decomposed"] = "a letter built from a base letter plus a combining mark"
    for i, ch in enumerate(s):
        o, cat = ord(ch), unicodedata.category(ch)
        if ch in "\n\r":
            continue
        if cat == "Cf":
            add("invisible format character", ch)
        elif cat in ("Cc", "Zl", "Zp") and ch != "\t":
            add("control or line-separator character", ch)
        elif cat == "Zs" and ch not in _OK_SPACE:
            add("odd space character", ch)
        elif cat in ("Co", "Cn", "Cs"):
            add("unassigned or private-use character", ch)
        elif cat == "Mn":
            add("combining mark", ch)
        elif cat.startswith("L") and ch not in _OK_LETTER and not unicodedata.name(ch, "").startswith("LATIN "):
            add("non-Latin or look-alike letter", ch)
        elif cat == "Nd" and not ("0" <= ch <= "9"):
            add("non-ASCII digit", ch)
        elif ch in _DASHES:
            add("dash other than '-'", ch)
        elif ch in _QUOTES:
            add("typographic quote", ch)
        elif ch in _BULLETS or (ch == "·" and (i == 0 or s[i - 1] == "\n")):
            add("bullet character", ch)
        elif _picto(o):
            add("emoji, pictograph, arrow or shape", ch)
    return [f"{where}: {kind} ({ex}); retype it in plain ASCII" for kind, ex in found.items()]


def link_problems(text, where="body"):
    s = str(text or "")
    m = LINK.search(s)
    if not m:
        return []
    token = re.match(r"\S*", s[m.start():]).group(0)[:80]
    return [f"{where}: link {token!r}: no links in mail to anyone outside (Luke 2026-10-26); attach the file, or send it to "
            "Luke to forward"]


def _greeting_names(line):
    m = GREETING.match(line)
    if not m:
        return None
    return {w.lower().rstrip(".") for w in re.findall(r"[A-Za-z][A-Za-z'.-]*", m.group("name"))}


def structure_problems(body, tail="none"):
    """The rules hz.py alone does not enforce: the greeting first, a message line, the closer's exact shape and names, and what may
    follow the closer (tail "none": nothing; tail "signature": exactly SIGNATURE_LINES)."""
    lines = _lines(body)
    i = _closer_index(lines)
    if i is None:
        return ["no 'Thanks <FirstName>,' closer line ('Thanks Team,' for group mail)"
                + ("; the body file must end with it" if tail == "none" else ", then the signature")]
    probs = []
    closer = lines[i].strip()
    above = [x.strip() for x in lines[:i] if x.strip()]
    greet = _greeting_names(above[0]) if above else None
    if greet is None:
        probs.append("no greeting line: the body must open with 'Hi <FirstName>,' ('Hi Team,' for group mail)")
    if len(above) < 2:
        probs.append("no message line between the greeting and 'Thanks <Name>,'")
    cm = CLOSER.match(closer)
    if not cm:
        probs.append(f"closer {closer[:70]!r} must read 'Thanks <FirstName>,': capital T, capitalised names, at most 3 names "
                     "('Thanks Team,' for group mail)")
    elif greet is not None:
        names = [n.strip() for n in re.split(_SEP, cm.group("who")) if n.strip()]
        off = [n for n in names if n.lower().rstrip(".") != "team" and n.lower().rstrip(".") not in greet]
        if off:
            probs.append(f"closer {closer!r} names {', '.join(off)}, not in the greeting {above[0]!r}; close with the greeting's "
                         "first name ('Thanks Team,' for group mail)")
    rest = [" ".join(x.split()) for x in lines[i + 1:] if x.strip()]
    if tail == "signature":
        if rest != list(SIGNATURE_LINES):
            probs.append("after 'Thanks <Name>,' the body must carry exactly the signature, nothing else: "
                         + " / ".join(SIGNATURE_LINES) + (f" (found {rest[0][:60]!r}...)" if rest else " (it is missing)"))
    elif rest:
        probs.append(f"text after the 'Thanks <Name>,' closer: {rest[0][:70]!r}; the body file must end at the closer "
                     "(gmail_api.py appends the signature itself; no signature, quote or P.S. in the file)")
    return probs


def counts(body):
    """-> (prose words, label lines) by the gate's own count: every non-blank line between the greeting (first line) and the closer
    counts, except short 'Label: value' lines (hz.py's rule: 18 words or fewer), which are counted as label lines."""
    lines = _lines(body)
    i = _closer_index(lines)
    above = [x.strip() for x in (lines if i is None else lines[:i]) if x.strip()]
    inner = above[1:] if above and _greeting_names(above[0]) is not None else above
    words = labels = 0
    for line in inner:
        n = len(WORD.findall(line))
        if LABEL.match(line) and n <= 18:
            labels += 1
        else:
            words += n
    return words, labels


def budget(asks):
    """hz.py's word budget: (target, cap)."""
    return max(90, 30 * asks), max(150, 45 * asks)


def budget_problems(body, asks, note=""):
    words, labels = counts(body)
    target, cap = budget(asks)
    probs = []
    if words > cap:
        probs.append(f"{words} words of prose (cap {cap}, target under {target}, for {asks} ask(s)); every line between the "
                     "greeting and the closer counts except short 'Label: value' lines. Cut it" + (f"; {note}" if note else ""))
    if labels > MAX_LABEL_LINES:
        probs.append(f"{labels} 'Label: value' lines (at most {MAX_LABEL_LINES}); group or trim them")
    return probs


# ---------------------------------------------------------------------------------------------------------------- asks
def _asks(v):
    """A declared asks value: None (not declared) or a whole number 0..MAX_ASKS. Anything else raises ValueError."""
    if v is None:
        return None
    if isinstance(v, bool) or not isinstance(v, int):
        raise ValueError(f"asks {v!r} is not a whole number 0..{MAX_ASKS}")
    if not 0 <= v <= MAX_ASKS:
        raise ValueError(f"asks {v} is outside 0..{MAX_ASKS} (the number of questions in the email being answered)")
    return v


def asks_in(inbound):
    """Question marks in the unquoted lines of the email being answered (URLs ignored), at most MAX_ASKS."""
    text = "\n".join(x for x in _lines(inbound) if not x.lstrip().startswith(">"))
    text = re.sub(r"\S+://\S+", " ", text)
    return min(text.count("?") + text.count("？"), MAX_ASKS)


def effective_asks(declared=None, inbound=None):
    """-> (asks used, note). No inbound email: at most UNPROVEN_ASKS. With it: min(declared, its question count), or the count when
    nothing was declared. Raises ValueError on a bad declared value."""
    d = _asks(declared)
    if inbound is None:
        n = min(d or 0, UNPROVEN_ASKS)
        note = (f"asks {d} was capped at {UNPROVEN_ASKS}: pass the email being answered (--asks-from FILE, manifest 'asks_from') "
                "to use its question count") if d is not None and d > UNPROVEN_ASKS else ""
        return n, note
    c = asks_in(inbound)
    n = c if d is None else min(d, c)
    return n, f"asks {n} from the email being answered ({c} question mark(s) in its unquoted lines)"


# ---------------------------------------------------------------------------------------------------------------- lint
def find_hz():
    """The repo's hz.py (reviewed, versioned), or None when it is missing (then every check fails closed)."""
    return next((p for p in HZ_CANDIDATES if Path(p).is_file()), None)


def hz_failed(problems):
    """True when hz.py itself could not give a verdict (missing, timed out, crashed): callers skip further hz.py runs."""
    return any(str(p).startswith(HZ_FAILED) for p in problems or [])


def _kill(p):
    try:
        if os.name == "posix":
            os.killpg(p.pid, signal.SIGKILL)                  # the whole session: a grandchild holding stdout dies too
        else:
            p.kill()
    except OSError:
        try:
            p.kill()
        except OSError:
            pass


def _run(cmd):
    """-> (exit code, stdout, stderr). Popen (not subprocess.run, which send-path tests replace): the linter is not a send. The
    child gets its own session/process group, so a timeout kills it and anything it started; then TimeoutExpired is raised."""
    kw = dict(stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8",
              errors="replace")
    if os.name == "posix":
        kw["start_new_session"] = True
    else:
        kw["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    p = subprocess.Popen(cmd, **kw)
    try:
        out, err = p.communicate(timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        _kill(p)
        try:
            p.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            for f in (p.stdout, p.stderr):
                try:
                    f.close()
                except OSError:
                    pass
        raise
    return p.returncode, out or "", err or ""


def _hz(text, asks=0, chat=False, hz_py=None):
    """hz.py lint on text. -> (ok, errors, warnings). Fails closed: any odd result is an error, never a pass."""
    hz = Path(hz_py) if hz_py else find_hz()
    if hz is None or not hz.is_file():
        where = hz if hz is not None else " or ".join(str(p) for p in HZ_CANDIDATES)
        return False, [f"hz.py (the /humanize linter) not found at {where}; nothing is sent until it is back. {REINSTALL}"], []
    with tempfile.TemporaryDirectory(prefix="bb-hz-") as d:
        f = Path(d) / "draft.txt"
        f.write_text(text, encoding="utf-8")
        cmd = [sys.executable or "python3", "-I", str(hz), "lint", str(f), "--asks", str(asks)] + (["--chat"] if chat else [])
        try:
            code, stdout, stderr = _run(cmd)
        except subprocess.TimeoutExpired:
            return False, [f"hz.py lint timed out after {TIMEOUT} s"], []
        except OSError as e:
            return False, [f"hz.py lint could not run: {e}"], []
    out = [x.rstrip() for x in stdout.splitlines() if x.strip()]
    last = out[-1].strip() if out else ""
    errs = [x.strip().replace(" Cut, or pass --long if the user asked for detail", " Cut it") for x in out if x.startswith("ERROR")]
    warns = [x.strip() for x in out if x.startswith("warn")]
    if code == 0 and last in ("PASS", "PASS with warnings") and not errs:
        return True, [], warns
    if code == 1 and last == "FAIL" and errs:
        return False, errs, warns
    err = " ".join(stderr.split())[-200:]
    return False, [f"hz.py lint gave an unexpected result (exit {code}, last line {last!r}){': ' + err if err else ''}"], warns


def lint(body, asks=None, inbound=None, hz_py=None, tail="none"):
    """-> (ok, problems, warnings, asks used). ok only when the gate's own rules and hz.py both pass."""
    try:
        n, note = effective_asks(asks, inbound)
    except ValueError as e:
        return False, [str(e)], [], 0
    if tail not in ("none", "signature"):
        return False, [f"unknown tail mode {tail!r}"], [], n
    probs = char_problems(body) + structure_problems(body, tail) + budget_problems(body, n, note) + link_problems(body)
    ok, errs, warns = _hz(prose(body), n, hz_py=hz_py)
    probs += errs
    return (ok and not probs), probs, warns, n


def check(body, asks=None, inbound=None, hz_py=None, tail="none"):
    """-> (ok, problems): lint() without the warnings."""
    ok, probs, _warns, _n = lint(body, asks=asks, inbound=inbound, hz_py=hz_py, tail=tail)
    return ok, probs


def subject_problems(subject, hz_py=None, run_hz=True):
    """The subject of outside mail: one line, no invisible characters; unless it is a thread's own "Re:"/"Fwd:" subject, also no
    look-alikes, emoji, links or hz.py --chat ERROR (dashes, curly quotes, banned phrases). run_hz=False (hz.py already failed
    closed on the body) skips the hz.py run so a hung linter costs one timeout, not two."""
    s = str(subject if subject is not None else "")
    if not s.strip():
        return ["subject: empty; outside mail needs a subject line"]
    if any(ch in s for ch in "\r\n\x85  "):
        return ["subject: a line break inside the subject"]
    if REPLY_SUBJECT.match(s):
        return [p for p in char_problems(s, "subject") if "invisible" in p or "control" in p]
    probs = char_problems(s, "subject") + link_problems(s, "subject")
    if not run_hz:
        return probs
    ok, errs, _warns = _hz(s.strip() + "\n", 0, chat=True, hz_py=hz_py)
    return probs + [("subject: " + e) for e in errs]


def attachment_problems(files):
    """files: paths/names, or (name, mime type) pairs. Text-like attachments carry unlinted prose, so outside mail cannot carry
    them."""
    import mimetypes
    bad = []
    for f in files or []:
        name, ctype = (f if isinstance(f, (tuple, list)) else (f, None))
        name = str(name or "")
        ctype = str(ctype or mimetypes.guess_type(name)[0] or "").lower()
        if Path(name).suffix.lower() in TEXT_ATTACH_EXT or ctype.startswith(TEXT_ATTACH_TYPES):
            bad.append(Path(name).name or ctype)
    if not bad:
        return []
    return [f"attachment {', '.join(bad)}: plain-text, HTML, Markdown, RTF or mail attachments carry unlinted text; put the words "
            "in the humanized body, or send a PDF/Office file"]


# ---------------------------------------------------------------------------------------------------------------- recipients
def owner_only(recipients):
    """True only when there is at least one recipient and EVERY one is exactly a bare ASCII address in OWN (case-insensitive,
    surrounding spaces ignored). 'Name <a@b>', 'a@b, c@d', 'a@b;c@d', newlines, non-ASCII look-alikes (the Kelvin sign) or anything
    else is not owner-only, so that mail is linted."""
    if isinstance(recipients, str):
        recipients = [recipients]
    addrs = []
    for r in recipients or []:
        if r is None:
            continue
        s = str(r)
        if not s.isascii():
            return False
        addrs.append(s.strip(" ").lower())
    return bool(addrs) and all(BARE_ADDRESS.fullmatch(a) is not None and a in OWN for a in addrs)


# ---------------------------------------------------------------------------------------------------------------- MCP hook
MAIL_TOOLS = frozenset({"send_message", "reply", "reply_all", "forward", "send_draft", "send_email"})
REPLY_TOOLS = frozenset({"reply", "reply_all"})
TEXT_KEYS = ("body", "forwardText", "forward_text", "text", "content", "message", "note", "comment")
HTML_KEYS = ("htmlBody", "html_body", "html")
SHAPE_KEYS = ("messageId", "draftId", "replyThreadId", "replyToMessageId", "forwardText", "htmlBody", "html_body", "subject")
HOOK_FIX = ("Write it with /humanize: 'Hi <FirstName>,', the message, 'Thanks <FirstName>,', then the five signature lines ("
            + " / ".join(SIGNATURE_LINES) + ") and nothing else. Pre-check: python3 scripts/humanize_gate.py check FILE --signature. "
            "A reply that answers several questions, or carries files, goes through scripts/gmail_api.py send --asks-from INBOUND.")


def _deny(reason):
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                   "permissionDecisionReason": "HUMANIZE GATE (pioneerleads): " + reason}}


def _split_tool(name):
    if not isinstance(name, str) or not name.startswith("mcp__") or "__" not in name[5:]:
        return None
    server, tool = name[5:].rsplit("__", 1)
    return server, tool


def _values(v):
    """A recipient field as a list of strings: a list, a JSON array in a string, or a comma/semicolon separated string."""
    if v is None:
        return []
    if isinstance(v, (list, tuple)):
        out = []
        for x in v:
            out += _values(x)
        return out
    if isinstance(v, dict):
        return [str(v.get("email") or v.get("address") or "")]
    s = str(v).strip()
    if s.startswith("["):
        try:
            return _values(json.loads(s))
        except ValueError:
            pass
    return [x for x in re.split(r"[,;]", s) if x.strip()]


def _recipients(ti):
    out = []
    for k in ("to", "cc", "bcc"):
        out += _values(ti.get(k))
    return out


def _is_mail(name, ti):
    parts = _split_tool(name)
    if not parts:
        return False
    server, tool = parts
    if tool not in MAIL_TOOLS or server.startswith("ccd_") or server.startswith("Read_and_Send_iMessages"):
        return False
    if "mail" in server.lower():
        return True
    return isinstance(ti, dict) and (any("@" in r for r in _recipients(ti)) or any(ti.get(k) for k in SHAPE_KEYS))


def _shown(problems):
    return "; ".join(problems[:6]) + (f"; ... {len(problems) - 6} more" if len(problems) > 6 else "")


def _decide_mail(tool, ti, hz_py=None):
    if str(ti.get("draftId") or "").strip() or tool == "send_draft":
        return _deny(f"{tool} with a draftId sends the stored draft as is, which this hook cannot read. Put the humanized text in "
                     "body instead.")
    html = [k for k in HTML_KEYS if isinstance(ti.get(k), str) and ti.get(k).strip()]
    if html:
        return _deny(f"{tool} carries {', '.join(html)}: most mail clients show the HTML part, and Brown Bison sends plain text. "
                     "Put the humanized text in " + ("forwardText" if tool == "forward" else "body") + " and drop the HTML field.")
    rcpts = _recipients(ti)
    if tool in REPLY_TOOLS:
        exempt = tool == "reply" and bool(_values(ti.get("to"))) and ti.get("replyAll") is not True and owner_only(rcpts)
    else:
        exempt = bool(rcpts) and owner_only(rcpts)
    if exempt:
        return None                                          # Luke's own addresses: board updates and alerts
    if ti.get("includeSignature") is True:
        return _deny("includeSignature appends a Gmail web signature this hook cannot read (and may not say Operations Manager); "
                     "set it false and put the signature lines in the body. " + HOOK_FIX)
    texts = [(k, ti[k]) for k in TEXT_KEYS if isinstance(ti.get(k), str) and ti[k].strip()]
    if not texts:
        if tool == "forward":
            return _deny(f"forward to {', '.join(rcpts) or 'the recipients'} has no note; put a short humanized note in forwardText. "
                         + HOOK_FIX)
        return _deny(f"{tool} has no plain-text body to check. " + HOOK_FIX)
    body_probs, broken = [], False
    for k, v in texts:
        ok, problems, _warns, _n = lint(v, asks=0, hz_py=hz_py, tail="signature")
        broken = broken or hz_failed(problems)
        if not ok:
            body_probs += [f"{k}: {p}" for p in problems] or [f"{k}: hz.py lint did not PASS"]
    atts = [(a.get("filename"), a.get("mimeType")) for a in (ti.get("attachments") or []) if isinstance(a, dict)]
    probs = attachment_problems(atts)
    threaded = bool(str(ti.get("replyThreadId") or ti.get("replyToMessageId") or "").strip())
    if ti.get("subject") is not None or (tool in ("send_message", "send_email") and not threaded):
        probs += subject_problems(ti.get("subject"), hz_py=hz_py, run_hz=not broken)   # a new message needs a clean subject
    if body_probs:
        return _deny(f"this {tool} is not humanized: {_shown(body_probs + probs)}. " + HOOK_FIX)
    if probs:
        return _deny(f"this {tool} is refused: {_shown(probs)}. " + HOOK_FIX)
    return None


def _name_from_raw(raw):
    m = re.search(r'"tool_name"\s*:\s*"([^"]+)"', raw or "")
    return m.group(1) if m else None


def _maybe_mail(name):
    parts = _split_tool(name)
    return parts is None or (parts[1] in MAIL_TOOLS and not parts[0].startswith(("ccd_", "Read_and_Send_iMessages")))


def hook_decision(raw, hz_py=None):
    """-> None (no decision: the normal permission flow) or a deny payload. Fails closed for anything that may be a mail send."""
    try:
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("not an object")
    except ValueError:
        return _deny("the hook input could not be read, so this send cannot be checked; nothing goes out unchecked.") \
            if _maybe_mail(_name_from_raw(raw)) else None
    name = data.get("tool_name") or ""
    ti = data.get("tool_input")
    parts = _split_tool(name)
    if parts is None or not _maybe_mail(name):
        return None                                          # not an MCP mail tool: not ours
    if not isinstance(ti, dict):
        return _deny(f"{name}: tool_input is missing or not an object; nothing goes out unchecked.")
    if not _is_mail(name, ti):
        return None                                          # e.g. a chat server's send_message: no address, no mail shape
    return _decide_mail(parts[1], ti, hz_py=hz_py)


def hook_main(stdin=None, stdout=None):
    stdin, stdout = stdin or sys.stdin, stdout or sys.stdout
    raw = ""
    try:
        raw = stdin.read()
        out = hook_decision(raw)
    except BaseException as e:                               # noqa: BLE001  SystemExit / KeyboardInterrupt included: fail closed
        out = _deny(f"hook error {type(e).__name__}: {e}; nothing goes out unchecked.") if _maybe_mail(_name_from_raw(raw)) else None
    if out is not None:
        stdout.write(json.dumps(out))
        stdout.flush()
    return 0


# ---------------------------------------------------------------------------------------------------------------- CLI
def ascii_int(v):
    """argparse type: a plain ASCII whole number ('٨' or '+8' is not 8)."""
    if not re.fullmatch(r"[0-9]{1,3}", str(v)):
        raise argparse.ArgumentTypeError(f"{v!r} is not a whole number")
    return int(v)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("check", help="lint a body file the way the senders will")
    p.add_argument("file")
    p.add_argument("--asks", type=ascii_int, default=None, help=f"questions in the email being answered, 0..{MAX_ASKS}")
    p.add_argument("--asks-from", help="the email being answered (a text file); asks above 1 need it")
    p.add_argument("--subject", help="also check this subject line")
    p.add_argument("--signature", action="store_true", help="the body carries the signature after the closer (Gmail connector)")
    sub.add_parser("hook", help="PreToolUse hook for Gmail connector sends (reads the hook JSON on stdin)")
    a = ap.parse_args(argv)
    if a.cmd == "hook":
        return hook_main()
    try:
        body = Path(a.file).read_text(encoding="utf-8")
        inbound = Path(a.asks_from).read_text(encoding="utf-8") if a.asks_from else None
    except (OSError, UnicodeDecodeError) as e:
        print(f"cannot read {e.filename or a.file}: {e}")
        print("FAIL")
        return 1
    ok, probs, warns, n = lint(body, asks=a.asks, inbound=inbound, tail="signature" if a.signature else "none")
    if a.subject is not None:
        sp = subject_problems(a.subject)
        probs, ok = probs + sp, ok and not sp
    for x in probs:
        print(x)
    for x in warns:
        print(x)
    print(f"asks used: {n}")
    print("FAIL" if not ok else ("PASS with warnings" if warns else "PASS"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
