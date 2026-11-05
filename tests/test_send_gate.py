#!/usr/bin/env python3
"""Offline tests for the humanize gate on the cloud senders (Luke's hard rule, 2026-11-05).

    python3 -m pytest -q tests/test_send_gate.py

Covers scripts/humanize_gate.py (prose cut, structure, the gate's own word count, look-alike characters, links, subjects,
attachments, asks evidence, hz.py fail-closed, owner-only exemption, the Gmail-connector PreToolUse hook and its settings entry),
scripts/gmail_api.py send (refuses with exit 3 before any token or network call; Operations Manager signature; call() refuses an
unarmed POST to the send endpoints) and scripts/send_outbox.py (its own sibling sender, manifest validation, REFUSED entries never
recorded, nonzero exit). Nothing here can send mail: every test runs with urllib/socket connects replaced by a function that
raises, gmail_api's access_token/call/_env are stubbed, and the end-to-end run goes through a shim that stubs the same calls in the
child process with no GMAIL_* variables. The corpus test runs every ops/outbox/*/*.txt body and every manifest subject.
"""
from __future__ import annotations

import base64
import email
import importlib.util
import io
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from email import policy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
OUTBOX = ROOT / "ops" / "outbox"
DAY = OUTBOX / "2026-11-05"
PASSING_1105 = ["boettcher-chase.txt", "carbonvalley-chase.txt", "fortcollins-doors.txt", "metro-chase.txt", "uscg-ak017.txt"]
WELD = DAY / "weld-second-walk.txt"
BRAND = Path("/Users/thecreator/brown-bison-gov/data/brand.py")   # the Mac's canonical signature (absent in cloud containers)
GMAIL_VARS = ("GMAIL_CLIENT_ID", "GMAIL_CLIENT_SECRET", "GMAIL_REFRESH_TOKEN")

GOOD = "Hi Sam,\n\nCan you price the chiller replacement by Friday, November 13? The addendum is attached.\n\nThanks Sam,\n"
_PARA = ("The crew will start at the north gate on Monday at seven. They will work through the east wing by noon. "
         "We will send the site log to you each night.")                                  # 31 words, 3 sentences
LONG = "Hi Sam,\n\n" + "\n\n".join([_PARA] * 6) + "\n\nThanks Sam,\n"          # 186 prose words: over 150 (asks 0), under 225 (asks 5)
MID = "Hi Sam,\n\n" + "\n\n".join([_PARA] * 4) + "\n\nThanks Sam,\n"           # 124 prose words: under the cap, over the target
INBOUND5 = "Hi Luke,\n\nCan you start Monday? Who runs the crew? What time? Which gate? Do you need a lift?\n\nSam\n"
SIG_TAIL = "\nLuke Adams\nOperations Manager\nBrown Bison Holdings LLC\n"
SIG = "Luke Adams\nOperations Manager\nBrown Bison Holdings LLC\n(720) 275-1554\nluke@brownbisonco.com"
GOOD_MCP = GOOD.rstrip("\n") + "\n\n" + SIG + "\n"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gate = _load("test_pl_humanize_gate", SCRIPTS / "humanize_gate.py")


class NetworkTouched(AssertionError):
    pass


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """Any HTTP or socket connect in this process raises, and no Gmail credential variable is visible."""
    def boom(*a, **k):
        raise NetworkTouched("a network call was attempted")
    monkeypatch.setattr(urllib.request, "urlopen", boom)
    monkeypatch.setattr(socket.socket, "connect", boom)
    monkeypatch.setattr(socket, "create_connection", boom)
    for k in GMAIL_VARS:
        monkeypatch.delenv(k, raising=False)


@pytest.fixture
def gm(monkeypatch):
    """scripts/gmail_api.py with every token/API/credential entry point replaced by a recorder that raises."""
    g = _load("test_pl_gmail_api", SCRIPTS / "gmail_api.py")
    g.touched = []

    def boom(*a, **k):
        g.touched.append(a)
        raise NetworkTouched("gmail_api reached the token/API step")
    for name in ("access_token", "call", "_env", "_env_file"):
        monkeypatch.setattr(g, name, boom)
    return g


def _send(g, monkeypatch, *argv):
    monkeypatch.setattr(sys, "argv", ["gmail_api.py", "send", *argv])
    g.main()


def _refused(g, monkeypatch, capsys, *argv):
    """Run gmail_api send, expect the humanize refusal; -> stderr."""
    with pytest.raises(SystemExit) as ei:
        _send(g, monkeypatch, *argv)
    err = capsys.readouterr().err
    assert ei.value.code == 3, err
    assert err.startswith("HUMANIZE: ") and err.rstrip().endswith("Write it with /humanize (hz.py lint to PASS) and resend."), err
    assert g.touched == []
    return err


def _body(tmp_path, text, name="body.txt"):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return str(p)


def _fake_hz(tmp_path, code):
    p = tmp_path / "fake_hz.py"
    p.write_text(code, encoding="utf-8")
    return p


def _hz_direct(text, asks=0):
    """hz.py lint run straight (no gate): -> (exit code, stdout)."""
    p = Path(os.environ.get("TMPDIR", "/tmp")) / f"hz-direct-{os.getpid()}.txt"
    p.write_text(text, encoding="utf-8")
    try:
        r = subprocess.run([sys.executable, "-I", str(gate.REPO_HZ), "lint", str(p), "--asks", str(asks)], capture_output=True,
                           text=True, timeout=60)
    finally:
        p.unlink()
    return r.returncode, r.stdout


# ---------------------------------------------------------------------------------------------------------------- the linter
def test_only_the_repo_copy_of_hz_py_runs():
    assert gate.find_hz() == gate.REPO_HZ == ROOT / ".claude" / "skills" / "humanize" / "scripts" / "hz.py"
    assert gate.HZ_CANDIDATES == (gate.REPO_HZ,), "a hand-made ~/.claude copy must never stand in for the reviewed linter"


def _counting_hang(tmp_path):
    log = tmp_path / "hz-runs.log"
    hz = _fake_hz(tmp_path, f"import time\nopen({str(log)!r}, 'a').write('run\\n')\ntime.sleep(30)\n")
    return hz, log


def test_a_hung_hz_costs_one_timeout_per_send(gm, monkeypatch, capsys, tmp_path):
    g2 = _load("test_pl_humanize_gate_hang", SCRIPTS / "humanize_gate.py")
    hz, log = _counting_hang(tmp_path)
    g2.HZ_CANDIDATES, g2.TIMEOUT = (hz,), 1
    monkeypatch.setattr(gm, "_gate", lambda: g2)
    err = _refused(gm, monkeypatch, capsys, "--to", "sam@example.com", "--subject", "Chiller pricing", "--body-file",
                   _body(tmp_path, GOOD))
    assert "timed out" in err
    assert log.read_text().count("run") == 1, "the subject must not wait out a second timeout"


