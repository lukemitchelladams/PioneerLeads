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
                              forward (any mail server). The body must end with "Thanks <Name>," and then the four signature lines
                              (SIGNATURE_LINES, no phone line), because the connector appends nothing. asks is always 0 here.
                              forward to anyone but Luke is refused (2026-11-06): it carries the original message and its quoted
                              thread, which the hook cannot read; write a new message instead.

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
          fine);
        - PHONE (Luke 2026-11-06, phone_problems): Luke's cell in any format (body, signature, subject, attachment names: any
          digits run that holds 7202751554 with separators of up to 8 characters, look-alike letters such as 'l554', the bare
          275-1554, HTML character references, spelled-out digits, or the number split by filler words: '720 dot 275 dot 1554',
          'area code 720; the rest is 2751554') and any invitation to phone him, callback promises included ("I'll return your
          call", "Luke will give you a ring"). Call invites are refused BY DEFAULT: every "call" and every "phone" in our
          own text is refused unless it is a trade term (on-call, service / emergency / pre-bid call, call-out, call log / rate /
          response, a call-back within 2 hours, "call for bids"), someone else's call or line ("the City will call us", "call
          the Town procurement office", "your techs carry a cell phone", "photos from my phone"), RFP wording in the plural
          ("phone calls must be returned within 4 hours"), "the call" as an event ("within 2 hours of the call", "bill the call",
          "who takes the call") or negated ("don't call", "email, not phone"); text / ring / buzz / cell / number / talk / live /
          voicemail / Zoom / WhatsApp / FaceTime are refused in invite shapes ("text me", "my cell", "a good number to reach you",
          "can we talk Monday", "talk soon", "go over it live", "ring you back"). A promise that Luke phones ANYONE is refused
          too, the reader's side ("I'll give your office a call", "Luke will call Jake", "I'll ring around 4", "Luke takes calls
          after 5", review #4) and third parties alike ("I'll give the inspector a call", "We'll call the Town for the gate code",
          "Let me give the inspector a call", "I'll phone the County tomorrow", review #5: no operator promises that Luke will
          phone anyone); field procedure ("We'll call 811", "We'll call for the final inspection", "We'll call in the inspection"),
          the reader told to call someone ("Give the inspector a call before you pour", "call in the locate ticket"), third
          parties calling each other, naming ("I'd call that a fair price") and phone equipment ("the phone jack", "phone and data
          cable", "the phone company") pass. Forms and proposals (not mail) may still print the number.
        hz.py's own warnings (adverbs, the 90-word target, long sentences, 3+ sentence paragraphs) are returned, printed by the
        CLI, and do not refuse: SKILL.md calls 150 the hard cap and 90 the target, and the adverb warns are discretionary.
    effective_asks(declared, inbound)   asks raise the word budget (cap max(150, 45 x asks)). Without the email being answered
                         (inbound text) asks is capped at 1; with it, asks = min(declared, '?' count in its unquoted lines), at
                         most MAX_ASKS. So an agent cannot lift the cap by typing a bigger number.
    subject_problems(subject, threaded=False)   invisible characters and Luke's cell always; a "Re:"/"Fwd:" subject on a really
                         threaded message is the thread's own and stops there (without threaded=True it is also checked for call
                         invites); any other subject also passes `hz.py lint --chat` and the link rule.
    attachment_problems(files)          plain-text, HTML, Markdown, RTF and .eml/.msg attachments are refused for outside mail (an
                         unlinted "cover letter"); PDFs, Office files, CSV and images are fine. A file NAME holding Luke's cell
                         is refused.
    owner_only(rcpts)    True only when every recipient is an ASCII address of Luke's own (OWN), bare or in the plain display-name
                         form 'Luke Adams <addr>' / '<addr>'; that mail is exempt
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
import html
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
# Luke 2026-10-18: title Operations Manager on every email. Luke 2026-11-06: no phone line (people were calling him all day);
# brand.py's NAME, TITLE, COMPANY and EMAIL, in that order, without its PHONE.
SIGNATURE_LINES = ("Luke Adams", "Operations Manager", "Brown Bison Holdings LLC", "luke@brownbisonco.com")

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
# 'Luke Adams <addr>', '"Luke Adams" <addr>', '<addr>': a plain display name (letters, spaces, . ' -) and ONE bracketed address
_DISPLAY_FORM = re.compile(r'(?:"(?P<qname>[A-Za-z][A-Za-z .\'-]{0,62})"|(?P<name>[A-Za-z][A-Za-z .\'-]{0,62}?))? ?<(?P<addr>[^<>\s"]+)>')
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


# ---------------------------------------------------------------------------------------------------------------- phone
# Luke 2026-11-06 ~10:50 MT, HARD RULE: people call him all day while he is at his day job, and he does not always have the latest
# information, so outside mail gets answers by email. It never carries his cell and never invites a call. Phone numbers on bid
# FORMS and PROPOSAL documents are not mail and are out of scope here.
#
# Call invites are refused BY DEFAULT (review 2026-11-06: a list of invite phrasings always misses one). Every "call" / "calling"
# and every "phone" / "telephone" in our own text is refused unless it is one of the allowed uses below; words too common to refuse
# outright (text, ring, cell, number, talk, chat, voicemail, Zoom) are refused in invite shapes (INVITES).
#   allowed: trade terms (on-call, service / emergency / after-hours / conference / pre-bid call, call-out, call list / log / rate /
#            response, a call-back within 2 hours, calls for service, "call for bids", "the right call", per call); field procedure
#            (calling 811, calling for / calling in an inspection or locate); a third party calling or being called, unless Luke's
#            side promises the call ("the City will call us", "call the Town procurement office", "give the inspector a call",
#            "a call with the County", "call Silas"; never "I'll call the Town", review #5); someone else's phone ("your techs
#            carry a cell phone", "his phone number is on the W-9", "the dispatcher answers the phone", "Phone: 719-694-0515");
#            photos ("photos from my phone"); a negation that governs the word ("don't call", "no phone call needed", "rather
#            than a phone call", "email, not phone"). Plural "calls" / "phone calls" (RFP wording: "phone calls must be returned
#            within 4 hours") pass unless they invite ("calls are fine", "I take calls after 5").
LUKE_CELL = "7202751554"                                     # (720) 275-1554, compared digits-only
_LOCAL = LUKE_CELL[3:]                                       # 2751554: the number without its area code
PHONE_FIX = ("No phone number or call invite in email (Luke 2026-11-06): answer by email; at most add 'Email is the best way to "
             "reach me during the day.'")
# digits joined by up to 8 characters that are neither digits nor ASCII letters: (720) 275-1554, 720 . . . 275 . . . 1554, 720-275-\n> 1554
_RUN = re.compile(r"[0-9](?:[^0-9A-Za-z]{0,8}[0-9])*")
_PHONE_WORD = re.compile(r"\b(?:cell|cellphone|mobile|mob|phone|ph|tel|telephone|call|text|txt|sms|reach|dial|direct)\W{0,4}$", re.I)
_LOOK = {"O": "0", "o": "0", "D": "0", "Q": "0", "I": "1", "l": "1", "i": "1", "S": "5", "s": "5", "Z": "2", "z": "2", "B": "8"}
_DASH_MAP = str.maketrans({c: "-" for c in "‐‑‒–—―−⁃﹘﹣"})


def _norm(text):
    """HTML character references decoded ('720&#45;275'), NFKC (full-width, superscript and math digits -> ASCII, odd spaces ->
    space), format characters dropped (soft hyphen, zero-width space, BOM, bidi marks), every other Unicode decimal digit -> ASCII,
    curly apostrophes -> "'", dashes -> '-'."""
    s = unicodedata.normalize("NFKC", html.unescape(str(text or "")))
    s = "".join(c for c in s if unicodedata.category(c) != "Cf")
    s = "".join(str(unicodedata.decimal(c)) if (c.isdecimal() and not "0" <= c <= "9") else c for c in s)
    return s.replace("’", "'").replace("‘", "'").replace("ʼ", "'").translate(_DASH_MAP)


def _lookalikes(s, as_digit):
    """O/o/D/Q, I/l/i, S/s, Z/z and B standing next to a digit (and not inside a word) read as 0, 1, 5, 2, 8 (as_digit) or as a
    separator (not as_digit): '720-275-l554', '72O-275-1554', '720-275-1S54'. Same length as s."""
    out = list(s)
    for i, c in enumerate(s):
        if c in _LOOK:
            p, n = (s[i - 1] if i else " "), (s[i + 1] if i + 1 < len(s) else " ")
            if (p.isdigit() or n.isdigit()) and not p.isalpha() and not n.isalpha():
                out[i] = _LOOK[c] if as_digit else "-"
    return "".join(out)


_UNITS = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")
_TEENS = ("ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen")
_TENS = {"twenty": 2, "thirty": 3, "forty": 4, "fourty": 4, "fifty": 5, "sixty": 6, "seventy": 7, "eighty": 8, "ninety": 9}
_NUM_WORD = {join: re.compile(r"(?<![A-Za-z])(?:(?P<tens>" + "|".join(_TENS) + r")(?:" + join + r"(?P<unit>" + "|".join(_UNITS[1:])
                              + r"))?|(?P<teen>" + "|".join(_TEENS) + r")|(?P<one>" + "|".join(_UNITS) + r"))(?![A-Za-z])", re.I)
             for join in (r"[- ]?", r"-?")}                 # 'fifty four' = 54, or 50 4 ('seven twenty two seventy-five')
