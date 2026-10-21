#!/usr/bin/env python3
"""hz.py - helper for the /humanize skill. Stdlib only.

  python hz.py lint FILE [--asks N] [--long] [--chat]
                                            mechanical check of a draft; exit 1 on any ERROR.
                                            --asks = questions in the incoming email (word budget scales)
                                            --chat = Teams one-liner: no "Thanks <FirstName>," closer required
  python hz.py log FILE                     copy a delivered draft into drafts/ so `learn` can match it later
  python hz.py learn [--scan DIR ...] [--all]
                                            match drafts to what was actually sent (data/sent.json),
                                            diff them, write learn/report.md + learn/pairs/*.md
  python hz.py voice                        build voice/stats.md, voice/recipients.md, voice/samples.md
  python hz.py init                         create the per-user data home (rules, voice, data, config.json)
  python hz.py where                        print the skill folder and the data home

data/sent.json comes from export_sent.ps1 (Outlook Sent Items, own text only).

Two folders: the SKILL folder (this script's parent: rules/banned.txt, references/) and the per-user
DATA HOME (corrections, voice, sent mail, learn output). Data home = $HZ_HOME if set, else the skill
folder when it already holds data/ (a personal install), else ~/.claude/humanize (a shared install,
so updates to the skill never touch anyone's data).
"""
import argparse
import json
import os
import re
import shutil
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
if os.environ.get("HZ_HOME"):
    HOME = Path(os.environ["HZ_HOME"]).expanduser()
elif (ROOT / "data").exists():
    HOME = ROOT
else:
    HOME = Path.home() / ".claude" / "humanize"
RULES = ROOT / "rules"              # packaged: banned.txt
USER_RULES = HOME / "rules"         # per user: corrections.md, banned.local.txt
DATA = HOME / "data"
VOICE = HOME / "voice"
LEARN = HOME / "learn"
DRAFTS = HOME / "drafts"


def load_cfg():
    p = HOME / "config.json"
    cfg = {"require_closer": True, "signature_name": ""}
    if p.exists():
        try:
            cfg.update(json.loads(p.read_text(encoding="utf-8-sig")))
        except ValueError:
            print(f"config.json unreadable at {p}; using defaults", file=sys.stderr)
    return cfg


CFG = load_cfg()
ME = (CFG.get("signature_name") or "").strip()          # e.g. "Sam Lee"; filled by export_sent.ps1
ME_FIRST = ME.split()[0] if ME else ""

GREETING = re.compile(r"^(hi|hey|hello|good (morning|afternoon|evening)|morning|afternoon)\b[^.?]{0,40}[,!:]?$", re.I)
SIGNOFF = re.compile(r"^(thanks|thank you|thx|ty|best|best regards|kind regards|regards|cheers|sincerely|talk soon)[,.! ]*$", re.I)
LABEL = re.compile(r"^[A-Z0-9(][^:\n]{0,45}:\s+\S")
# required last line of every email (unless config require_closer=false): "Thanks <FirstName>," / "Thanks Team," / "Thanks Sam and Alex,"
CLOSER = re.compile(r"^Thanks\s+(?P<who>[A-Za-z][\w.'-]*(?:\s*(?:,|and|&)\s*[A-Za-z][\w.'-]*)*),$", re.I)
GREET_NAME = re.compile(r"^(?:hi|hey|hello|good morning|good afternoon|morning|afternoon)\s+(.+?)\s*[,!:]?$", re.I)
PHONE = re.compile(r"(\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}")
SIG_HINT = re.compile(r"(https?://|www\.|@[\w-]+\.\w|sent from my|radius channels|^\s*[a-z]?\s*\|)", re.I)
SKIP_SUBJ = re.compile(r"^\s*(accepted|declined|tentative|canceled|cancelled|automatic reply|out of office|updated invitation|invitation)\b", re.I)
SKIP_BODY = re.compile(r"reacted to your message|^test\s*$", re.I | re.M)
WORD = re.compile(r"[A-Za-z][A-Za-z'’]*")