def test_a_hung_hz_costs_one_timeout_per_hook_call(tmp_path, monkeypatch):
    hz, log = _counting_hang(tmp_path)
    monkeypatch.setattr(gate, "TIMEOUT", 1)
    out = gate.hook_decision(json.dumps({"tool_name": "mcp__Gmail__send_message", "tool_input": {
        "to": ["sam@example.com"], "subject": "Chiller pricing", "body": GOOD_MCP}}), hz_py=hz)
    assert _denied(out) and "timed out" in out["hookSpecificOutput"]["permissionDecisionReason"]
    assert log.read_text().count("run") == 1


@pytest.mark.parametrize("name", PASSING_1105)
def test_1105_bodies_pass(name):
    ok, probs = gate.check((DAY / name).read_text(encoding="utf-8"))
    assert ok, probs


def test_weld_second_walk_fails():
    ok, probs = gate.check(WELD.read_text(encoding="utf-8"))
    assert not ok
    text = " | ".join(probs)
    assert "greeting 'Hi,' has no name" in text
    assert "closer 'Thanks,' must be exactly" in text


def test_prose_cuts_at_first_closer():
    body = "Hi Sam,\n\nOne line.\n\nThanks Sam,\n\nMore text.\n\nThanks Sam,\n"
    assert gate.prose(body) == "Hi Sam,\n\nOne line.\n\nThanks Sam,"
    assert gate.prose("Hi Sam,\n\nNo closer here.\n") == "Hi Sam,\n\nNo closer here.\n"
    assert gate.prose("Hi Team,\n\nx\n\nThanks Team,") == "Hi Team,\n\nx\n\nThanks Team,"


def test_good_body_passes_with_crlf_bom_nbsp_and_accents():
    assert gate.check(GOOD)[0]
    assert gate.check(GOOD.replace("\n", "\r\n"))[0]
    assert gate.check("﻿" + GOOD)[0]
    assert gate.check(GOOD + "\n\n  \n")[0], "blank lines after the closer are fine"
    assert gate.check(GOOD.replace("Friday, November", "Friday, November"))[0], "a pasted no-break space is fine"
    assert gate.check(GOOD.replace("The addendum", "José has the addendum; it"))[0], "precomposed accents are fine"


@pytest.mark.parametrize("tail", [SIG_TAIL, "\n> On Nov 4 Sam wrote:\n> price?\n", "\nP.S. one more thing.\n",
                                  "\nOwner, Brown Bison Holdings LLC\n"])
def test_text_after_closer_fails(tail):
    ok, probs = gate.check(GOOD + tail)
    assert not ok
    assert any("text after the 'Thanks <Name>,' closer" in p for p in probs), probs


def test_no_greeting_fails():
    ok, probs = gate.check("Can you price the chiller replacement by Friday, November 13?\n\nThanks Sam,\n")
    assert not ok and any(p.startswith("no greeting line") for p in probs), probs


@pytest.mark.parametrize("greeting, closer", [
    ("Hi Ms. Lopez,", "Thanks Lopez,"), ("Good morning Sgt. Ruiz,", "Thanks Ruiz,"),
    ("Hi Silas, Conor and the H2 Global estimating crew,", "Thanks Silas and Conor,"),
    ("Hi Silas, Conor and the H2 Global estimating crew,", "Thanks Team,"),
    ("Hey Sam,", "Thanks Sam,"), ("Morning Sam!", "Thanks Sam,"), ("Hello Team:", "Thanks Team,"),
])
def test_greeting_forms_that_pass(greeting, closer):
    ok, probs = gate.check(GOOD.replace("Hi Sam,", greeting).replace("Thanks Sam,", closer))
    assert ok, probs


@pytest.mark.parametrize("greeting", ["Dear Maria,", "Maria,", "Hi Sam, thanks for the photos.", "Subject: Chiller pricing", "Hi Sam"])
def test_greeting_forms_that_fail(greeting):
    ok, probs = gate.check(GOOD.replace("Hi Sam,", greeting))
    assert not ok and any(p.startswith("no greeting line") for p in probs), probs


def test_no_message_line_fails():
    ok, probs = gate.check("Hi Sam,\n\nThanks Sam,\n")
    assert not ok and any(p.startswith("no message line") for p in probs), probs


@pytest.mark.parametrize("closer", ["Thanks,", "Thanks Sam", "Best,", "Thanks Sam!", ""])
def test_missing_closer_fails(closer):
    ok, probs = gate.check(GOOD.replace("Thanks Sam,", closer))
    assert not ok and any(p.startswith("no 'Thanks <FirstName>,' closer") for p in probs), probs


@pytest.mark.parametrize("closer", ["thanks sam,", "thanks Sam,", "Thanks sam,", "Thanks Sam, Please, Wire, The, Deposit, Today,"])
def test_badly_shaped_closer_fails_with_a_specific_message(closer):
    ok, probs = gate.check(GOOD.replace("Thanks Sam,", closer))
    assert not ok and any(p.startswith("closer ") and "must read 'Thanks <FirstName>,'" in p for p in probs), probs


@pytest.mark.parametrize("closer", ["Thanks Bob,", "Thanks Sam, Wire, Today,", "Thanks Sam and Wire,"])
def test_closer_names_must_be_in_the_greeting(closer):
    ok, probs = gate.check(GOOD.replace("Thanks Sam,", closer))
    assert not ok and any("not in the greeting" in p for p in probs), probs


def test_group_mail_closers():
    assert gate.CLOSER.match("Thanks Team,") and gate.CLOSER.match("Thanks Sam and Alex,") and not gate.CLOSER.match("Thanks,")
    assert gate.check(GOOD.replace("Hi Sam,", "Hi Team,").replace("Thanks Sam,", "Thanks Team,"))[0]
    assert gate.check(GOOD.replace("Hi Sam,", "Hi Sam and Alex,").replace("Thanks Sam,", "Thanks Sam and Alex,"))[0]


def test_missing_hz_fails_closed(monkeypatch, tmp_path):
    monkeypatch.setattr(gate, "HZ_CANDIDATES", (tmp_path / "home" / "hz.py", tmp_path / "repo" / "hz.py"))
    assert gate.find_hz() is None
    ok, probs = gate.check(GOOD)
    assert not ok
    assert "not found" in probs[-1] and "restore it" in probs[-1], probs


def test_explicit_missing_hz_fails_closed(tmp_path):
    ok, probs = gate.check(GOOD, hz_py=tmp_path / "nope.py")
    assert not ok and "not found" in probs[-1]


@pytest.mark.parametrize("code", [
    "raise RuntimeError('boom')\n",                                   # crash
    "print('hello')\n",                                               # exit 0, no PASS line
    "import sys\nprint('PASS')\nsys.exit(2)\n",                       # PASS but an odd exit
    "import sys\nprint('ERROR L1: x')\nprint('PASS')\n",              # PASS printed next to an ERROR
    "import sys\nprint('FAIL')\nsys.exit(1)\n",                       # FAIL with no ERROR line
])
def test_hz_odd_results_fail_closed(tmp_path, code):
    ok, probs = gate.check(GOOD, hz_py=_fake_hz(tmp_path, code))
    assert not ok, probs