_OH = re.compile(r"(?<![A-Za-z'])(?:oh|o)(?![A-Za-z'])", re.I)
# a gap between digit groups that is only spoken separators: '720-275 and then 1554', '275 dash 1554'
_SPOKEN_GAP = re.compile(r"^[^0-9A-Za-z]*(?:(?:and|then|dash|hyphen|dot|point|space|x|plus)[^0-9A-Za-z]*){1,3}$", re.I)
_CHAIN_GAP = 24                                              # characters between two groups of one number
# the words that may stand between the groups of one spoken / split number ('720 dot 275 dot 1554', 'area code 720; the rest is
# 2751554', '720-275 and then 1554'); any other word ('units', 'Main', 'sq ft') ends the chain, so addresses and quantities pass
_CHAIN_WORDS = frozenset(
    "and then dot dash hyphen x point period space slash the rest is are its it's number numbers num no remaining digits digit "
    "followed by after that comes last first next plus area code prefix ends end in with of my his luke's lukes cell cellphone "
    "phone mobile line direct call text me at or to reach a an so again finally part half second third try dial hit then "
    "same as before local exchange extension ext".split())


def _spelled(s, join=r"[- ]?"):
    """Number words -> digits ('seven two zero' -> '7 2 0', 'fifteen fifty-four' -> '15 54', 'two75' -> '275'); 'oh' / 'o' next
    to a digit -> 0 ('seven two oh'). join: what may stand between 'fifty' and 'four' (a space too, or only a hyphen)."""
    def word(m):
        if m.group("tens"):
            return str(_TENS[m.group("tens").lower()]) + (str(_UNITS.index(m.group("unit").lower())) if m.group("unit") else "0")
        if m.group("teen"):
            return str(10 + _TEENS.index(m.group("teen").lower()))
        return str(_UNITS.index(m.group("one").lower()))
    s = _NUM_WORD[join].sub(word, s)

    def oh(m):
        before, after = s[max(0, m.start() - 4):m.start()], s[m.end():m.end() + 4]
        near = re.search(r"[0-9][ ,./-]{0,3}$", before) or re.match(r"^[ ,./-]{0,3}[0-9]", after)
        return "0" if near else m.group(0)
    return _OH.sub(oh, s)


def _chain_gap_ok(gap):
    return (len(gap) <= _CHAIN_GAP and "\n\n" not in gap
            and all(w.lower() in _CHAIN_WORDS for w in re.findall(r"[A-Za-z][A-Za-z']*", gap)))


def _chain_hit(s):
    """Digit groups joined by up to _CHAIN_GAP characters, words from _CHAIN_WORDS included ('720 dot 275 dot 1554', '720x275x1554',
    'Area code 720; the rest is 2751554', 'the number is 720-275 and then 1554'): -> (start, end) of the first chain that spells
    the full 7202751554 on group boundaries (a leading 1 allowed), or of 275 + 1554 joined only by spoken separators. "Bid number
    2751554" or "Section 2.75 and 1.554" is not his cell."""
    groups = list(re.finditer(r"[0-9]+", s))
    i = 0
    while i < len(groups):
        j = i
        while j + 1 < len(groups) and _chain_gap_ok(s[groups[j].end():groups[j + 1].start()]):
            j += 1
        chain = groups[i:j + 1]
        digits, starts, ends = "", set(), set()
        for g in chain:
            starts.add(len(digits))
            if g.group(0).startswith("1"):
                starts.add(len(digits) + 1)                  # 1-720-..., 17202751554
            digits += g.group(0)
            ends.add(len(digits))
        k = digits.find(LUKE_CELL)
        while k >= 0:
            if k in starts and k + len(LUKE_CELL) in ends:
                return chain[0].start(), chain[-1].end()
            k = digits.find(LUKE_CELL, k + 1)
        for a, b in zip(chain, chain[1:]):
            if a.group(0) == "275" and b.group(0) == "1554" and _SPOKEN_GAP.match(s[a.end():b.start()]):
                return a.start(), b.end()
        i = j + 1
    return None


def luke_cell_in(text):
    """The first run of digits that is Luke's cell, else None: a run whose digits hold 7202751554 (any separators of up to 8
    characters, a leading 1 or +1, look-alike letters for digits, HTML character references, spelled-out digits), the bare 275-1554
    with a separator, 2751554 right after a phone word ("cell 2751554"), or the number split by words ("720 dot 275 dot 1554",
    "area code 720; the rest is 2751554"). "Bid number 2751554" is not his cell."""
    base = _norm(text)
    variants = [(base, base), (_lookalikes(base, True), base), (_lookalikes(base, False), base)]   # (searched, shown)
    for words in dict.fromkeys(_spelled(base, join) for join in _NUM_WORD):
        if words != base:
            variants += [(words, words), (_lookalikes(words, True), words), (_lookalikes(words, False), words)]
    for s, shown in variants:
        for m in _RUN.finditer(s):
            groups = re.findall(r"[0-9]+", m.group(0))
            if (LUKE_CELL in "".join(groups) or any(a == "275" and b == "1554" for a, b in zip(groups, groups[1:]))
                    or (_LOCAL in groups and _PHONE_WORD.search(s[max(0, m.start() - 24):m.start()]))):
                start = m.start() - (1 if m.start() and s[m.start() - 1] in "(+" else 0)
                return " ".join(shown[start:m.end()].split())
    for s, shown in variants:
        hit = _chain_hit(s)
        if hit:
            return " ".join(shown[hit[0]:hit[1]].split())
    return None


def _flat(text):
    """_norm(), paragraphs (blank lines) kept as one newline each, every other run of whitespace one space ("Can we talk\\nby
    phone" is one phrase)."""
    s = _norm(text).replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(" ".join(p.split()) for p in re.split(r"\n[ \t]*\n", s))


_CLAUSE_END = re.compile(r"[,.;:!?()\[\]\"\n]")
_SENT_END = re.compile(r"[.!?\n]")


def _before(t, s, width=80):
    b = t[max(0, s - width):s]
    return b[max((m.end() for m in _CLAUSE_END.finditer(b)), default=0):]


def _after(t, e, width=80):
    a = t[e:e + width]
    m = _CLAUSE_END.search(a)
    return a[:m.start()] if m else a


def _sentence(t, s, e):
    a = max((m.end() for m in _SENT_END.finditer(t, 0, s)), default=0)
    m = _SENT_END.search(t, e)
    return t[a:m.start() if m else len(t)]


def _luke_near(t, s):
    """'him' / 'his' means Luke when Luke is named just before."""
    return "luke" in t[max(0, s - 150):s].lower()


# a negation that governs the phrase: the clause before it ENDS with the negation and at most 4 small words ("don't call", "please
# do not call me", "no phone call needed", "rather than a phone call", "email, not phone"). "Don't hesitate to call me", "if you
# can't find it call me" and "why not give me a call" stay invites.
_NEG = re.compile(r"(?:\b(?:don't|dont|do not|doesn't|does not|didn't|did not|can't|cant|cannot|can not|won't|will not|wouldn't|"
                  r"would not|shouldn't|should not|never|no|no need (?:to|for)|unable to|not able to|instead of|rather than|without|"
                  r"in place of|(?:better|easier|faster|quicker|simpler|more reliable|rather [\w']+) than)|(?<!\bwhy )\bnot)"
                  r"(?: (?:please|need|needs|to|have|has|be|able|take|taking|make|making|answer|return|get|jump|hop|on|a|an|the|any|"
                  r"for|set|setup|up|schedule|give|you|me|us|him|it|by|via|over|more|another|other|further|ever|again|phone|"
                  r"telephone|quick|call|calls|talk|speak|chat)){0,4} ?$", re.I)   # "can't talk on the phone", "better than a call"
_FIRST = re.compile(r"\b(?:i|i'm|i'll|i'd|i've|me|my|mine|we|we're|we'll|we'd|we've|us|our|ours|luke|luke's|brown bison)\b", re.I)
_PHOTO = re.compile(r"\b(?:photos?|pictures?|pics?|images?|videos?|camera|snapped|took|shot|screenshots?)\b", re.I)
# trade / third-party wording in the same sentence that makes "phone" someone else's line (only when nothing in it is ours)
_ANCHOR = re.compile(r"\b(?:dispatch\w*|answering service|hotline|on-call|on call|24/7|24-hour|24 hours?|after-hours|after hours|"
                     r"technicians?|techs?|crews?|foreman|foremen|operators?|tenants?|residents?|staff|service calls?|emergency|"
                     r"(?:trouble|repair|warranty|no-heat|no heat|no-cool|no cool|alarm|nuisance|tenant|customer|maintenance|"
                     r"after-hours|after hours|snow|plow) calls|"
                     r"emergencies|answer(?:s|ed|ing)? (?:the )?phones?|phone lines?|the (?:town|county|city|district|state|owner|"
                     r"buyer|agency|school|airport|base)(?:'s)?|forms?|w-9|sign-?in|roster|bid form|proposal)\b", re.I)