# -ly words that are not adverbs (or are fine): never flagged
LY_OK = {
    "only", "early", "family", "supply", "apply", "reply", "july", "italy", "daily", "weekly", "monthly",
    "quarterly", "yearly", "hourly", "nightly", "assembly", "rely", "ally", "fly", "anomaly", "poly",
    "multiply", "comply", "imply", "reply", "replied", "kelly", "emily", "sally", "holly", "billy",
    "bully", "belly", "jelly", "lily", "molly", "ely", "oly", "friendly", "costly", "timely", "likely",
    "unlikely", "lonely", "lovely", "ugly", "silly", "elderly", "orderly", "curly", "burly", "surly",
    "gnarly", "underbelly", "butterfly", "dragonfly", "firefly", "resupply", "bimonthly", "biweekly",
    "semiannually", "annually",
}


# ---------------------------------------------------------------- shared
def words(text):
    return WORD.findall(text)


def norm_tokens(text):
    """[(normalized, original)] for diffing; punctuation-only tokens dropped."""
    out = []
    for t in text.split():
        n = re.sub(r"[^\w$%]", "", t.lower())
        if n:
            out.append((n, t))
    return out


def load_banned():
    """rules/banned.txt (packaged) + <data home>/rules/banned.local.txt (the user's own additions)
    -> {'error': [(label, regex)], 'warn': [...]}"""
    out = {"error": [], "warn": []}
    lines = []
    for p in (RULES / "banned.txt", USER_RULES / "banned.local.txt"):
        if p.exists():
            lines += ["[error]"] + p.read_text(encoding="utf-8").splitlines()
    sect = "error"
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.lower() in ("[error]", "[warn]"):
            sect = line.lower()[1:-1]
            continue
        label = line.split("  #")[0].strip()
        if label.startswith("re:"):
            pat = label[3:].strip()
        else:
            pat = r"(?<![\w'])" + re.escape(label).replace(r"\ ", r"\s+") + r"(?![\w])"
        try:
            out[sect].append((label, re.compile(pat, re.I)))
        except re.error as e:
            print(f"banned.txt: bad pattern {label!r}: {e}", file=sys.stderr)
    return out


def strip_signature(body, freq):
    """Peel signature / auto-footer lines off the bottom. Returns (own_text, removed_tail_lines)."""
    lines = body.replace("\r\n", "\n").split("\n")
    tail = []
    # the user's signature block starts with their name on its own line: cut from there down
    for i, l in enumerate(lines):
        if ME and i > 0 and re.match(r"^\s*" + re.escape(ME) + r"\d?\s*$", l, re.I):
            tail = lines[i:][::-1]
            lines = lines[:i]
            break
    while len(lines) > 1:
        l = lines[-1].strip()
        if GREETING.match(l):
            break
        if l == "" or l in freq or PHONE.search(l) or SIG_HINT.search(l):
            tail.append(lines.pop())
            continue
        break
    return "\n".join(lines).strip(), [t.strip() for t in reversed(tail) if t.strip()]