def test_hz_timeout_fails_closed(tmp_path, monkeypatch):
    monkeypatch.setattr(gate, "TIMEOUT", 1)
    ok, probs = gate.check(GOOD, hz_py=_fake_hz(tmp_path, "import time\ntime.sleep(30)\n"))
    assert not ok and "timed out" in probs[-1], probs


@pytest.mark.skipif(os.name != "posix", reason="process-group kill is POSIX")
def test_hz_timeout_kills_a_grandchild_holding_stdout(tmp_path, monkeypatch):
    monkeypatch.setattr(gate, "TIMEOUT", 1)
    hz = _fake_hz(tmp_path, "import subprocess, time\nsubprocess.Popen(['sleep', '30'])\ntime.sleep(30)\n")
    t0 = time.monotonic()
    ok, probs = gate.check(GOOD, hz_py=hz)
    assert not ok and "timed out" in probs[-1], probs
    assert time.monotonic() - t0 < 10, "the timeout waited for the grandchild's pipe"


def test_fake_pass_still_needs_structure(tmp_path):
    hz = _fake_hz(tmp_path, "print('PASS')\n")
    assert gate.check(GOOD, hz_py=hz)[0]
    assert not gate.check(GOOD + SIG_TAIL, hz_py=hz)[0], "a structure problem fails even when hz.py passes"


# ---------------------------------------------------------------------------------------------------------------- word budget
def test_label_wall_is_refused():
    """40 'Label: value' lines (783 words) pass hz.py with a warning; the gate refuses more than 12."""
    lines = [f"Item {i}: The crew will clean the hood ducts and the fans and haul the grease away by noon." for i in range(40)]
    body = "Hi Sam,\n\nThe walk is Tuesday at nine.\n\n" + "\n\n".join(lines) + "\n\nThanks Sam,\n"
    code, out = _hz_direct(gate.prose(body))
    assert code == 0 and "PASS with warnings" in out, out                 # what hz.py alone lets through
    ok, probs = gate.check(body)
    assert not ok and any("40 'Label: value' lines (at most 12)" in p for p in probs), probs
    twelve = "Hi Sam,\n\nThe walk is Tuesday at nine.\n\n" + "\n\n".join(lines[:12]) + "\n\nThanks Sam,\n"
    assert gate.check(twelve)[0], "12 short label lines are allowed (SKILL.md)"
    assert not gate.check(twelve.replace("Thanks Sam,", lines[12] + "\n\nThanks Sam,"))[0]


def test_greeting_shaped_lines_still_count():
    """'Hey ...' lines match hz.py's GREETING and drop out of its count; the gate counts every line after the first."""
    body = "Hi Sam,\n\n" + "\n\n".join(["Hey crew arrives at six sharp tomorrow"] * 30) + "\n\nThanks Sam,\n"
    code, out = _hz_direct(gate.prose(body))
    assert code == 0, out
    ok, probs = gate.check(body)
    assert not ok and any("210 words of prose (cap 150" in p for p in probs), probs     # 30 lines x 7 words


def test_target_overrun_passes_with_the_warning_shown(tmp_path):
    ok, probs, warns, n = gate.lint(MID)
    assert ok, probs
    assert any("prose words (target under 90" in w for w in warns), warns
    r = _cli(_body(tmp_path, MID))
    assert r.returncode == 0 and r.stdout.strip().splitlines()[-1] == "PASS with warnings", r.stdout
    assert "warn" in r.stdout and "target under 90" in r.stdout


def test_hz_hint_never_suggests_long():
    ok, probs = gate.check(LONG)
    assert not ok and not any("--long" in p for p in probs), probs


# ---------------------------------------------------------------------------------------------------------------- asks
@pytest.mark.parametrize("asks", [21, -1, 100, True, "2", 2.0])
def test_asks_bad_values_error(asks):
    ok, probs = gate.check(GOOD, asks=asks)
    assert not ok and "asks" in probs[0], probs


def test_asks_without_the_inbound_email_is_capped_at_one():
    assert gate.effective_asks(8) == (1, gate.effective_asks(8)[1]) and "capped at 1" in gate.effective_asks(8)[1]
    assert gate.effective_asks(None)[0] == 0 and gate.effective_asks(1)[0] == 1
    long330 = "Hi Sam,\n\n" + "\n\n".join([_PARA] * 11) + "\n\nThanks Sam,\n"        # 341 prose words
    ok, probs = gate.check(long330, asks=8)
    assert not ok and any("capped at 1" in p for p in probs), probs
    ok, probs = gate.check(LONG, asks=5)
    assert not ok, "asks 5 with no inbound email must not lift the cap"


def test_asks_with_the_inbound_email():
    assert gate.asks_in(INBOUND5) == 5
    assert gate.asks_in("Can you price it?\n> On Tue Sam wrote:\n> what? why? when?\nhttps://x.example/a?b=c\n") == 1
    assert gate.effective_asks(None, INBOUND5)[0] == 5
    assert gate.effective_asks(8, INBOUND5)[0] == 5, "min(declared, counted)"
    assert gate.effective_asks(2, INBOUND5)[0] == 2
    assert gate.check(LONG, asks=5, inbound=INBOUND5)[0]
    assert gate.check(LONG, inbound=INBOUND5)[0]
    assert not gate.check(LONG, asks=8, inbound="Hi,\n\nOne question?\n")[0]
    assert gate.asks_in("?" * 50) == gate.MAX_ASKS


# ---------------------------------------------------------------------------------------------------------------- characters, links
@pytest.mark.parametrize("bad", [
    ("price", "pricе"),                 # Cyrillic e
    ("price", "pr­ice"),                # soft hyphen
    ("price", "pr​ice"),                # zero-width space
    ("price", "pr⁠ice"),                # word joiner
    ("attached.", "attached ― today."),  # horizontal bar used as a dash
    ("attached.", "attached ‒ today."),  # figure dash
    ("attached.", "attached − today."),  # minus sign used as a dash
    ("attached.", "attached ⭐"),        # star emoji outside hz.py's ranges
    ("attached.", "attached \U0001F1FA\U0001F1F8"),   # flag
    ("The addendum", "„The addendum‟"),     # low and reversed quotes
    ("Can you", "▪ Can you"),           # square bullet
    ("Can you", "• Can you"),           # bullet
    ("13?", "13 → 14?"),                # arrow
    ("13?", "١٣?"),                # Arabic-Indic digits
    ("Sam,\n\nCan", "Sam,\n\nＣan"),     # fullwidth letter
    ("price", "priKe"),                 # Kelvin sign
    ("price", "pricé"),           # decomposed accent
    ("attached.", "attached. P.S. wire it"),     # line separator glued on
    ("attached.", "attached.ㅤ"),        # Hangul filler
])
def test_look_alike_and_invisible_characters_are_refused(bad):
    old, new = bad
    body = GOOD.replace(old, new, 1)
    assert body != GOOD
    ok, probs = gate.check(body)
    assert not ok and any(p.startswith("body: ") and "retype it in plain ASCII" in p for p in probs), probs