_TRADE_MOD = (r"service|emergency|after-hours|after hours|afterhours|overnight|weekend|holiday|night|trouble|repair|warranty|"
              r"maintenance|no-heat|no heat|no-cool|no cool|nuisance|dispatch|dispatched|conference|pre-bid|prebid|pre-proposal|"
              r"pre-submittal|presubmittal|pre-submission|pre-construction|preconstruction|kickoff|kick-off|bidders'?|vendors'?|"
              r"roll|judgment|judgement|right|wrong|close|tough|hard|final|sales|cold|duty|alarm|fire|911|panic|elevator|wake-up|"
              r"tenant|customer|work-order|work order|scheduled|unscheduled|routine|billable|non-billable|first|each|every|per|"
              r"single|minimum|trip|truck|pm|preventive|preventative|standby|stand-by|snow|plow|plowing|storm|outage|mutual aid")
_TRADE_BEFORE = re.compile(r"(?:\bon(?: ?- ?| )|\b(?:" + _TRADE_MOD + r")(?:[- ](?:tele)?phone)?[- ])$", re.I)
_TRADE_AFTER = re.compile(
    r"^(?:-?outs?\b|(?: (?:you|us|them|the crew|crews|a crew|a tech))? out\b|-ins?\b| in (?:number|info|details)\b"
    r"|[- ](?:lists?|rotations?|schedules?|logs?|sheets?|volumes?|cent(?:er|re)s?|responses?|times?|turnaround|fees?|charges?|"
    r"rates?|minimums?|records?|reports?|tickets?|queues?|tree|box(?:es)?|buttons?|stations?|systems?|data|history|counts?|"
    r"frequency|frequencies|signs?|types?|totals?|hours?|windows?|duration|priority|priorities|notes?|letters?|slips?|routing|"
    r"handling|takers?|intake|recordings?|tracking|accounting|premiums?|basis|threshold)\b"
    r"| for (?:new |additional |more )?(?:bids?|proposals?|quotes?|quotations?|qualifications?|service|tenders?|papers?|projects?|"
    r"submissions?|offers?|entries|applications?|vendors?|contractors?|interest|statements?|heat|heating|cooling|water|air)\b"
    r"| for (?:a |an |the |your |all |each |any )?(?:(?:utility|811|one-?call|line) )?(?:locates?|locate tickets?)\b"   # call for a locate
    r"| for (?:a |an |the |your |all |each |any |(?:the |a |an )?(?:final|rough-?in|framing|footing|city|county|town|state) )?"
    r"(?:inspections?|inspectors?)\b"                                                  # calling for inspections
    r"| in (?:the |a |an |your |our )?(?:(?:utility|811|one-?call|final|rough-?in|framing|footing|city|county|town|state) )?"
    r"(?:locates?|locate tickets?|tickets?|work orders?|service requests?|inspections?)\b"   # call in the locate / the inspection
    r"| (?:811|911)\b"                                                                  # we'll call 811 before we dig (review #5)
    # naming, not phoning (review #5, as on the Mac): "I'd call that a fair price", "We call this Option B"
    r"| (?:this|that|it|the (?:job|project|work|scope|site|lot|bid|item|unit|line)) (?:a|an|the|extra|option|phase|part|done|"
    r"complete|finished|final|base|alternate|our|substantially|even|good|fair)\b"
    r"| (?:is|was|has been|gets|got) (?:placed|received|logged|made|answered|dispatched|closed)\b| attention\b"
    r"|[- ]?backs? (?:within|response|time|in \d|inside|requirement|window|guarantee|of \d|under)\b"
    r"| it\b(?! in\b))", re.I)
_WHAT_WE_CALL = re.compile(r"\bwhat (?:we|they|you|people|i|the [\w ]{1,20}?) $", re.I)
_ORG = (r"(?:town|county|city|district|state|owners?|buyers?|agency|government|school|airport|base|contracting officer|co|"
        r"dispatchers?|dispatch|tenants?|residents?|inspectors?|supervisors?|managers?|staff|department|customers?|clients?|utility|"
        r"monitoring company|alarm company|answering service|system|bas|panel|controls?|operators?|purchasing|procurement)")
_GOV_SUBJ = re.compile(r"\b(?:the|a|an|each|every|any)(?: [\w'-]+){0,3}? " + _ORG + r"(?:'s)?(?: (?:will|would|may|can|could|"
                       r"shall|should|might|must|usually|typically|normally|often|always|then|is going to|are going to|plans? to|"
                       r"needs? to|wants? to|has to|have to)){0,2} $", re.I)
_OTHER_SUBJ = re.compile(r"(?:\b(?:they|she)|\b(?:your|their|her)(?: [\w'-]+){1,2})(?: (?:will|would|may|can|could|shall|should|"
                         r"might|must|usually|typically|then|is going to|are going to)){0,2} $", re.I)
_FIRST_OBJ = re.compile(r"^(?:-?me\b| (?:back )?(?:me|us|luke|our|my|brown bison|bb)\b)", re.I)
_POSS_BEFORE = re.compile(r"(?:\b(?:your|their|her|its)|(?<!\bluke)(?<!\blet)(?<!\bit)(?<!\bthat)(?<!\bwhat)(?<!\bhere)(?<!\bthere)"
                          r"(?<!\bwho)(?<!\bhe)(?<!\bshe)(?<!\bwhere)(?<!\bhow)'s)(?: [\w/-]+){0,2} $", re.I)   # not let's / it's
_HIS_BEFORE = re.compile(r"\bhis(?: [\w/-]+){0,2} $", re.I)
_GIVE_THIRD = re.compile(r"\bgive (?:(?:the|your|their|her|its|each|every) [\w' -]{1,40}?|them|her|(?!luke\b|brown\b)(?-i:[A-Z][a-z]+)"
                         r"(?: (?-i:[A-Z][a-z]+))?) a (?:quick |short |brief )?$", re.I)
_NOT_THE = (r"(?!(?:office|number|cell|cellphone|line|main line|phone|mobile|direct line|brown bison|bb|morning|afternoon|evening|"
            r"night|day|week|weekend|time|hour|minute|moment|second)\b)")
_THIRD_OBJ = re.compile(r"^ (?:back )?(?:(?:your|their|her|its) |(?:the|each|every|any|that|those|these|this) " + _NOT_THE
                        + r"|(?:them|they|her)\b|(?:to|with|from|between) (?:the|your|their|his|her|its|them|a|an|each|every)\b"
                        r"|\+?\(?\d)", re.I)
_NAME_AFTER = re.compile(r"^ (?:back |(?:to|with|from) )?(?-i:(?P<n>[A-Z][A-Za-z][A-Za-z'.&-]*))")   # Silas, Xcel, RTD
_NOT_NAMES = frozenset(
    "luke brown bison me us our my monday tuesday wednesday thursday friday saturday sunday mon tue tues wed thu thur thurs fri sat "
    "sun today tomorrow tonight anytime any anyone whenever back with if when after before or and then now soon later asap please "
    "ok okay thanks thank questions question quick the this that here there directly instead again sometime around once january "
    "february march april may june july august september october november december jan feb mar apr jun jul aug sep sept oct nov "
    "dec me. at in on to for about re regarding".split())

# review 2026-11-06 #4: a promise that Luke phones the reader's side. The subject is ours and stands right before the verb ('I'll',
# 'We'll be', 'Luke will', 'he can', 'I'm happy to'); the object is the reader or theirs ('your office', 'your PM', 'your cell', 'the
# shop', 'Jake', 'them'). Review #5 (CEO session 2026-11-06, Luke's rule: no operator promises that Luke will phone anyone): with a
# helper or contraction ('I'll', 'We'll', 'Luke can', 'let me') the promise is refused whatever the object ("We'll call the Town
# for the gate code", "I'll give the inspector a call"); field procedure (811, calling for / in an inspection or locate, in
# _TRADE_AFTER) and naming ("I'd call that a fair price") still pass, and "Give the inspector a call" (no subject of ours) is the
# reader's call.
_OURS = (r"\b(?P<subj>i|we|luke|he|brown bison)(?:'ll|'d|'m|'s|'re)?"
         r"(?: (?:will|would|can|could|shall|should|may|might|must|am|is|are|be|going to|gonna|plan to|plans to|want to|wants to|"
         r"need to|needs to|have to|has to|try to|tries to|also|just|then|probably|definitely|gladly|happily|quickly|first|still|"
         r"again|happy to|glad to|be sure to|make sure to|try and|to)){0,4}")
_OURS_SUBJ = re.compile(_OURS + r" $", re.I)
_STARTERS = frozenset("also so but yes no sorry hi hey hello just and or even still otherwise great sure fine he he'll he's he'd "
                       "if when".split())