def load_sent(exclude_ai=False):
    p = DATA / "sent.json"
    if not p.exists():
        sys.exit("data/sent.json missing. Run scripts/export_sent.ps1 first.")
    rows = json.loads(p.read_text(encoding="utf-8-sig"))
    if isinstance(rows, dict):
        rows = [rows]
    rows = [r for r in rows if r.get("body") and not SKIP_SUBJ.match(r.get("subject") or "") and not SKIP_BODY.search(r["body"])]
    cnt = Counter()
    for r in rows:
        for l in {x.strip() for x in r["body"].splitlines() if x.strip()}:
            cnt[l] += 1
    freq = {l for l, c in cnt.items() if c >= 12 and not GREETING.match(l)}
    for r in rows:
        r["own"], r["tail"] = strip_signature(r["body"], freq)
        r["key"] = f"{r['sent']}|{r.get('subject', '')}"
        r["dt"] = datetime.fromisoformat(r["sent"])
    # drop empty forwards: fewer than 4 words once the greeting is removed
    rows = [r for r in rows if len(words(GREETING.sub("", r["own"].strip().split("\n")[0]) + " " + " ".join(r["own"].split("\n")[1:]))) >= 4]
    # mail-merge / campaign sends: same body (after the greeting) sent 3+ times
    sig = Counter()
    for r in rows:
        ls = [l for l in r["own"].split("\n") if l.strip()]
        r["merge"] = re.sub(r"\W+", " ", " ".join(ls[1:] if ls and GREETING.match(ls[0].strip()) else ls).lower())[:160]
        sig[r["merge"]] += 1
    rows = [r for r in rows if sig[r["merge"]] < 3 or len(r["merge"]) < 25]
    if exclude_ai:
        ai = set(json.loads((DATA / "ai_matched.json").read_text(encoding="utf-8"))) if (DATA / "ai_matched.json").exists() else set()
        rows = [r for r in rows if r["key"] not in ai]
    return rows


def first_recipient(to):
    return (to or "").split(";")[0].strip().strip("'\"") or "(none)"


def pct(vals, q):
    if not vals:
        return 0
    vals = sorted(vals)
    return vals[min(len(vals) - 1, int(q * len(vals)))]