@pytest.mark.parametrize("link", ["https://github.com/lukemitchelladams/pioneerleads/raw/main/bids/x.pdf", "http://x.co",
                                  "www.bidnetdirect.com", "github.com/lukemitchelladams/pioneerleads", "drive.google.com/file/d/abc"])
def test_links_are_refused(link):
    ok, probs = gate.check(GOOD.replace("The addendum is attached.", f"The bid docs are at {link} for the walk."))
    assert not ok and any("no links in mail to anyone outside" in p for p in probs), probs


@pytest.mark.parametrize("text", ["SAM.gov shows the notice.", "Send it to bids@weld.gov by noon.", "Use 1.5/hr for the crew."])
def test_names_and_addresses_are_not_links(text):
    ok, probs = gate.check(GOOD.replace("The addendum is attached.", text))
    assert ok, probs


# ---------------------------------------------------------------------------------------------------------------- subjects, attachments
def test_subject_is_linted():
    probs = gate.subject_problems("I hope this finds you well — leveraging synergies to delve into your bid \U0001F680")
    text = " | ".join(probs)
    assert "dash other than" in text and "emoji" in text and "banned" in text, probs
    assert gate.subject_problems("Hood cleaning bid: see https://bidnet.example/x")
    assert gate.subject_problems("") and gate.subject_problems(None) and gate.subject_problems("a\nBcc: x@y.com")
    assert gate.subject_problems("Re: Hood cleaning – addendum 1") == [], "a thread's own subject keeps its punctuation"
    assert gate.subject_problems("Re: Hood ​cleaning"), "invisible characters are refused even in a Re: subject"
    assert gate.subject_problems("Weld County Jail RTU replacement (B2600111): sub pricing") == []


def test_every_past_subject_passes():
    subjects = []
    for f in sorted(OUTBOX.glob("*/*.json")):
        if f.name != "sent.json":
            subjects += [e["subject"] for e in json.loads(f.read_text(encoding="utf-8"))]
    assert subjects
    bad = [(s, gate.subject_problems(s)) for s in subjects if gate.subject_problems(s)]
    assert not bad, bad


def test_text_attachments_are_refused():
    assert gate.attachment_problems(["bids/x/cover-letter.txt"])
    assert gate.attachment_problems(["note.HTML", "a.pdf"])
    assert gate.attachment_problems([("notes", "text/plain")]) and gate.attachment_problems([("fwd.eml", None)])
    assert gate.attachment_problems([("x", "message/rfc822")])
    assert gate.attachment_problems(["Bid Specs.docx", "Attachment 1.pdf", "Pricing.xlsx", "rates.csv", "site.jpg"]) == []


# ---------------------------------------------------------------------------------------------------------------- recipients
@pytest.mark.parametrize("rcpts", [["luke@brownbisonco.com"], ["LUKE@BrownBisonCo.com"], ["lukemitchelladams@gmail.com"],
                                   ["lukemitchelladams@gmail.com", "luke@brownbisonco.com"], [" luke@brownbisonco.com "],
                                   "luke@brownbisonco.com"])
def test_owner_only_true(rcpts):
    assert gate.owner_only(rcpts)


@pytest.mark.parametrize("rcpts", [
    [], None, [None], [""],
    ["sam@example.com"],
    ["luke@brownbisonco.com", "sam@example.com"],                   # mixed owner + outsider
    ["Luke Adams <luke@brownbisonco.com>"],                         # display names are not bare addresses
    ["sam@example.com <luke@brownbisonco.com>"],
    ['"luke@brownbisonco.com" <sam@example.com>'],
    ["luke@brownbisonco.com, sam@example.com"],                     # comma smuggling
    ["luke@brownbisonco.com;sam@example.com"],                      # semicolon smuggling
    ["luke@brownbisonco.com\nBcc: sam@example.com"],                # header injection
    ["luke@brownbisonco.com\n"],                                    # a newline is not stripped here
    ["luKe@brownbisonco.com"],                                 # Kelvin sign lower()s to 'k'
    ["luke@brownbisonco.com.example.com"], ["luke@brownbisonco.com."], ["xluke@brownbisonco.com"],
    ["contact@brownbisonco.com"],                                   # a company inbox, not Luke
])
def test_owner_only_false(rcpts):
    assert not gate.owner_only(rcpts)


# ---------------------------------------------------------------------------------------------------------------- CLI
def _cli(*args):
    return subprocess.run([sys.executable, str(SCRIPTS / "humanize_gate.py"), "check", *args], capture_output=True, text=True,
                          timeout=60)


def test_cli_pass_and_fail(tmp_path):
    r = _cli(_body(tmp_path, GOOD))
    assert r.returncode == 0 and r.stdout.strip().splitlines()[-1] == "PASS", r.stdout + r.stderr
    r = _cli(str(WELD))
    lines = r.stdout.strip().splitlines()
    assert r.returncode == 1 and lines[-1] == "FAIL" and any("greeting 'Hi,'" in x for x in lines), r.stdout
    r = _cli(_body(tmp_path, LONG), "--asks", "5")
    assert r.returncode == 1 and "capped at 1" in r.stdout, r.stdout
    r = _cli(_body(tmp_path, LONG), "--asks", "5", "--asks-from", _body(tmp_path, INBOUND5, "inbound.txt"))
    assert r.returncode == 0 and "asks used: 5" in r.stdout, r.stdout
    r = _cli(_body(tmp_path, GOOD), "--asks", "21")
    assert r.returncode == 1 and "outside 0..20" in r.stdout, r.stdout
    r = _cli(_body(tmp_path, GOOD), "--asks", "٨")
    assert r.returncode == 2 and "not a whole number" in r.stderr, r.stderr
    r = _cli(_body(tmp_path, GOOD), "--subject", "Chiller — pricing")
    assert r.returncode == 1 and "subject: dash" in r.stdout, r.stdout
    r = _cli(_body(tmp_path, GOOD_MCP), "--signature")
    assert r.returncode == 0, r.stdout


# ---------------------------------------------------------------------------------------------------------------- gmail_api send
def test_signature_is_operations_manager(gm):
    assert "Operations Manager" in gm.SIGNATURE
    for bad in ("Owner", "CEO", "General Manager", "Sales Manager"):
        assert bad not in gm.SIGNATURE
    assert gm.SIGNATURE.startswith("\n\n") and gm.SIGNATURE.endswith("\n")
    assert gm.SIGNATURE.strip("\n").split("\n") == list(gate.SIGNATURE_LINES) == ["Luke Adams", "Operations Manager",
                                                                                   "Brown Bison Holdings LLC", "(720) 275-1554",
                                                                                   "luke@brownbisonco.com"]
    assert "Owner, Brown Bison" not in (SCRIPTS / "gmail_api.py").read_text(encoding="utf-8")
    assert gm.MAX_ASKS == gate.MAX_ASKS


@pytest.mark.skipif(not BRAND.is_file(), reason="brown-bison-gov/data/brand.py is not on this machine (cloud container)")
def test_signature_matches_brand_py(gm):
    brand = _load("test_bb_brand", BRAND)
    assert gm.SIGNATURE.strip("\n") == brand.SIGNATURE == "\n".join(gate.SIGNATURE_LINES)