_GIVE_OBJ = re.compile(r"\bgive (?P<obj>(?:[\w'-]+ ){1,3}?)a (?:quick |short |brief |fast )?$", re.I)
_READER_SIDE = re.compile(r"^ (?:back )?(?:(?:you|ya|u|ur|them|him|her)\b|your\b(?! attention\b)|(?:the|that) (?:shop|office|yard|"
                          r"front desk|desk|main line|line|cell|cellphone|mobile|number|landline|house|trailer|field office|"
                          r"site office)\b|(?-i:(?P<n>[A-Z][A-Za-z][A-Za-z'.&-]*)))", re.I)


def _ours_subject(t, s, before):
    """True when the clause before position s ends with a subject of ours and its helper verbs ('I'll ', 'Luke will '). 'he' is
    ours unless someone other than Luke is named earlier in the sentence ('Silas said he will call your office')."""
    m = _OURS_SUBJ.search(before)
    if not m:
        return False
    if m.group("subj").lower() != "he":
        return True
    sent = t[max((x.end() for x in _SENT_END.finditer(t, 0, s)), default=0):s]
    names = [n for n in re.findall(r"\b[A-Z][a-z]+\b", sent) if n.lower() not in _NOT_NAMES and n.lower() not in _STARTERS]
    return not names


def _reader_side(after):
    """'your office', 'the shop', 'Jake', 'them' right after the verb: the reader's side, or someone Luke would be phoning."""
    m = _READER_SIDE.match(after)
    return bool(m) and not (m.group("n") and m.group("n").lower().rstrip(".") in _NOT_NAMES)


_LET_ME = re.compile(r"\blet (?:me|us)(?: (?:just|quickly|also|first|go ahead and))* $", re.I)
_FIELD_GIVE = re.compile(r"^ (?:811|911)\b")                 # we'll give 811 a call
# review #5: ring as a verb, or 'give X a ring / buzz', promised by Luke's side to anyone ("I'll ring the inspector Monday", "I'll
# give the inspector a ring"); not a bell ("We'll ring the doorbell")
_RING_VERB = re.compile(r"(?<![\w-])ring(?![\w-])(?= (?:(?:the|your|their|his|her|its|each|every|any|that|those|these|this) "
                        r"(?!(?:door ?)?bells?\b|chimes?\b|buzzer\b)|(?:them|him|her)\b|(?-i:[A-Z])))", re.I)
_GIVE_RING = re.compile(r"\bgive (?P<obj>(?:[\w'-]+ ){1,3}?)a (?:quick |short |brief |fast )?(?:ring|buzz|holler|shout|bell|tinkle)\b",
                        re.I)


def _ours_promise(t, s, before):
    """Review #5: the clause before position s ends with Luke's side promising the call: a subject of ours with a helper or
    contraction ('I'll ', 'We'll ', 'Luke can ', 'he will ' when he is Luke) or 'let me ' / 'let us '. A bare 'We ' is not a promise
    ('We call this Option B')."""
    if _LET_ME.search(before):
        return True
    m = _OURS_SUBJ.search(before)
    return bool(m) and len(m.group(0).strip()) > len(m.group("subj")) and _ours_subject(t, s, before)

# "the call" as an event in RFP / trade wording (review 2026-11-06 #3): measured from it, billed, logged, answered by someone else
_DET = r"(?:the|a|an|each|every|any|that|this|one|such)"
_TIME_OF = re.compile(r"(?:\b(?:\d+|a|an|one|two|three|four|five|six|eight|ten|twelve|fifteen|twenty|thirty|forty-five|sixty|ninety|"
                      r"a few|several|half an?)[ -](?:hours?|hrs?|minutes?|mins?|days?|business days?|working days?)"
                      r"(?: or (?:less|fewer|sooner))? (?:of|from|after|following|since|upon)(?: (?:receipt of|receiving|logging))?"
                      r"|\b(?:time|moment|receipt|point|start|end|close|log) of|\bupon|\bupon receipt of) " + _DET + r" $", re.I)
_TRADE_VERB = re.compile(r"\b(?:bills?|billed|billing|charges?|charged|charging|invoices?|invoiced|invoicing|prices?|priced|pricing|"
                         r"logs?|logged|logging|records?|recorded|recording|documents?|documented|documenting|dispatch(?:es|ed|ing)?|"
                         r"quotes?|quoted|tickets?|ticketed|codes?|coded|counts?|counted|treats?|treated|close(?:s|d)? out) " + _DET
                         + r" $", re.I)                      # bill the call at the regular rate
_TAKE_VERB = re.compile(r"\b(?:takes?|took|taking|answers?|answered|answering|fields?|fielded|fielding|handles?|handled|handling|"
                        r"covers?|covered|covering|picks? up|picked up|picking up|responds? to|responded to|responding to|"
                        r"receives?|received|receiving|returns?|returned|returning|gets?|got|getting) " + _DET + r" $", re.I)
# a promise to return the reader's call ('I'll return your call this afternoon', 'he would return your call tonight')
_RETURN_YOURS = re.compile(r"\b(?:return|returns|returning|returned|get back to|getting back to) (?:your|ur)"
                           r"(?: (?:phone|missed|earlier|last|recent))? $", re.I)
_HE = re.compile(r"\b(?:he|he's|he'll|he'd|him|his)\b", re.I)
_BARE_YOU = re.compile(r"\b(?:you|you'll|you'd|you're|u|ya)\b", re.I)
# the clause opens with someone else as its subject: 'Your dispatcher will text you', 'The County will ring you', 'Silas can'
_THIRD_START = re.compile(r"^\s*(?:(?:and|so|then|but|also|otherwise)\s+)?(?:(?P<pron>they|she)\b|(?:your|their|her|the|each|every|"
                          r"a|an|that|this|its)\s+(?!and\b)[\w'-]+|(?-i:(?P<name>[A-Z][a-z]+))(?:'s)?\b)", re.I)


def _third_subject(t, s):
    """True when the clause before position s opens with a third party as its subject and holds nothing of ours (no I / we / Luke
    / he / Brown Bison): the call or text is between other people, not Luke and the reader."""
    before = _before(t, s)
    m = _THIRD_START.match(before)
    if not m or _FIRST.search(before) or _HE.search(before):
        return False
    return not (m.group("name") and m.group("name").lower() in _NOT_NAMES)


def _call_event_ok(t, s, before):
    """'the call' as an event in trade wording: 'within 2 hours of the call', 'bill the call at the regular rate', 'who takes the
    call when the alarm trips' (not 'I'll take the call', 'can you take the call Monday')."""
    if _TIME_OF.search(before) or _TRADE_VERB.search(before):
        return True
    return bool(_TAKE_VERB.search(before)) and not (_FIRST.search(before) or _HE.search(before) or _BARE_YOU.search(before))


_CALL = re.compile(r"(?<![\w])(?:call(?:ing)?(?![\w])|callme\b|phonecall\b)", re.I)   # not calls/called/caller/callback/recall
_PHONE = re.compile(r"(?<![\w])(?:tele)?phone(?![\w])(?![- ]?call)", re.I)          # "phone call" is checked as a call
_THIRD_AFTER = (r"(?! (?:to|with) (?:the|your|their|his|her|its|a|an|them|(?-i:[A-Z]))"
                r"| (?:numbers |it |this |that |more |details |the scope |pricing )?(?:through |over )?(?:by|over|via|in|on) (?:e-?mail|writing|the portal"
                r"|bidnet|this thread)| you (?:with|to|in)\b| policy\b)")
_CONNECT = r"connect(?=[.?!,;\n]| (?:by|on|over|via|this|next|tomorrow|today|later|soon|sometime|briefly|quickly)\b|$)"
_DAYS = r"(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
_TALK_THIRD = (r"(?!(?: (?:it|this|that|things|them))?(?: (?:over|through))? (?:to|with|about) (?:the|your|their|his|her|its|a|an|"
               r"them|that|this|it|(?-i:[A-Z])))")                                     # talk (it over) with the inspector
# review 2026-11-06 #4: filler between 'can we' / 'let's' and the verb ('should we just talk', 'can we jump on real quick'); hop / jump
# on with no object ('Can we hop on?'), not 'jump on it' / 'hop on the lift'; sync up
_FILLER = r"(?:(?:quickly|briefly|just|maybe|also|real quick|both|all|go ahead and|probably|still|even) )*"
_HOP = (r"(?:hop|jump) on\b(?! (?:it|this|that|these|those|site|board|the|a|an|your|our|my|their|his|her|its|each|every|any|all|"
        r"both)\b)")
_SYNC = (r"sync(?: up)?\b(?! (?:the|your|our|their|it|this|that|these|those|schedules?|calendars?|files?|data|drawings?|"
         r"folders?)\b)")
_OFFER_ADJ = (r"(?:fine|best|better|easier|easiest|easy|good|great|ok|okay|quick|quicker|quickest|fast|faster|fastest|simpler|"
              r"simplest|preferred|ideal|too|also|as well|for me|for us|for luke|way to go)")