# ---------------------------------------------------------------- lint
def cmd_lint(a):
    text = Path(a.file).read_text(encoding="utf-8-sig")
    lines = text.split("\n")
    errs, warns = [], []
    banned = load_banned()

    for i, raw in enumerate(lines, 1):
        l = raw.rstrip("\r")
        s = l.strip()
        if "—" in l:
            errs.append((i, "em dash"))
        if "–" in l:
            errs.append((i, "en dash"))
        if re.search(r"\s--\s", l):
            errs.append((i, "double hyphen used as a dash"))
        if re.search(r"[“”‘’]", l):
            errs.append((i, "curly quotes"))
        if re.match(r"^\s*([-*•]\s|#{1,6}\s|```|\|)", l) or "**" in l:
            errs.append((i, "markdown (bullet dash, #, **, table or fence); use 'Label: value' lines"))
        if re.search(r"[\U0001F300-\U0001FAFF☀-➿]", l):
            errs.append((i, "emoji"))
        if i == 1 and re.match(r"^subject\s*:", s, re.I):
            warns.append((i, "subject line (drop it when replying on a thread)"))
        for label, rx in banned["error"]:
            if rx.search(l):
                errs.append((i, f"banned: '{label}'"))
        flagged = set()
        for label, rx in banned["warn"]:
            if rx.search(l):
                warns.append((i, f"qualifier/filler: '{label}'"))
                flagged.add(label.lower())
        for w in words(l):
            lw = w.lower().replace("’", "'")
            if lw.endswith("ly") and len(lw) > 4 and lw not in LY_OK and lw not in flagged:
                warns.append((i, f"adverb: '{w}'"))
        # hard wrap: a long line with no closing punctuation followed by a lowercase continuation
        if i < len(lines):
            nxt = lines[i].strip()
            if s and nxt and len(s) >= 40 and s[-1] not in '.:!?)"' and nxt[0].islower() and not LABEL.match(nxt):
                errs.append((i, "hard-wrapped line; one paragraph = one unbroken line"))
            elif s and nxt and not GREETING.match(s):
                warns.append((i, "no blank line before the next line"))

    body_lines = [l.strip() for l in lines if l.strip()]
    if body_lines and re.match(r"^(hi|hey|hello|morning|afternoon|good morning|good afternoon)\s*[,!:]?$", body_lines[0], re.I):
        errs.append((1, f"greeting '{body_lines[0]}' has no name; use the first name ('Hi Sam,') or 'Hi Team,'"))
    last = body_lines[-1] if body_lines else ""
    last_n = max((i for i, l in enumerate(lines, 1) if l.strip()), default=0)
    cm = CLOSER.match(last)
    names = [x for x in (ME, ME_FIRST) if x]
    if names and re.match(r"^-?\s*(" + "|".join(map(re.escape, names)) + r")\b", last, re.I):
        errs.append((last_n, f"own name '{last}' as a sign-off; the email signature adds it"))
    elif a.chat or not CFG.get("require_closer", True):
        pass
    elif cm:
        gm = GREET_NAME.match(body_lines[0])
        greet = gm.group(1).split()[0].strip(",!") if gm else ""
        who = cm.group("who").split()[0].strip(",")
        if greet and greet.lower() not in ("there",) and who.lower() != greet.lower():
            warns.append((last_n, f"closer 'Thanks {who},' does not match the greeting name '{greet}'"))
    elif re.match(r"^(thanks|thank you|thx|ty)\b", last, re.I):
        errs.append((last_n, f"closer '{last}' must be exactly 'Thanks <FirstName>,' ('Thanks Team,' for groups)"))
    elif SIGNOFF.match(last):
        errs.append((last_n, f"sign-off '{last}'; end with 'Thanks <FirstName>,' instead"))
    else:
        errs.append((last_n, "missing last line 'Thanks <FirstName>,' (use --chat for Teams one-liners)"))
    if text.count("!") > 1:
        warns.append((0, f"{text.count('!')} exclamation marks"))
    if text.count("?") > 3:
        warns.append((0, f"{text.count('?')} questions; cut to the ones that block the work"))

    # a "Label: value" line is a spec line only while it stays short; a label on a paragraph is prose
    is_label = lambda l: LABEL.match(l) and len(words(l)) <= 18
    prose = [l for l in body_lines if not GREETING.match(l) and not is_label(l) and not CLOSER.match(l)]
    label_lines = [l for l in body_lines if is_label(l)]
    prose_words = sum(len(words(l)) for l in prose)
    total_words = len(words(text))
    sentences = [x for p in prose for x in re.split(r"(?<=[.!?])\s+", p) if words(x)]
    longest = max((len(words(x)) for x in sentences), default=0)
    for x in sentences:
        n = len(words(x))
        if n > 28:
            warns.append((0, f"{n}-word sentence: '{x[:60]}...'"))
    for p in prose:
        n = len([x for x in re.split(r"(?<=[.!?])\s+", p) if words(x)])
        if n > 3:
            warns.append((0, f"paragraph with {n} sentences: '{p[:50]}...'"))
    # budget scales with the number of questions the incoming email asked
    target, cap = max(90, 30 * a.asks), max(150, 45 * a.asks)
    if not a.long:
        if prose_words > cap:
            errs.append((0, f"{prose_words} prose words (cap {cap}; target under {target} for {a.asks} ask(s)). Cut, or pass --long if the user asked for detail"))
        elif prose_words > target:
            warns.append((0, f"{prose_words} prose words (target under {target} for {a.asks} ask(s))"))
    if len(label_lines) > 12:
        warns.append((0, f"{len(label_lines)} Label: value lines; group or trim"))

    print(f"words {total_words} | prose words {prose_words} | label lines {len(label_lines)} | sentences {len(sentences)} | longest {longest}")
    for n, m in errs:
        print(f"ERROR {('L' + str(n)) if n else '   '}: {m}")
    for n, m in warns:
        print(f"warn  {('L' + str(n)) if n else '   '}: {m}")
    print("FAIL" if errs else ("PASS with warnings" if warns else "PASS"))
    sys.exit(1 if errs else 0)


# ---------------------------------------------------------------- log
def cmd_log(a):
    src = Path(a.file)
    DRAFTS.mkdir(parents=True, exist_ok=True)
    dst = DRAFTS / f"{datetime.now():%Y%m%d-%H%M%S}__{src.name}"
    shutil.copy2(src, dst)
    print(f"logged {dst.name}")