def test_send_refuses_weld_before_any_network_call(gm, monkeypatch, capsys):
    err = _refused(gm, monkeypatch, capsys, "--to", "bids@weld.gov", "--subject", "Jail RTU", "--body-file", str(WELD))
    assert "greeting 'Hi,' has no name" in err


def test_send_refuses_before_reading_attachments(gm, monkeypatch, capsys, tmp_path):
    _refused(gm, monkeypatch, capsys, "--to", "bids@weld.gov", "--subject", "x", "--body-file", str(WELD), "--",
             str(tmp_path / "missing.pdf"))


def test_no_signature_is_refused_for_outside_mail(gm, monkeypatch, capsys, tmp_path):
    err = _refused(gm, monkeypatch, capsys, "--no-signature", "--to", "sam@example.com", "--subject", "Chiller", "--body-file",
                   _body(tmp_path, GOOD))
    assert "--no-signature is only for mail to Luke's own addresses" in err
    with pytest.raises(NetworkTouched):                  # to Luke alone it is allowed
        _send(gm, monkeypatch, "--no-signature", "--to", "luke@brownbisonco.com", "--subject", "x", "--body-file", str(WELD))


def test_subject_is_refused_through_send(gm, monkeypatch, capsys, tmp_path):
    err = _refused(gm, monkeypatch, capsys, "--to", "sam@example.com", "--subject",
                   "I hope this finds you well — leveraging synergies \U0001F680", "--body-file", _body(tmp_path, GOOD))
    assert "subject: " in err


def test_text_attachment_is_refused_through_send(gm, monkeypatch, capsys, tmp_path):
    cover = tmp_path / "cover-letter.txt"
    cover.write_text("I hope this finds you well! I wanted to reach out — we are thrilled to leverage synergies.\n")
    err = _refused(gm, monkeypatch, capsys, "--to", "sam@example.com", "--subject", "Chiller", "--body-file", _body(tmp_path, GOOD),
                   "--", str(cover))
    assert "attachment cover-letter.txt" in err


@pytest.mark.parametrize("flags", [
    ["--to", "luke@brownbisonco.com", "--bcc", "bids@weld.gov"],
    ["--to", "luke@brownbisonco.com", "--cc", "sam@example.com"],
    ["--to", "Luke Adams <luke@brownbisonco.com>"],
    ["--bcc", "luke@brownbisonco.com, sam@example.com"],
    ["--to", "luKe@brownbisonco.com"],
])
def test_mixed_or_disguised_recipients_are_linted(gm, monkeypatch, capsys, flags):
    _refused(gm, monkeypatch, capsys, *flags, "--subject", "x", "--body-file", str(WELD))


def test_recipient_with_a_line_break_is_refused(gm, monkeypatch, capsys, tmp_path):
    err = _refused(gm, monkeypatch, capsys, "--to", "luke@brownbisonco.com\nBcc: sam@example.com", "--subject", "x",
                   "--body-file", _body(tmp_path, GOOD))
    assert "line break or control character" in err


def test_text_after_closer_is_refused(gm, monkeypatch, capsys, tmp_path):
    err = _refused(gm, monkeypatch, capsys, "--to", "sam@example.com", "--subject", "x",
                   "--body-file", _body(tmp_path, GOOD + SIG_TAIL))
    assert "text after the 'Thanks <Name>,' closer" in err


@pytest.mark.parametrize("to", ["luke@brownbisonco.com", "LukeMitchellAdams@gmail.com", "luke@brownbisonco.com\n"])
def test_owner_only_mail_is_exempt(gm, monkeypatch, to):
    with pytest.raises(NetworkTouched):                 # reached the (stubbed) token step: the gate let it through
        _send(gm, monkeypatch, "--to", to, "--subject", "note to self", "--body-file", str(WELD))
    assert len(gm.touched) == 1


def _capture_send(gm, monkeypatch):
    posted = []
    monkeypatch.setattr(gm, "access_token", lambda: "fake-token")

    def fake_call(method, path, token, body=None, ctype="application/json"):
        posted.append((method, path, body))
        return {"id": "fake-id", "threadId": "fake-thread"}
    monkeypatch.setattr(gm, "call", fake_call)
    return posted


def test_passing_body_goes_out_with_the_operations_manager_signature(gm, monkeypatch, tmp_path, capsys):
    posted = _capture_send(gm, monkeypatch)
    _send(gm, monkeypatch, "--to", " sam@example.com ", "--subject", "Chiller", "--body-file", _body(tmp_path, GOOD), "--asks", "2")
    out = json.loads(capsys.readouterr().out)
    assert out["id"] == "fake-id" and out["to"] == ["sam@example.com"] and out["asks"] == 1
    (method, path, payload), = posted
    assert (method, path) == ("POST", "/gmail/v1/users/me/messages/send")
    msg = email.message_from_bytes(base64.urlsafe_b64decode(json.loads(payload)["raw"]), policy=policy.default)
    assert msg["To"] == "sam@example.com"
    assert msg.get_content().replace("\r\n", "\n") == GOOD.rstrip() + gm.SIGNATURE
    assert "Owner" not in msg.get_content()


@pytest.mark.parametrize("asks", ["21", "-1", "two", "2.5", "٨", "+8"])
def test_send_asks_bad_values_error(gm, monkeypatch, capsys, asks):
    with pytest.raises(SystemExit) as ei:
        _send(gm, monkeypatch, "--to", "sam@example.com", "--subject", "x", "--body-file", str(DAY / PASSING_1105[0]),
              "--asks", asks)
    assert ei.value.code == 2 and "--asks" in capsys.readouterr().err
    assert gm.touched == []


def test_send_asks_needs_the_inbound_email(gm, monkeypatch, capsys, tmp_path):
    body = _body(tmp_path, LONG)
    err = _refused(gm, monkeypatch, capsys, "--to", "sam@example.com", "--subject", "x", "--body-file", body)
    assert "words of prose" in err
    err = _refused(gm, monkeypatch, capsys, "--to", "sam@example.com", "--subject", "x", "--body-file", body, "--asks", "8")
    assert "capped at 1" in err
    posted = _capture_send(gm, monkeypatch)
    inbound = _body(tmp_path, INBOUND5, "inbound.txt")
    _send(gm, monkeypatch, "--to", "sam@example.com", "--subject", "x", "--body-file", body, "--asks", "8", "--asks-from", inbound)
    rec = json.loads(capsys.readouterr().out)
    assert len(posted) == 1 and rec["asks"] == 5 and rec["asks_from"] == inbound


def test_send_refuses_an_unreadable_asks_from(gm, monkeypatch, capsys, tmp_path):
    err = _refused(gm, monkeypatch, capsys, "--to", "sam@example.com", "--subject", "x", "--body-file", _body(tmp_path, GOOD),
                   "--asks-from", str(tmp_path / "nope.txt"))
    assert "cannot read --asks-from" in err