_ADV = r"(?: (?:usually|always|probably|much|way|a lot|often|just|really|also|still|definitely|totally))?"
_CLAUSE_START = r"(?:^|(?<=\n)|(?<=[.!?;:,(] )|(?<=[.!?;:,(]))(?:(?:and|or|but|so|also|otherwise|else) )?"
INVITES = tuple(re.compile(p, re.I) for p in (
    r"\b(?:can|could|shall|should|may|might|would|will) (?:we|i) " + _FILLER + r"(?:talk|chat|speak|catch up|touch base|"
    + _HOP + r"|" + _SYNC + r"|" + _CONNECT + r")\b" + _THIRD_AFTER,                    # can we talk Monday? should we just talk?
    r"\blet(?:'s| us) " + _FILLER + r"(?:talk|chat|speak|catch up|touch base|hop on|jump on|get on|" + _SYNC + r"|" + _CONNECT
    + r")\b" + _THIRD_AFTER,                                                            # let's talk / let's just talk / let's connect
    r"\b(?:talk|speak|chat)(?: (?:to|with) (?:you|ya|u))? (?:soon|later|tomorrow|tmrw|tmr|tmw|tomoz|2morrow|2moro|tonight|then|"
    r"shortly|in a (?:bit|few|while|minute|min|sec|second)|in a few (?:minutes|mins|hours|hrs)|this (?:afternoon|evening|morning)|"
    r"later today|first thing|real soon|next week|this week|" + _DAYS + r")\b(?! in the\b)",   # talk soon, talk tmrw, talk in a bit
    r"\b(?:a few|a couple(?: of)?|some|a|\d+|five|ten|fifteen|twenty|thirty)[ -](?:minutes?|mins?)(?: (?:to|for))? (?:talk|chat|"
    r"speak|connect|catch up|touch base)\b",                                            # a few minutes to talk
    r"\b(?:a|the|good|best|convenient|better|free) time (?:to|for (?:a|an)) (?:quick )?(?:talk|chat|speak|connect|catch up|"
    r"touch base|conversation)\b",                                                      # a good time to talk, find a time to talk
    r"(?<!feel )\b(?:free|available|happy|glad|open|around) (?:to|for) (?:a )?(?:quick |short |brief )?(?:talk|chat|speak|hop on|"
    r"jump on|get on|conversation|" + _SYNC + r"|" + _CONNECT + r")\b" + _THIRD_AFTER,  # available to talk, free to connect
    r"\b(?:hit|ping) (?:me|us|luke) up\b", r"\bping (?:me|us|luke)\b(?! (?:by|on|via|over) e-?mail)",
    r"\b(?:hop|jump|get) on (?:a |an )?(?:zoom|teams|webex|google meet|meet|facetime|video)\b",
    r"\b(?:set ?up|schedule|book|arrange|grab|do|have) (?:a|an) (?:quick |short |brief )?(?:zoom|teams|webex|facetime|video|"
    r"google meet|gmeet|skype|gotomeeting|goto meeting)\b",                             # could we do a Google Meet
    r"\bleave (?:me |us |luke )?(?:a |your )?(?:voicemail|voice mail|vm|voice message)\b"
    r"(?! (?:for|at|with|on) (?:the|your|their|his|her|its|(?-i:[A-Z])))",           # not 'leave a voicemail for Jane'
    r"\b(?:my|our|luke's) (?:voicemail|voice mail)\b",
    r"\b(?:my|our|luke's) (?:cell|cellphone|cell phone|mobile|mobile phone|direct line|direct dial|direct number|office line|"
    r"personal line|personal number|landline|phone number|contact number|callback number|call-back number)\b"
    r"(?! (?:photos?|pictures?|pics?|videos?|camera|shots?)\b)",                        # my cell (not 'my cell photos')
    r"\b(?:my|our|luke's) number\b(?! (?:one|1|of)\b)",                                 # my number is below
    r"\b(?:on|to) (?:my|luke's) (?:cell|mobile)\b",
    r"\b(?:by|via|over) (?:cell|mobile|text|txt|sms|whatsapp|imessage|facetime|signal)\b(?! (?:file|box|field|tower)\b)",
    r"\b(?:text|txt|sms|whatsapp|imessage) (?:me|(?-i:us|Us)|luke)\b",                # text me / text us (not 'text US Code')
    r"\b(?:send|shoot|drop|fire|flick) (?:me|us|luke) a (?:quick )?(?:text|txt|sms)\b",
    r"(?<!\bthe )(?<!\bthis )(?<!\bthat )(?<!\bits )(?<!\bplain )(?<!\bfull )(?<!\bwhich )(?<!\bbody )"
    r"\b(?:text(?:ing|s)?|sms|whatsapp|imessage|signal) (?:is|are|works|work|would work|would be|'s)"
    r"(?: (?:usually|always|probably|much|way|a lot|often|just|really))? (?:the )?(?:fine|best|better|easier|easiest|easy|good|"
    r"great|ok|okay|quick|quicker|quickest|fast|faster|fastest|simpler|simplest|preferred|ideal|way to go)\b",   # text is quickest
    r"\ba text (?:works|would|is fine|is best)\b",
    r"\bfeel free to (?:text|ring|buzz|ping)\b",
    r"\bc/t\b",
    r"\b(?:ring|buzz) (?:me|us|luke)\b",
    r"\bgive (?:me |us |luke |our office |the office )?a (?:quick )?(?:ring|buzz|shout|holler|bell|tinkle)\b",
    r"\bring (?:any ?time|whenever)\b",
    r"\b(?:i|we|luke)(?:'ll|'d| will| can| could| would| shall) (?:ring|buzz|text) you\b",
    r"\b(?:good|best|right|direct|cell|phone|mobile|callback) number (?:to|for|where|at which) (?:i |we |luke )?(?:can )?(?:reach|"
    r"call|text|contact|get (?:a )?hold)",                                             # a good number to reach you
    r"\bwhat(?:'s| is)? (?:the |your )?(?:best |good )?(?:number|cell|phone) (?:can|could|should|do|would|will) (?:i|we|luke) "
    r"(?:reach|call|text|use)",                                                         # what number can I reach you at
    r"\bbest (?:phone |cell |mobile |contact |callback |call-back )?number (?:to|for) (?:reach|call|text|contact|get (?:a )?hold)",
    r"\bbest (?:phone|cell|mobile|contact|callback|call-back) number\b"
    r"(?![^.?!\n]{0,40}\b(?:sign-?in|form|sheet|roster|w-9|bid form|proposal)\b)",     # not '... number for the walk sign-in sheet'
    r"\breach (?:me|us|luke)(?: directly)? (?:at|on) [+(]?\d",                          # reach me at <any number>
    r"\breachable (?:at|on) [+(]?\d",
    r"\bcalls (?:are|is) (?:fine|welcome|ok|okay|best|easiest|easier|great|good|quicker|faster)\b", r"\bcalls welcome\b",
    r"\b(?:i|luke)(?:'ll|'m|'d|'s| will| can| do| am| is| would| also| usually| only| still| always| generally| normally)?"
    r"(?: (?:happy|glad|able|willing|available|free|open) to)? (?:take|takes|taking|return|returns|returning|answer|answers|"
    r"answering|field|fields|fielding) (?:your |any |phone |the |all |my )?calls\b",   # Luke takes calls after 5
    r"\b(?:happy|glad|able|willing|available|free|open) to (?:take|return|answer|field) (?:your |any |phone |the |all )?calls\b"
    r"(?! (?:from|for) (?:the |your |their )?(?:tenants?|residents?|customers?|dispatch|alarm|emergenc|after-hours|town|county|"
    r"city))",                                                                         # happy to take calls after 5
    r"\b(?:i|we)(?:'d| would)? (?:prefer|like|rather) (?:phone )?calls\b",
    # review 2026-11-06 #3: invites the first list missed
    r"\bholler(?: at)? (?:me|us|luke)\b",                                               # holler at me
    r"\b(?:hit|try|ring|buzz|dial)(?: (?:me|us|luke))?(?: (?:up )?(?:on|at))? (?:my|our|luke's) (?:line|lines|cell|cellphone|"
    r"mobile|phone|number|direct|direct line|landline|digits|office line)\b",          # hit my line
    r"\b(?:give|shoot|send|drop|throw|toss|fire|hit) (?:me|us|luke|our office|the office|the shop) a (?:quick |short |brief |"
    r"fast )?(?:ring|buzz|holler|bell|tinkle|shout)\b",                                 # shoot me a quick ring
    r"\bon the (?:horn|blower)\b",                                                      # get you on the horn
    r"\bdial (?:me|us|luke)\b",                                                         # dial me in
    r"\b(?:want|wanna|like|need|prefer|willing|able|love|ready|happy|glad) to (?:talk|chat|catch up|touch base|hop on|jump on)"
    r"\b" + _TALK_THIRD + _THIRD_AFTER,                                             # if you want to talk
    r"\b(?:we|i|luke and i)(?:'d|'ll| should| could| can| need to| ought to| must| have to| gotta| will| might)"
    r"(?: (?:quickly|briefly|probably|really|just|maybe|definitely|still))? (?:talk|chat|catch up|touch base)\b"
    + _TALK_THIRD + _THIRD_AFTER,                                                     # we should chat
    r"\b(?:chat|chatting|talk|talking|speak|speaking|connect|connecting|discuss|discussing|go over|going over|review|reviewing|"
    r"walk through|run through|sync|catch up|touch base)(?: [\w']+){0,3}? live\b(?![- ](?:load|loads|wire|wires|"
    r"wiring|electrical|electric|circuits?|parts?|work|panels?|lines?|feeds?|video|stream|data|traffic|equipment|conductors?|"
    r"power|voltage|bus|front|edge|oak)\b)",                                           # go over it live, connect live
    r"\b(?:whats ?app|imessage|face ?time|telegram|wechat|viber)\b",                    # Hit me on WhatsApp, FaceTime me
    # review 2026-11-06 #4 (13:40 MT probe): plain, casual and slangy drafting the lists above missed
    _OURS + r" give (?:your (?:[\w'-]+ ){1,2}|(?:the|that) (?:shop|office|yard|front desk|desk|main line|line|cell|number|house|"
    r"trailer)(?: [\w'-]+)? |(?-i:[A-Z][a-z]+) (?:(?-i:[A-Z][a-z]+) )?|them |her |him )a (?:quick |short |brief |fast )?(?:ring|"
    r"buzz|holler|shout|bell|tinkle)\b",                                                # I'll give your shop a ring
    _OURS + r" (?:(?:ring|buzz)(?: back)?|dial)(?= ?(?:[.,;:!?)\n]|$)| (?:you|ya|u|through|around|after|before|at|later|tomorrow|"
    r"tonight|today|this|first|when|once|if|again|sometime|then|shortly|soon|asap|in a|in the (?:morning|afternoon|evening)|"
    + _DAYS + r")\b)",                                                                   # I'll ring around 4, I'll ring through
    _OURS + r" (?:try|ring|buzz|dial|text) (?:you|ya|u|your (?:[\w'-]+ )?(?:cell|cellphone|mobile|phone|line|office|shop|number|"
    r"desk|landline|direct)|the (?:shop|office|front desk|desk|cell|line|number|landline|main line))\b",   # I'll try you at the shop
    r"\b(?:he|i|luke) (?:doesn't|don't|does not|do not|can't|cannot|won't|didn't|did not|may not|might not) pick up\b"
    r"(?! (?:the|a|an|your|our|his|my|it|them|plans|permits?|keys?|materials?|parts?|supplies|bids?|packets?|documents?|docs)\b)",
    r"\bleave (?:me |us |luke |him )?(?:a |your )?(?:message|msg)\b(?! (?:in|on|at|for|with|through|via) (?:the|your|their|his|"
    r"her|its|a|an|bidnet|(?-i:[A-Z])))",                                               # leave a message (and he'll call back)
    _CLAUSE_START + r"(?:phone )?calls(?: (?:after|before|between|around|until|from|on|in the) [\w:]+(?: ?(?:pm|am|p\.m\.|a\.m\.))?)?"
    r"(?: (?:work|works|would work)(?: (?:best|better|fine|great|too|well|for (?:me|us|luke)))\b| (?:are|is|'re|would be)" + _ADV
    + r" (?:fine|welcome|ok|okay|best|easiest|easier|great|good|quicker|faster|better|preferred|too)\b)",   # calls after 5 are best
    r"\b(?:a |the )?call-?back(?: works\b| would work\b| (?:is|'s|would be)" + _ADV + r" (?:too|also|fine|welcome|ok|okay|best|"
    r"easiest|easier|great|good|quicker|faster|better|preferred)\b)",                   # a callback works too (not 'callback work')
    r"\bcall-?backs(?: would work\b| work (?:best|better|fine|great|too|well|for (?:me|us|luke))\b| (?:are|would be)" + _ADV
    + r" (?:too|also|fine|welcome|ok|okay|best|easiest|easier|great|good|quicker|faster|better|preferred)\b)",   # callbacks are fine
    _CLAUSE_START + r"(?:cell|cellphone|cell phone|mobile|mobile phone|text|texting|texts|txt|sms|a text|a quick text)(?: (?:number|"
    r"line|message|msg))?(?: (?:after|before|until|around) [\w:]+(?: ?(?:pm|am))?)?(?: (?:works?|would work|will work|will do)\b|"
    r"(?:'s| is| are| would be| will be)" + _ADV + r" (?:the |a )?" + _OFFER_ADJ + r"\b)",  # Cell works. Text works too.
    r"\b(?:try|get|hit|reach|catch|grab|find|ring|buzz|ping|text|message|msg)(?: (?:me|us|luke)) (?:on|at|via) (?:the |my |our |"
    r"luke's )?(?:cell|cellphone|cell phone|mobile|mobile phone|digits|personal line|direct line)\b",   # try me on the cell
    r"\b(?:my|our|luke's) (?:digits|office number|main number|shop number|shop line|main line|business line|business number|"
    r"work number|work cell|work phone|office phone|shop phone|home number|home phone)\b",   # our office number is on the website
    r"\b(?:number|cell|phone|mobile|digits|contact info)(?:'s| is| are)? (?:in|on|at the bottom of|below|under) (?:my|our|luke's) "
    r"(?:sig|signature|email signature|e-?mail sig|footer|card|business card)\b(?! (?:block|line|page|sheet)s?\b)",   # in my sig
    r"\b(?:cell|cellphone|mobile|phone|direct|contact|office|callback) (?:number|#|line)s? (?:on|in|from|at the bottom of|under|"
    r"listed on|listed in) (?:my|our|luke's)\b",                                        # use the cell number on my W-9
    r"\b(?:my|our|luke's) (?:phone |cell )?lines? (?:is|are|'s|stays?)(?: (?:always|still|usually|wide))? open\b",   # my line is open
    r"\b(?:send|shoot|drop|fire|flick|leave|text) (?:me|us|luke) (?:an? )?(?:quick |short )?(?:sms|txt|text message|voice note|"
    r"voice memo|voice message|voicemail|voice mail|vm)\b",                             # send me an SMS, send me a voice note
    r"\b(?:message|msg|dm|text|ping|hit|find|reach|contact|catch|call) (?:me|us|luke) (?:on|via|over|through) (?:signal|whatsapp|"
    r"telegram|imessage|sms|wechat|viber|messenger)\b",                                 # message me on Signal
    r"\b(?:easier|quicker|faster|simpler|better|best|easiest|quickest|fastest|simplest|nicer) (?:to|if we|if i|if we just) "
    r"(?:just )?(?:talk|chat|speak|connect|catch up|touch base|" + _HOP + r")\b" + _TALK_THIRD + _THIRD_AFTER,   # easier to talk?
    r"\b(?:talk|chat|speak)(?:ing)? (?:than|instead of|rather than|vs\.?|versus) (?:type|typing|write|writing|e-?mail|e-?mailing|"
    r"text|texting|messages?|messaging)\b",                                             # quicker to talk than type
    r"\b(?:rather|prefer to) (?:just )?(?:talk|chat|speak|" + _HOP + r")\b" + _TALK_THIRD + _THIRD_AFTER,   # rather talk than type
    r"\b(?:i|we)(?:'ll|'d| can| could| will| would| should| shall| might| may)?(?: (?:quickly|briefly|just|both|all|also|happily|"
    r"gladly))? " + _HOP + r"(?! (?:to|with) (?:the|their|his|her|its|(?-i:[A-Z])))",    # Brad and I can hop on with you at 9
    r"\b(?:have|got|spare|find|grab|give me|give us)(?: (?:you|me|us))? (?:a few|a couple(?: of)?|some|\d+|five|ten|fifteen|"
    r"twenty|thirty)[ -](?:minutes?|mins?)(?: [\w']+){0,3}? (?:to|for) (?:a )?(?:quick )?(?:talk|chat|speak|connect|catch up|"
    r"touch base|go over|go through|walk through|run through|discuss|sync|hop on|jump on)\b" + _TALK_THIRD,   # 10 minutes to go over
    r"\b(?:a|an|the|my|our|your) (?:ms |microsoft )?(?:teams|zoom|webex|google meet|gotomeeting|skype|facetime|video) (?:invite|"
    r"invitation|link|meeting|session|call)s?\b(?![^.?!\n]{0,60}\b(?:pre-?bid|pre-?proposal|pre-?submittal|bidders?'? conference|"
    r"addend\w*|site walk|site visit|walk-?through|public meeting|board meeting|bid opening)\b)",   # send a Teams invite
    r"\bhmu\b", r"\bholla(?: at)? (?:me|us|luke)\b",                                    # hmu, holla at me
))
# the same, but for a call or text to the READER, which is fine when someone else is the subject ('Your dispatcher will text you',
# 'The County will ring you'): 'Luke will give you a buzz', 'I'll ring you back', 'Luke's going to buzz you', 'talk it through'
INVITES_YOU = tuple(re.compile(p, re.I) for p in (
    r"(?<![-\w])(?<!\bthe )(?<!\ba )(?<!\ban )(?<!\bthat )(?<!\bthis )(?<!\byour )(?<!\bmy )(?<!\bour )(?<!\bany )(?<!\bits )"
    r"(?:ring|buzz|text|txt|sms|holler at) (?:you|ya|u)\b(?! (?:ordered|sent|wrote|quoted|supplied|need|needed|asked|mentioned|"
    r"requested|used|have|had|got|gave|forwarded|attached)\b)",                        # ring you back, buzz you, text you
    r"\b(?:give|shoot|send|drop|throw|toss|fire|hit) (?:you|ya) a (?:quick |short |brief |fast )?(?:ring|buzz|holler|bell|"
    r"tinkle|shout)\b",                                                                 # give you a ring
    r"\bring (?:the|our|my) (?:shop|office|front desk|desk|main line|line|cell|number|landline|yard|house)\b",   # ring the shop
    r"\bhit (?:you|ya|u) up\b",                                                         # Luke will hit you up Monday
    r"\b(?:reached|reachable|reach (?:me|us|luke)|find (?:me|us|luke)|get (?:me|us|luke)|catch (?:me|us|luke)) (?:at|on|via|through) "
    r"(?:the |my |our |luke's |his )?(?:(?:shop|office|main|direct|personal|work|home|cell|mobile|business) )?(?:line|lines|number|"
    r"phone|cell|cellphone|mobile|landline|digits|extension)\b",                        # I can be reached at the shop line
    r"\btalk(?:ing)?(?: (?:it|this|that|things|them|these|those|everything))? (?:through|over)\b(?! (?:by |over |via |in |on )?"
    r"(?:e-?mail|writing|the portal|bidnet|this thread)\b)(?! with (?:the|your|their|his|her|its|them|(?-i:[A-Z])))",  # talk it through
))
# 'Best way to get Luke is his cell after 5': 'his' is Luke when he is named just before (_luke_near)
_HIS_LINE = re.compile(r"\bhis (?:cell|cellphone|cell phone|mobile|mobile phone|direct line|direct dial|direct number|personal line|"
                       r"personal number|number|phone number|line|landline|digits)\b(?! (?:photos?|pictures?|pics?|videos?)\b)", re.I)