# ---------------------------------------------------------------- learn
def draft_time(p):
    m = re.match(r"(\d{8}-\d{6})__", p.name)
    if m:
        return datetime.strptime(m.group(1), "%Y%m%d-%H%M%S")
    return datetime.fromtimestamp(p.stat().st_mtime)


def clean_draft(text):
    lines = text.replace("\r\n", "\n").split("\n")
    if lines and re.match(r"^\s*subject\s*:", lines[0], re.I):
        lines = lines[1:]
    return "\n".join(lines).strip()


def cmd_learn(a):
    rows = load_sent()
    for r in rows:
        r["toks"] = norm_tokens(r["own"])
        r["set"] = {n for n, _ in r["toks"]}
    state_p = DATA / "learn_state.json"
    done = set() if a.all or not state_p.exists() else set(json.loads(state_p.read_text(encoding="utf-8")))

    files = list(DRAFTS.glob("*.txt")) if DRAFTS.exists() else []
    for d in a.scan or []:
        files += [p for p in Path(d).rglob("*.txt") if p.stat().st_size < 8000]

    pairs, unmatched = [], 0
    for f in files:
        sig = f"{f}|{int(f.stat().st_mtime)}"
        if sig in done:
            continue
        try:
            text = clean_draft(f.read_text(encoding="utf-8-sig"))
        except UnicodeDecodeError:
            text = clean_draft(f.read_text(encoding="cp1252", errors="replace"))
        dt = norm_tokens(text)
        if len(dt) < 8:
            continue
        dset = {n for n, _ in dt}
        dnorm = [n for n, _ in dt]
        best, best_r = None, 0.0
        for r in rows:
            inter = len(dset & r["set"])
            if inter / max(1, len(dset | r["set"])) < 0.2:
                continue
            ratio = SequenceMatcher(None, dnorm, [n for n, _ in r["toks"]], autojunk=False).ratio()
            if ratio > best_r:
                best, best_r = r, ratio
        done.add(sig)
        if best is None or best_r < 0.45:
            unmatched += 1
            continue
        pairs.append((f, text, dt, best, best_r))

    LEARN.mkdir(parents=True, exist_ok=True)
    (LEARN / "pairs").mkdir(exist_ok=True)
    del_words, del_phr, ins_phr, repl = Counter(), Counter(), Counter(), Counter()
    gold, edited = [], []
    ai_keys = set(json.loads((DATA / "ai_matched.json").read_text(encoding="utf-8"))) if (DATA / "ai_matched.json").exists() else set()

    for idx, (f, text, dt, r, ratio) in enumerate(sorted(pairs, key=lambda x: x[3]["dt"], reverse=True), 1):
        ai_keys.add(r["key"])
        sm = SequenceMatcher(None, [n for n, _ in dt], [n for n, _ in r["toks"]], autojunk=False)
        dels, inss, reps = [], [], []
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            old = " ".join(o for _, o in dt[i1:i2])
            new = " ".join(o for _, o in r["toks"][j1:j2])
            if tag == "delete":
                dels.append(old)
            elif tag == "insert":
                inss.append(new)
            elif tag == "replace":
                reps.append((old, new))
        for d in dels + [o for o, _ in reps]:
            for w in words(d):
                if not re.search(r"\d", w):
                    del_words[w.lower()] += 1
            if 1 < len(d.split()) <= 8:
                del_phr[d.lower().strip(" ,.")] += 1
        for i in inss:
            if len(i.split()) <= 8:
                ins_phr[i.lower().strip(" ,.")] += 1
        for o, n in reps:
            if len(o.split()) <= 6 and len(n.split()) <= 6:
                repl[f"{o.lower()}  ->  {n.lower()}"] += 1
        rec = dict(n=idx, file=str(f), sent=r["sent"], to=first_recipient(r["to"]), subject=r.get("subject", ""),
                   ratio=ratio, dw=len(dt), sw=len(r["toks"]), dels=dels, inss=inss, reps=reps)
        (gold if ratio >= 0.95 else edited).append(rec)
        (LEARN / "pairs" / f"{idx:03d}.md").write_text(
            f"# Pair {idx:03d}  similarity {ratio:.2f}\n\nDraft file: {f}\nSent: {r['sent']} to {rec['to']}\nSubject: {rec['subject']}\n"
            f"Words: draft {rec['dw']} -> sent {rec['sw']}\n\n## Draft (what Claude wrote)\n\n{text}\n\n## Sent (what was actually sent)\n\n{r['own']}\n",
            encoding="utf-8")

    (DATA / "ai_matched.json").write_text(json.dumps(sorted(ai_keys), indent=0), encoding="utf-8")
    state_p.write_text(json.dumps(sorted(done), indent=0), encoding="utf-8")

    allp = gold + edited
    out = [f"# /humanize learn report  ({datetime.now():%Y-%m-%d %H:%M})", "",
           f"Drafts scanned this run: {len(pairs) + unmatched}. Matched to a sent email: {len(allp)}. "
           f"Sent unchanged (>=95% same): {len(gold)}. Edited before sending: {len(edited)}."]
    if allp:
        dws = [p["dw"] for p in allp]
        sws = [p["sw"] for p in allp]
        out.append(f"Median words: draft {statistics.median(dws)} -> sent {statistics.median(sws)}. "
                   f"Drafts cut before sending: {sum(1 for p in allp if p['sw'] < p['dw'] * 0.9)} of {len(allp)}.")
    out += ["", "## Words deleted most before sending (excluding numbers)", ""]
    out += [f"{c:>3}  {w}" for w, c in del_words.most_common(60)]
    out += ["", "## Phrases deleted before sending (2-8 words, seen in any pair)", ""]
    out += [f"{c:>3}  {w}" for w, c in del_phr.most_common(60)]
    out += ["", "## Replacements (draft -> sent)", ""]
    out += [f"{c:>3}  {w}" for w, c in repl.most_common(60)]
    out += ["", "## Phrases added before sending", ""]
    out += [f"{c:>3}  {w}" for w, c in ins_phr.most_common(40)]
    out += ["", "## Edited pairs, most-changed first", ""]
    for p in sorted(edited, key=lambda x: x["ratio"]):
        out.append(f"pairs/{p['n']:03d}.md  sim {p['ratio']:.2f}  words {p['dw']}->{p['sw']}  {p['sent'][:10]}  to {p['to']}  | {p['subject'][:60]}")
    out += ["", "## Sent unchanged (gold examples)", ""]
    for p in gold:
        out.append(f"pairs/{p['n']:03d}.md  words {p['sw']}  {p['sent'][:10]}  to {p['to']}  | {p['subject'][:60]}")
    (LEARN / "report.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out[:4]))
    print(f"report: {LEARN / 'report.md'}")


# ---------------------------------------------------------------- voice
def cmd_voice(a):
    rows = load_sent(exclude_ai=True)
    VOICE.mkdir(parents=True, exist_ok=True)
    wc = [len(words(r["own"])) for r in rows]
    firsts, lasts, tails, openers = Counter(), Counter(), Counter(), Counter()
    sent_lens, n_words = [], 0
    flags = Counter()
    quals = ["just", "really", "actually", "very", "basically", "definitely", "probably", "maybe", "hopefully",
             "honestly", "simply", "quite", "pretty", "totally", "absolutely", "sorry", "apologies", "thanks",
             "thank you", "please", "let me know", "attached", "below", "fyi", "np", "sounds good", "will do"]
    qc = Counter()
    trigrams = Counter()
    for r in rows:
        own = r["own"]
        ls = [l.strip() for l in own.split("\n") if l.strip()]
        if not ls:
            continue
        n_words += len(words(own))
        first = ls[0]
        if GREETING.match(first):
            parts = first.split(None, 1)
            firsts[parts[0] + (" " + re.sub(r"[A-Z][\w.'-]*", "<Name>", parts[1]) if len(parts) > 1 else "")] += 1
            flags["greeting"] += 1
            body = ls[1:]
        else:
            firsts["(no greeting) " + " ".join(first.split()[:3])] += 0
            body = ls
        if body:
            lasts[body[-1][:70]] += 1
            openers[" ".join(body[0].split()[:3])] += 1
        for t in r["tail"][:1]:
            tails[t[:60]] += 1
        low = own.lower()
        for q in quals:
            qc[q] += len(re.findall(r"(?<![\w'])" + re.escape(q) + r"(?![\w])", low))
        if "!" in own:
            flags["exclamation"] += 1
        if "?" in own:
            flags["question"] += 1
        if "—" in own or "–" in own:
            flags["em/en dash"] += 1
        if any(LABEL.match(l) for l in body):
            flags["label: value lines"] += 1
        if any(re.match(r"^[-*•]\s", l) for l in body):
            flags["dash/bullet lines"] += 1
        if re.search(r"\b\w+'(s|t|re|ll|ve|m|d)\b", own):
            flags["contractions"] += 1
        for p in body:
            for x in re.split(r"(?<=[.!?])\s+", p):
                if words(x):
                    sent_lens.append(len(words(x)))
        toks = [w.lower() for w in words(" ".join(body))]
        for i in range(len(toks) - 2):
            trigrams[" ".join(toks[i:i + 3])] += 1

    n = len(rows)
    dates = sorted(r["dt"] for r in rows)
    st = [f"# Sent-mail voice stats ({datetime.now():%Y-%m-%d})", "",
          f"Source: {n} sent emails, {dates[0]:%Y-%m-%d} to {dates[-1]:%Y-%m-%d}, own text only (quoted thread and signature stripped; Claude-drafted matches excluded).",
          "", "## Length (words)", "",
          f"Median {statistics.median(wc):.0f}. 25th pct {pct(wc, .25)}. 75th pct {pct(wc, .75)}. 90th pct {pct(wc, .9)}.",
          f"Sentence length: median {statistics.median(sent_lens):.0f} words, 90th pct {pct(sent_lens, .9)}.",
          "", "## Habits (% of emails)", ""]
    st += [f"{k}: {100 * v / n:.0f}%" for k, v in flags.most_common()]
    st += ["", "## Greeting line (top)", ""] + [f"{c:>4}  {k}" for k, c in firsts.most_common(12) if c]
    st += ["", "## First words after greeting (top)", ""] + [f"{c:>4}  {k}" for k, c in openers.most_common(30)]
    st += ["", "## Last line typed (top)", ""] + [f"{c:>4}  {k}" for k, c in lasts.most_common(25)]
    st += ["", "## First line of the stripped signature/footer (top)", ""] + [f"{c:>4}  {k}" for k, c in tails.most_common(5)]
    st += ["", f"## Word/phrase use per 1,000 words (total {n_words} words)", ""]
    st += [f"{1000 * c / max(1, n_words):6.2f}  {q}" for q, c in sorted(qc.items(), key=lambda x: -x[1])]
    st += ["", "## Most common 3-word runs", ""] + [f"{c:>4}  {k}" for k, c in trigrams.most_common(40)]
    (VOICE / "stats.md").write_text("\n".join(st) + "\n", encoding="utf-8")

    by = defaultdict(list)
    for r in rows:
        by[first_recipient(r["to"])].append(r)
    rec = ["# Per-recipient habits (from sent mail)", "", "recipient | emails | median words | greeting used most", "--- | --- | --- | ---"]
    for name, rs in sorted(by.items(), key=lambda x: -len(x[1]))[:60]:
        g = Counter()
        for r in rs:
            ls = [l.strip() for l in r["own"].split("\n") if l.strip()]
            g[ls[0] if ls and GREETING.match(ls[0]) else "(none)"] += 1
        rec.append(f"{name} | {len(rs)} | {statistics.median(len(words(r['own'])) for r in rs):.0f} | {g.most_common(1)[0][0]}")
    (VOICE / "recipients.md").write_text("\n".join(rec) + "\n", encoding="utf-8")

    picks, per = [], Counter()
    for r in sorted(rows, key=lambda r: r["dt"], reverse=True):
        w = len(words(r["own"]))
        name = first_recipient(r["to"])
        if 10 <= w <= 140 and per[name] < 3:
            picks.append(r)
            per[name] += 1
        if len(picks) >= 60:
            break
    sm = ["# Real emails the user wrote (voice reference, newest first)", "",
          "Own text only. Use these for rhythm, length, greeting and wording. Never copy deal facts from them.", ""]
    for r in picks:
        sm += [f"---- {r['sent'][:10]} to {first_recipient(r['to'])} | {r.get('subject', '')[:70]}", "", r["own"], ""]
    (VOICE / "samples.md").write_text("\n".join(sm) + "\n", encoding="utf-8")
    print(f"voice built from {n} emails: stats.md, recipients.md ({len(by)} recipients), samples.md ({len(picks)} samples)")


# ---------------------------------------------------------------- init / where
CORRECTIONS_TEMPLATE = """# Corrections log

Every rule here came from the user editing or rejecting a draft. Newest first. /humanize reads this
file on every run and these rules override SKILL.md where they conflict.

Format: date | what they changed or said | the rule.
"""

PROFILE_TEMPLATE = """# Voice profile

Not built yet. Run `/humanize voice` (Windows + Outlook desktop) to build it from your Sent Items.
Until then, write to SKILL.md's defaults: first-name greeting, answer first, short, "Thanks <FirstName>," last.
"""


def cmd_init(a):
    for d in (USER_RULES, DATA, VOICE, LEARN, DRAFTS):
        d.mkdir(parents=True, exist_ok=True)
    made = []
    for p, body in ((USER_RULES / "corrections.md", CORRECTIONS_TEMPLATE),
                    (USER_RULES / "banned.local.txt", "# Your own banned phrases, one per line. Same format as the skill's rules/banned.txt.\n[error]\n"),
                    (VOICE / "profile.md", PROFILE_TEMPLATE),
                    (HOME / "config.json", json.dumps({"require_closer": True, "signature_name": ""}, indent=2) + "\n")):
        if not p.exists():
            p.write_text(body, encoding="utf-8")
            made.append(p.name)
    print(f"data home: {HOME}")
    print("created: " + (", ".join(made) if made else "nothing (already set up)"))


def cmd_where(a):
    print(f"skill folder: {ROOT}")
    print(f"data home:    {HOME}")
    print(f"corrections:  {USER_RULES / 'corrections.md'}")
    print(f"voice:        {VOICE / 'profile.md'}")
    print(f"signature:    {ME or '(not set: run export_sent.ps1 or edit config.json)'}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("lint"); p.add_argument("file"); p.add_argument("--long", action="store_true"); p.add_argument("--asks", type=int, default=1); p.add_argument("--chat", action="store_true"); p.set_defaults(fn=cmd_lint)
    p = sub.add_parser("log"); p.add_argument("file"); p.set_defaults(fn=cmd_log)
    p = sub.add_parser("learn"); p.add_argument("--scan", nargs="*"); p.add_argument("--all", action="store_true"); p.set_defaults(fn=cmd_learn)
    p = sub.add_parser("voice"); p.set_defaults(fn=cmd_voice)
    p = sub.add_parser("init"); p.set_defaults(fn=cmd_init)
    p = sub.add_parser("where"); p.set_defaults(fn=cmd_where)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