def test_send_refuses_when_the_gate_cannot_load(gm, monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(gm, "GATE_FILE", tmp_path / "humanize_gate.py")
    err = _refused(gm, monkeypatch, capsys, "--to", "sam@example.com", "--subject", "x", "--body-file", _body(tmp_path, GOOD))
    assert "could not run" in err


def test_send_refuses_when_hz_is_missing(gm, monkeypatch, capsys, tmp_path):
    g2 = _load("test_pl_humanize_gate_nohz", SCRIPTS / "humanize_gate.py")
    g2.HZ_CANDIDATES = (tmp_path / "a" / "hz.py", tmp_path / "b" / "hz.py")
    monkeypatch.setattr(gm, "_gate", lambda: g2)
    err = _refused(gm, monkeypatch, capsys, "--to", "sam@example.com", "--subject", "x", "--body-file", _body(tmp_path, GOOD))
    assert "not found" in err and "restore it" in err


@pytest.mark.parametrize("path", ["/gmail/v1/users/me/messages/send", "/gmail/v1/users/me/drafts/send",
                                  "/upload/gmail/v1/users/me/messages/send?uploadType=media"])
def test_call_refuses_an_unarmed_send(path):
    g = _load("test_pl_gmail_api_call", SCRIPTS / "gmail_api.py")      # the real call(); urlopen raises (autouse fixture)
    with pytest.raises(SystemExit) as ei:
        g.call("POST", path, "tok", json.dumps({"raw": "x"}).encode())
    assert "HUMANIZE: refused POST" in str(ei.value.code)
    with pytest.raises(NetworkTouched):                                  # other calls are not affected
        g.call("GET", "/gmail/v1/users/me/profile", "tok")


def test_send_arms_exactly_its_own_payload_once(monkeypatch, tmp_path, capsys):
    g = _load("test_pl_gmail_api_armed", SCRIPTS / "gmail_api.py")
    monkeypatch.setattr(g, "access_token", lambda: "fake-token")
    seen = []

    def fake_urlopen(req, timeout=None):
        seen.append(req)
        return io.BytesIO(b'{"id": "fake-id", "threadId": "t"}')
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    _send(g, monkeypatch, "--to", "sam@example.com", "--subject", "Chiller", "--body-file", _body(tmp_path, GOOD))
    assert json.loads(capsys.readouterr().out)["id"] == "fake-id"
    (req,) = seen
    assert req.full_url.endswith("/gmail/v1/users/me/messages/send")
    with pytest.raises(SystemExit):                                      # the same payload cannot be replayed through call()
        g.call("POST", "/gmail/v1/users/me/messages/send", "tok", req.data)


# ---------------------------------------------------------------------------------------------------------------- MCP hook
def _hook(tool, ti):
    return gate.hook_decision(json.dumps({"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": ti}))


def _denied(out):
    return (out or {}).get("hookSpecificOutput", {}).get("permissionDecision") == "deny"


def test_settings_gate_the_mcp_mail_tools():
    s = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    entries = [e for e in s["hooks"]["PreToolUse"] if "humanize_gate.py" in json.dumps(e)]
    assert entries, "no PreToolUse entry runs scripts/humanize_gate.py hook"
    rx = [re.compile(e["matcher"]) for e in entries]
    for name in ("mcp__Gmail__send_message", "mcp__Gmail__reply", "mcp__Gmail__forward", "mcp__claude_ai_Gmail__send_message",
                 "mcp__910c93d7-015e-4b6a-959a-1621638f94ec__reply", "mcp__Gmail__send_draft"):
        assert any(r.search(name) for r in rx), name
    for name in ("mcp__Gmail__get_thread", "mcp__Gmail__create_draft", "Bash", "mcp__Gmail__search_threads"):
        assert not any(r.search(name) for r in rx), name
    cmds = [h["command"] for e in entries for h in e["hooks"]]
    assert all(c.endswith("|| exit 2") and " hook" in c for c in cmds), cmds


def test_hook_command_denies_and_fails_closed(tmp_path):
    """The exact settings command, run by bash: a bad send prints the deny JSON; a missing or broken gate exits 2 (blocks)."""
    s = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    (cmd,) = [h["command"] for e in s["hooks"]["PreToolUse"] for h in e["hooks"] if "humanize_gate.py" in h["command"]]
    payload = json.dumps({"hook_event_name": "PreToolUse", "tool_name": "mcp__Gmail__send_message",
                          "tool_input": {"to": ["sam@example.com"], "subject": "Bid",
                                         "body": "Hi,\n\nI hope this finds you well — I wanted to reach out.\n\nThanks,"}})
    env = {k: v for k, v in os.environ.items() if k not in GMAIL_VARS}

    def run(project):
        return subprocess.run(["bash", "-c", cmd], input=payload, capture_output=True, text=True, timeout=120,
                              env={**env, "CLAUDE_PROJECT_DIR": str(project)})
    r = run(ROOT)
    assert r.returncode == 0 and _denied(json.loads(r.stdout)), r.stdout + r.stderr
    assert run(tmp_path).returncode == 2, "a missing gate must block"
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "humanize_gate.py").write_text("this is not python(\n")
    assert run(tmp_path).returncode == 2, "a broken gate must block"
    ok = json.dumps({"hook_event_name": "PreToolUse", "tool_name": "mcp__Gmail__send_message",
                     "tool_input": {"to": ["sam@example.com"], "subject": "Chiller replacement: pricing", "body": GOOD_MCP}})
    r = subprocess.run(["bash", "-c", cmd], input=ok, capture_output=True, text=True, timeout=120,
                       env={**env, "CLAUDE_PROJECT_DIR": str(ROOT)})
    assert r.returncode == 0 and r.stdout.strip() == "", r.stdout + r.stderr


def test_hook_send_message():
    tool = "mcp__Gmail__send_message"
    bad = {"to": ["sam@example.com"], "subject": "Bid", "body": "Hi,\n\nI hope this finds you well — I wanted to reach out.\n\nThanks,"}
    out = _hook(tool, bad)
    assert _denied(out) and "not humanized" in out["hookSpecificOutput"]["permissionDecisionReason"], out
    good = {"to": ["sam@example.com"], "subject": "Chiller replacement: pricing", "body": GOOD_MCP}
    assert _hook(tool, good) is None
    assert _denied(_hook(tool, {**good, "body": GOOD})), "the connector appends nothing: the signature must be in the body"
    assert _denied(_hook(tool, {**good, "body": GOOD_MCP.replace("Operations Manager", "Owner")}))
    assert _denied(_hook(tool, {**good, "subject": "Chiller — pricing"}))
    assert _denied(_hook(tool, {**good, "subject": ""}))
    assert _hook(tool, {**good, "subject": "Re: Chiller – pricing", "replyThreadId": "T1"}) is None
    assert _denied(_hook(tool, {**good, "includeSignature": True}))
    assert _denied(_hook(tool, {**good, "htmlBody": "<p>Hi Sam</p>"}))
    assert _denied(_hook(tool, {**good, "draftId": "d1"}))
    assert _denied(_hook(tool, {**good, "attachments": [{"filename": "cover.txt", "mimeType": "text/plain", "content": "eA=="}]}))
    assert _hook(tool, {**good, "attachments": [{"filename": "specs.pdf", "mimeType": "application/pdf", "content": "eA=="}]}) is None
    assert _denied(_hook(tool, {**good, "body": GOOD_MCP.replace("The addendum is attached.", "See https://github.com/x/y.")}))
    assert _denied(_hook(tool, {**good, "to": ["luke@brownbisonco.com", "sam@example.com"], "body": "board update"}))