def _third_object(t, e, after):
    """The call goes to someone else: 'call the Town procurement office', 'call your supplier', 'call them', 'a call with the
    County', 'call 811', 'call Silas'. Not 'call the office', 'call the number below', 'call this afternoon', 'call him' (Luke)."""
    if _THIRD_OBJ.match(after):
        return True
    if re.match(r"^ (?:back )?(?:him|his)\b", after, re.I):
        return not _luke_near(t, e)
    m = _NAME_AFTER.match(after)
    return bool(m) and m.group("n").lower().rstrip(".") not in _NOT_NAMES


def _call_ok(t, s, e):
    """True when this 'call' / 'calling' / 'phone call' is not an invitation to phone Luke (see the comment above LUKE_CELL)."""
    word = t[s:e].lower()
    before, after = _before(t, s), _after(t, e)
    if _NEG.search(before):
        return True
    if word == "callme":
        return False
    if _TRADE_BEFORE.search(before) or _TRADE_AFTER.match(after) or _WHAT_WE_CALL.search(before):
        return True
    if _call_event_ok(t, s, before):
        return True
    ret = _RETURN_YOURS.search(before)
    if ret:                                                  # I'll return your call: ours, unless the Town returns it
        return _third_subject(t, s - len(before) + ret.start())
    if _GOV_SUBJ.search(before):
        return True                                          # the City will call us for each repair
    first_obj = bool(_FIRST_OBJ.match(after)) or (bool(re.match(r"^ (?:back )?him\b", after, re.I)) and _luke_near(t, s))
    if first_obj:
        return False
    give = _GIVE_OBJ.search(before)                          # I'll give your office a call / Luke will give Jake a call
    if give:
        gs, gb = s - len(before) + give.start(), before[:give.start()]
        if _FIELD_GIVE.match(" " + give.group("obj")):
            return True                                      # we'll give 811 a call before we dig
        if _ours_promise(t, gs, gb) or (_ours_subject(t, gs, gb) and _reader_side(" " + give.group("obj"))):
            return False                                     # I'll give the inspector a call (review #5), let me give your PM a call
    elif _ours_promise(t, s, before) or (_ours_subject(t, s, before) and _reader_side(after)):
        return False                                         # I'll call the Town (review #5), Luke will call your office / Jake
    if _OTHER_SUBJ.search(before):
        return True                                          # their crew will call the Town
    give = _GIVE_THIRD.search(before)
    if give or re.search(r"\bgive him a (?:quick )?$", before, re.I):
        return bool(give) or not _luke_near(t, s)
    if _POSS_BEFORE.search(before) or (_HIS_BEFORE.search(before) and not _luke_near(t, s)):
        return True                                          # your call (a decision), their phone call
    return _third_object(t, e, after)