def test_hook_owner_only_board_update_is_left_alone():
    assert _hook("mcp__Gmail__send_message", {"to": ["luke@brownbisonco.com"], "subject": "BROWN BISON 11/05 PM",
                                              "body": "1. #1 TODAY: x\n2. DUE: y"}) is None
    assert _hook("mcp__Gmail__reply", {"messageId": "m1", "to": ["luke@brownbisonco.com"], "body": "ok"}) is None


def test_hook_reply_and_forward():
    assert _denied(_hook("mcp__Gmail__reply", {"messageId": "m1", "body": "Hi,\n\nSure thing!\n\nThanks,"}))
    assert _denied(_hook("mcp__Gmail__reply", {"messageId": "m1", "to": ["luke@brownbisonco.com"], "replyAll": True, "body": "ok"}))
    assert _hook("mcp__Gmail__reply", {"messageId": "m1", "body": GOOD_MCP}) is None
    assert _denied(_hook("mcp__Gmail__forward", {"messageId": "m1", "to": ["sam@example.com"]})), "a forward needs a note"
    assert _hook("mcp__Gmail__forward", {"messageId": "m1", "to": ["sam@example.com"], "forwardText": GOOD_MCP}) is None
    assert _denied(_hook("mcp__Gmail__forward", {"messageId": "m1", "to": ["sam@example.com"], "forwardText": GOOD}))
    assert _denied(_hook("mcp__Gmail__send_draft", {"draftId": "d1"}))
    assert _denied(_hook("mcp__910c93d7-015e-4b6a-959a-1621638f94ec__send_message",
                         {"to": ["sam@example.com"], "subject": "x", "body": "Hi,\n\nHey!\n\nThanks,"}))


def test_hook_leaves_other_tools_alone_and_fails_closed():
    assert _hook("mcp__Slack__send_message", {"channel_id": "C1", "message": "Hi,"}) is None
    assert _hook("mcp__ccd_session__send_message", {"to": ["sam@example.com"], "body": "x"}) is None
    assert _hook("Bash", {"command": "ls"}) is None
    assert _denied(_hook("mcp__Gmail__send_message", "not an object"))
    assert _denied(gate.hook_decision('{"tool_name": "mcp__Gmail__send_message", "tool_input": {'))
    assert _denied(gate.hook_decision("garbage"))


def test_hook_cli_prints_the_deny_json():
    payload = json.dumps({"hook_event_name": "PreToolUse", "tool_name": "mcp__Gmail__reply",
                          "tool_input": {"messageId": "m1", "body": "Hi,\n\nSure thing!\n\nThanks,"}})
    r = subprocess.run([sys.executable, "-I", str(SCRIPTS / "humanize_gate.py"), "hook"], input=payload, capture_output=True,
                       text=True, timeout=60)
    assert r.returncode == 0 and _denied(json.loads(r.stdout)), r.stdout + r.stderr


# ---------------------------------------------------------------------------------------------------------------- send_outbox
def test_send_outbox_import_sends_nothing(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("send_outbox ran a command at import")
    monkeypatch.setattr(subprocess, "run", boom)
    so = _load("test_pl_send_outbox_import", SCRIPTS / "send_outbox.py")
    assert callable(so.main)


def _fake_runner(calls, kws):
    def fake_run(cmd, **kw):
        calls.append(cmd)
        kws.append(kw)
        if any(x.endswith("bad.txt") for x in cmd):
            return subprocess.CompletedProcess(cmd, 3, "", "HUMANIZE: ERROR L1: greeting 'Hi,' has no name. Write it with "
                                                           "/humanize (hz.py lint to PASS) and resend.\n")
        if any(x.endswith("broken.txt") for x in cmd):
            return subprocess.CompletedProcess(cmd, 1, "", "Gmail API 500 on POST /gmail/v1/users/me/messages/send\n")
        return subprocess.CompletedProcess(cmd, 0, json.dumps({"id": "fake-1", "threadId": "t"}) + "\n", "")
    return fake_run


def test_send_outbox_does_not_record_a_refused_entry_and_exits_nonzero(monkeypatch, tmp_path, capsys):
    so = _load("test_pl_send_outbox", SCRIPTS / "send_outbox.py")
    monkeypatch.chdir(tmp_path)
    (tmp_path / "specs.pdf").write_bytes(b"%PDF-1.4\n")
    manifest = tmp_path / "outbox.json"
    manifest.write_text(json.dumps([
        {"key": "good", "subject": "s", "to": ["sam@example.com"], "body_file": "good.txt", "files": ["specs.pdf"], "asks": 2,
         "asks_from": "inbound.txt", "thread": "T1"},
        {"key": "bad", "subject": "s", "to": ["bids@weld.gov"], "body_file": "bad.txt", "files": []},
        {"key": "broken", "subject": "s", "to": ["ann@example.com"], "body_file": "broken.txt", "files": []},
    ]))
    calls, kws = [], []
    monkeypatch.setattr(so.subprocess, "run", _fake_runner(calls, kws))
    assert so.main([str(manifest)]) == 3
    out = capsys.readouterr().out
    assert "REFUSED bad: HUMANIZE:" in out and "FAILED broken:" in out and "sent good: fake-1" in out, out
    assert "outbox: 1 sent, 0 skipped, 1 refused, 1 failed" in out, out
    assert set(json.loads((tmp_path / "sent.json").read_text())) == {"good"}
    good_cmd, bad_cmd, _ = calls
    assert good_cmd[1] == str(SCRIPTS / "gmail_api.py") and kws[0]["cwd"] == str(ROOT), "the sender beside send_outbox, run from the repo"
    assert good_cmd[good_cmd.index("--asks") + 1] == "2"
    assert good_cmd[good_cmd.index("--asks-from") + 1] == str(tmp_path / "inbound.txt")
    assert good_cmd[good_cmd.index("--body-file") + 1] == str(tmp_path / "good.txt")
    sep = good_cmd.index("--")
    assert good_cmd[sep + 1:] == [str(tmp_path / "specs.pdf")] and good_cmd.index("--to") < sep
    assert "--asks" not in bad_cmd and bad_cmd[-1] == "--"
    calls.clear()                                   # a rerun skips the sent entry and tries the refused one again
    assert so.main([str(manifest)]) == 3
    assert len(calls) == 2 and not any(any(x.endswith("good.txt") for x in c) for c in calls)


def test_send_outbox_ignores_a_sender_in_the_working_directory(monkeypatch, tmp_path, capsys):
    so = _load("test_pl_send_outbox_cwd", SCRIPTS / "send_outbox.py")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "gmail_api.py").write_text("print('ungated stub')\n")
    monkeypatch.chdir(tmp_path)
    (tmp_path / "outbox.json").write_text(json.dumps([{"key": "a", "subject": "s", "to": ["sam@example.com"],
                                                       "body_file": "good.txt", "files": []}]))
    calls, kws = [], []
    monkeypatch.setattr(so.subprocess, "run", _fake_runner(calls, kws))
    assert so.main(["outbox.json"]) == 0
    assert calls[0][1] == str(SCRIPTS / "gmail_api.py") != str(tmp_path / "scripts" / "gmail_api.py")


@pytest.mark.parametrize("entry, why", [
    ({"asks": "8"}, "'asks' must be a whole number"),
    ({"asks": True}, "'asks' must be a whole number"),
    ({"files": ["--asks", "8"]}, "starting with '-'"),
    ({"files": ["--no-signature"]}, "starting with '-'"),
    ({"cc": ["--bcc", "x@example.com"]}, "starting with '-'"),
    ({"to": "sam@example.com"}, "'to' must be a list"),
    ({"to": [], "bcc": []}, "needs 'to' or 'bcc'"),
    ({"files": ["missing.pdf"]}, "is not a file"),
    ({"subject": "--no-signature"}, "'subject' starts with '-'"),
    ({"thread": 5}, "'thread' must be a string"),
])
def test_send_outbox_rejects_malformed_entries(monkeypatch, tmp_path, capsys, entry, why):
    so = _load("test_pl_send_outbox_bad", SCRIPTS / "send_outbox.py")
    monkeypatch.chdir(tmp_path)
    base = {"key": "k", "subject": "s", "to": ["sam@example.com"], "body_file": "good.txt", "files": []}
    (tmp_path / "outbox.json").write_text(json.dumps([{**base, **entry}]))
    calls, kws = [], []
    monkeypatch.setattr(so.subprocess, "run", _fake_runner(calls, kws))
    assert so.main(["outbox.json"]) == 1
    out = capsys.readouterr().out
    assert "FAILED k: bad manifest entry" in out and why in out, out
    assert calls == [] and not (tmp_path / "sent.json").exists()


_SHIM = r'''
import importlib.util, json, os, socket, sys, urllib.request
def boom(*a, **k):
    raise SystemExit("TEST SHIM: network touched")
urllib.request.urlopen = boom
socket.socket.connect = boom
socket.create_connection = boom
spec = importlib.util.spec_from_file_location("gmail_api_real", os.environ["PL_REAL_GMAIL_API"])
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
g._env = boom
g._env_file = boom
g.access_token = lambda: "fake-token"
def fake_call(method, path, token, body=None, ctype="application/json"):
    with open(os.environ["PL_CALL_LOG"], "a") as fh:
        fh.write(json.dumps({"method": method, "path": path}) + "\n")
    return {"id": "fake-" + os.path.basename(sys.argv[sys.argv.index("--body-file") + 1]), "threadId": "fake-thread"}
g.call = fake_call
g.main()
'''


def test_send_outbox_end_to_end_with_the_real_gate(tmp_path):
    """(a copy of) send_outbox.py -> its sibling shim -> the real gmail_api.py, gate and hz.py, with the token/API calls stubbed."""
    (tmp_path / "scripts").mkdir()
    shutil.copy(SCRIPTS / "send_outbox.py", tmp_path / "scripts" / "send_outbox.py")
    (tmp_path / "scripts" / "gmail_api.py").write_text(_SHIM, encoding="utf-8")
    (tmp_path / "good.txt").write_text(GOOD, encoding="utf-8")
    (tmp_path / "bad.txt").write_text(WELD.read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "tail.txt").write_text(GOOD + SIG_TAIL, encoding="utf-8")
    (tmp_path / "long.txt").write_text(LONG, encoding="utf-8")
    (tmp_path / "inbound.txt").write_text(INBOUND5, encoding="utf-8")
    (tmp_path / "outbox.json").write_text(json.dumps([
        {"key": "good", "subject": "s", "to": ["sam@example.com"], "body_file": "good.txt", "files": []},
        {"key": "bad", "subject": "s", "to": ["bids@example.gov"], "body_file": "bad.txt", "files": []},
        {"key": "tail", "subject": "s", "bcc": ["a@example.com", "b@example.com"], "body_file": "tail.txt", "files": []},
        {"key": "long-bare", "subject": "s", "to": ["sam@example.com"], "body_file": "long.txt", "files": [], "asks": 5},
        {"key": "long-asks", "subject": "s", "to": ["sam@example.com"], "body_file": "long.txt", "files": [], "asks": 5,
         "asks_from": "inbound.txt"},
        {"key": "self", "subject": "s", "to": ["luke@brownbisonco.com"], "body_file": "bad.txt", "files": []},
    ]))
    env = {k: v for k, v in os.environ.items() if k not in GMAIL_VARS}
    env.update(HOME=str(tmp_path / "home"), PL_REAL_GMAIL_API=str(SCRIPTS / "gmail_api.py"),
               PL_CALL_LOG=str(tmp_path / "calls.jsonl"))
    r = subprocess.run([sys.executable, str(tmp_path / "scripts" / "send_outbox.py"), "outbox.json"], cwd=tmp_path, env=env,
                       capture_output=True, text=True, timeout=180)
    assert r.returncode == 3, r.stdout + r.stderr
    out = r.stdout
    assert "sent good: fake-good.txt" in out and "sent long-asks: fake-long.txt" in out and "sent self: fake-bad.txt" in out, out
    assert "REFUSED bad: HUMANIZE:" in out and "REFUSED tail: HUMANIZE:" in out and "REFUSED long-bare: HUMANIZE:" in out, out
    sent = json.loads((tmp_path / "sent.json").read_text())
    assert set(sent) == {"good", "long-asks", "self"} and sent["long-asks"]["asks"] == 5
    calls = [json.loads(x) for x in (tmp_path / "calls.jsonl").read_text().splitlines()]
    assert len(calls) == 3 and all(c["path"] == "/gmail/v1/users/me/messages/send" for c in calls)


# ---------------------------------------------------------------------------------------------------------------- corpus
def test_corpus_report(capsys):
    """Every past cloud body through check() (asks 0). Reports the list; the known 11/05 Weld FAIL must be caught."""
    bodies = sorted(OUTBOX.glob("*/*.txt"))
    results = [(p, gate.check(p.read_text(encoding="utf-8"))) for p in bodies]
    failed = [(p, probs) for p, (ok, probs) in results if not ok]
    with capsys.disabled():
        print(f"\n[corpus] {len(bodies)} bodies under ops/outbox/*/: {len(bodies) - len(failed)} PASS, {len(failed)} FAIL (asks 0)")
        for p, probs in failed:
            print(f"[corpus] FAIL {p.relative_to(ROOT)}: {' | '.join(probs)[:160]}")
    assert bodies
    assert WELD in [p for p, _ in failed]