# review 2026-11-06 #4: phone / telephone as equipment or a utility in specs ('Replace the phone jack', 'phone and data cable', 'a
# VoIP phone system', 'the elevator phone', 'telephone poles', 'the phone company'), unless it is ours ('my desk phone')
_PHONE_GEAR_AFTER = re.compile(
    r"^(?: and | & | ?/ ?)(?:data|low[- ]voltage|cable|cabling|wiring|intercom|network)\b"
    r"|^[ -](?:jacks?|cables?|cabling|wires?|wiring|systems?|data|outlets?|ports?|handsets?|sets?|support|poles?|pedestals?|"
    r"company|companies|closets?|rooms?|backboards?|conduits?|drops?|risers?|terminals?|terminations?|blocks?|panels?|carriers?|"
    r"providers?|utilit(?:y|ies)|booths?|entry|rough-?ins?|devices?|equipment|switch(?:es)?|pbx|trunks?|circuits?|cords?|"
    r"boxes?|stations?|instruments?|demarcs?|demarcation|vaults?|manholes?|ducts?|duct ?banks?|service entrances?|"
    r"lines? (?:to|from|into|for the|at the|between|in the))\b", re.I)
_PHONE_GEAR_BEFORE = re.compile(
    r"\b(?:voip|ip|sip|elevator|emergency|courtesy|pay|house|desk|wall|lobby|cordless|analog|digital|cellular|satellite|refuge|"
    r"area of refuge|rescue assistance|blue-light|blue light|entry|door|gate|fire|firefighters?'?|security|guard|speaker|"
    r"hands-?free|intercom|cab|car|pool|panic|existing|abandoned|new|replacement|spare)[ -]$", re.I)
_OURS_POSS = re.compile(r"\b(?:my|our|luke's|his|me|us)\b(?: [\w-]+)? $"                     # my desk phone, us by the shop phone
                        r"|\b(?:me|us|luke|him|my|our|luke's)\b.*\b(?:on|at|via|by|through|to)(?: (?:the|a|an|my|our|his|luke's))?"
                        r"(?: [\w-]+)? $", re.I)                                            # reach me on the desk phone


def _phone_ok(t, s, e):
    """True when this 'phone' / 'telephone' is not Luke's line offered to the reader."""
    before, after = _before(t, s), _after(t, e)
    if _NEG.search(before):
        return True
    sent = _sentence(t, s, e)
    if _PHOTO.search(sent):
        return True                                          # photos from my phone are attached
    if _POSS_BEFORE.search(before) or (_HIS_BEFORE.search(before) and not _luke_near(t, s)):
        return True                                          # your on-call phone number, his phone number is on the W-9
    if not _OURS_POSS.search(before) and (_PHONE_GEAR_AFTER.match(after) or _PHONE_GEAR_BEFORE.search(before)):
        return True                                          # the phone jack, phone and data cabling, the elevator phone
    if (re.match(r"^(?: number)?\W{0,3}[+(]?\d", t[e:e + 16])
            and not re.search(r"\b(?:my|our|luke's)(?: [\w-]+)? $", before, re.I)):
        return True                                          # Phone: 719-694-0515 (someone else's; Luke's is caught by number)
    return bool(_ANCHOR.search(sent)) and not _FIRST.search(sent)   # the dispatcher answers the phone


def _snip(t, s, e):
    pre = _before(t, s, 40).split()[-3:]
    post = _after(t, e, 40)
    words = post.split()
    tail = (" " + " ".join(words[:2])) if post[:1] == " " else (words[0] if words else "")
    return " ".join(pre + [t[s:e] + tail]).strip()


def call_invites(text):
    """Every call invite in text (see the comment above LUKE_CELL), in order, one per place: the default-refused call/phone words
    with a few words around them, and the INVITES phrases."""
    t = _flat(text)
    hits = []
    for m in _CALL.finditer(t):
        if not _call_ok(t, m.start(), m.end()):
            hits.append((m.start(), m.end(), _snip(t, m.start(), m.end())))
    for m in _PHONE.finditer(t):
        if not _phone_ok(t, m.start(), m.end()):
            hits.append((m.start(), m.end(), _snip(t, m.start(), m.end())))
    for rx in INVITES:
        for m in rx.finditer(t):
            if not _NEG.search(_before(t, m.start())):
                hits.append((m.start(), m.end(), m.group(0)))
    for rx in INVITES_YOU:
        for m in rx.finditer(t):
            if not _NEG.search(_before(t, m.start())) and not _third_subject(t, m.start()):
                hits.append((m.start(), m.end(), m.group(0)))
    for m in _HIS_LINE.finditer(t):
        if _luke_near(t, m.start()) and not _NEG.search(_before(t, m.start())):
            hits.append((m.start(), m.end(), m.group(0)))
    for rx in (_RING_VERB, _GIVE_RING):                      # review #5: I'll ring the inspector, I'll give the Town a ring
        for m in rx.finditer(t):
            before = _before(t, m.start())
            if rx is _GIVE_RING and _FIELD_GIVE.match(" " + m.group("obj")):
                continue
            if not _NEG.search(before) and _ours_promise(t, m.start(), before):
                hits.append((m.start(), m.end(), _snip(t, m.start(), m.end()) if rx is _RING_VERB else m.group(0)))
    found, last = [], -1
    for s, e, phrase in sorted(hits):
        if s >= last and phrase.lower() not in (f.lower() for f in found):
            found.append(phrase)
        last = max(last, e)
    return found


def phone_problems(text, where="body", phrases=True):
    """Luke's hard rule of 2026-11-06 for mail to anyone but him: no cell number in any format, no invitation to phone him.
    phrases=False checks the number only (a thread's own "Re:" subject)."""
    probs = []
    cell = luke_cell_in(text)
    if cell:
        probs.append(f"{where}: Luke's cell number {cell[:40]!r}. " + PHONE_FIX)
    hits = call_invites(text) if phrases else []
    if hits:
        shown = ", ".join(repr(h[:60]) for h in hits[:4]) + (f" (+{len(hits) - 4} more)" if len(hits) > 4 else "")
        probs.append(f"{where}: call invite {shown}. " + PHONE_FIX)
    return probs


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
    probs = (char_problems(body) + structure_problems(body, tail) + budget_problems(body, n, note) + link_problems(body)
             + phone_problems(body))
    ok, errs, warns = _hz(prose(body), n, hz_py=hz_py)
    probs += errs
    return (ok and not probs), probs, warns, n


def check(body, asks=None, inbound=None, hz_py=None, tail="none"):
    """-> (ok, problems): lint() without the warnings."""
    ok, probs, _warns, _n = lint(body, asks=asks, inbound=inbound, hz_py=hz_py, tail=tail)
    return ok, probs


def subject_problems(subject, hz_py=None, run_hz=True, threaded=False):
    """The subject of outside mail: one line, no invisible characters, never Luke's cell; unless it is a thread's own "Re:"/"Fwd:"
    subject, also no look-alikes, emoji, links, call invites or hz.py --chat ERROR (dashes, curly quotes, banned phrases).
    A "Re:"/"Fwd:" subject is the thread's own only when the message really is threaded (threaded=True: gmail_api.py --thread, a
    connector replyThreadId / replyToMessageId, or a reply tool); typing "Re:" on a new message does not skip the call-invite check.
    run_hz=False (hz.py already failed closed on the body) skips the hz.py run so a hung linter costs one timeout, not two."""
    s = str(subject if subject is not None else "")
    if not s.strip():
        return ["subject: empty; outside mail needs a subject line"]
    if any(ch in s for ch in "\r\n\x85  "):
        return ["subject: a line break inside the subject"]
    if REPLY_SUBJECT.match(s):
        return ([p for p in char_problems(s, "subject") if "invisible" in p or "control" in p]
                + phone_problems(s, "subject", phrases=not threaded))
    probs = char_problems(s, "subject") + link_problems(s, "subject") + phone_problems(s, "subject")
    if not run_hz:
        return probs
    ok, errs, _warns = _hz(s.strip() + "\n", 0, chat=True, hz_py=hz_py)
    return probs + [("subject: " + e) for e in errs]


def attachment_problems(files):
    """files: paths/names, or (name, mime type) pairs. Text-like attachments carry unlinted prose, so outside mail cannot carry
    them."""
    import mimetypes
    bad, cell = [], []
    for f in files or []:
        name, ctype = (f if isinstance(f, (tuple, list)) else (f, None))
        name = str(name or "")
        ctype = str(ctype or mimetypes.guess_type(name)[0] or "").lower()
        if Path(name).suffix.lower() in TEXT_ATTACH_EXT or ctype.startswith(TEXT_ATTACH_TYPES):
            bad.append(Path(name).name or ctype)
        if luke_cell_in(Path(name).name):                    # the file NAME (its contents are not read here)
            cell.append(Path(name).name)
    probs = []
    if bad:
        probs.append(f"attachment {', '.join(bad)}: plain-text, HTML, Markdown, RTF or mail attachments carry unlinted text; put "
                     "the words in the humanized body, or send a PDF/Office file")
    if cell:
        probs.append(f"attachment name {', '.join(repr(c[:60]) for c in cell)}: Luke's cell number in the file name; rename the "
                     "file. " + PHONE_FIX)
    return probs


# ---------------------------------------------------------------------------------------------------------------- recipients
def owner_only(recipients):
    """True only when there is at least one recipient and EVERY one is an ASCII address in OWN (case-insensitive, surrounding
    spaces ignored), written bare ('luke@brownbisonco.com') or in the plain display-name form ('Luke Adams <luke@brownbisonco.com>',
    '"Luke Adams" <lukemitchelladams@gmail.com>', '<luke@brownbisonco.com>'). The address inside the brackets is matched exactly;
    a display name holding '@', '<', ',', ';' or a quote, a second address, 'a@b, c@d', 'a@b;c@d', newlines, non-ASCII look-alikes
    (the Kelvin sign) or anything else is not owner-only, so that mail is linted."""
    if isinstance(recipients, str):
        recipients = [recipients]
    addrs = []
    for r in recipients or []:
        if r is None:
            continue
        s = str(r)
        if not s.isascii():
            return False
        s = s.strip(" ")
        m = _DISPLAY_FORM.fullmatch(s)
        addrs.append((m.group("addr") if m else s).lower())
    return bool(addrs) and all(BARE_ADDRESS.fullmatch(a) is not None and a in OWN for a in addrs)


# ---------------------------------------------------------------------------------------------------------------- MCP hook
MAIL_TOOLS = frozenset({"send_message", "reply", "reply_all", "forward", "send_draft", "send_email"})
REPLY_TOOLS = frozenset({"reply", "reply_all"})
TEXT_KEYS = ("body", "forwardText", "forward_text", "text", "content", "message", "note", "comment")
HTML_KEYS = ("htmlBody", "html_body", "html")
SHAPE_KEYS = ("messageId", "draftId", "replyThreadId", "replyToMessageId", "forwardText", "htmlBody", "html_body", "subject")
HOOK_FIX = ("Write it with /humanize: 'Hi <FirstName>,', the message, 'Thanks <FirstName>,', then the four signature lines ("
            + " / ".join(SIGNATURE_LINES) + ", no phone line) and nothing else. Pre-check: python3 scripts/humanize_gate.py check "
            "FILE --signature. "
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
    """At most 6 problems, phone problems first, with PHONE_FIX said once at the end (never cut off with the 7th problem)."""
    phone = [p for p in problems if p.endswith(PHONE_FIX)]
    ps = [p[: -len(PHONE_FIX)].rstrip(" .") for p in phone] + [p for p in problems if not p.endswith(PHONE_FIX)]
    out = "; ".join(ps[:6]) + (f"; ... {len(ps) - 6} more" if len(ps) > 6 else "")
    return out + (". " + PHONE_FIX if phone else "")


def _field(k, p):
    """'body: <problem>' from lint() under the connector field it came from: 'forwardText: ...', never 'body: body: ...'."""
    return f"{k}: {p[len('body: '):]}" if p.startswith("body: ") else f"{k}: {p}"


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
    if tool == "forward":
        # Luke 2026-11-06: the connector sends the original message (and its quoted thread) under forwardText, and this hook reads
        # only forwardText. Every email sent before 2026-11-06 carries "(720) 275-1554" in its signature, and replies quote it.
        return _deny(f"forward to {', '.join(rcpts) or 'the recipients'} is refused: a forward carries the original message and "
                     "its quoted thread, which this hook cannot read (mail before 2026-11-06 carries Luke's cell in the signature). "
                     "Write a new humanized message instead (send_message, or scripts/gmail_api.py send with the file attached), "
                     "or forward it to Luke. " + PHONE_FIX)
    texts = [(k, ti[k]) for k in TEXT_KEYS if isinstance(ti.get(k), str) and ti[k].strip()]
    if not texts:
        return _deny(f"{tool} has no plain-text body to check. " + HOOK_FIX)
    body_probs, broken = [], False
    for k, v in texts:
        ok, problems, _warns, _n = lint(v, asks=0, hz_py=hz_py, tail="signature")
        broken = broken or hz_failed(problems)
        if not ok:
            body_probs += [_field(k, p) for p in problems] or [f"{k}: hz.py lint did not PASS"]
    atts = [(a.get("filename"), a.get("mimeType")) for a in (ti.get("attachments") or []) if isinstance(a, dict)]
    probs = attachment_problems(atts)
    threaded = tool in REPLY_TOOLS or bool(str(ti.get("replyThreadId") or ti.get("replyToMessageId") or "").strip())
    if ti.get("subject") is not None or (tool in ("send_message", "send_email") and not threaded):
        probs += subject_problems(ti.get("subject"), hz_py=hz_py, run_hz=not broken,   # a new message needs a clean subject
                                  threaded=threaded)
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
