---
name: humanize
description: Write or rewrite any email, reply, Teams message or note going to a customer, partner, reseller, distributor or vendor rep so it is short, direct, in the user's own voice, and free of AI tells. Use for every customer-facing draft, even one-liners. Triggers on "humanize", "/humanize", "reply to", "write back to", "draft an email", "email to", "respond to", "make this sound like me", "shorten this", "too long", "sounds like AI", or pasted text to clean up. "/humanize voice" builds the user's voice profile from Outlook Sent Items; "/humanize learn" compares past drafts with what the user actually sent and adds rules.
---

# /humanize

The job: text the user can paste and send without editing. The skill was built from one seller's data: 40 of 41 AI drafts got edited before sending, and almost every edit was a cut. Every rule below closes that gap.

Two folders:

- **Skill folder**: the folder this SKILL.md is in (the base directory shown when the skill loads). Written as `<skill>` below. Holds `scripts/`, `rules/banned.txt`, `references/`.
- **Data home**: the user's own data, `~/.claude/humanize` by default. Written as `<home>` below. Holds `rules/corrections.md`, `rules/banned.local.txt`, `voice/`, `data/`, `learn/`, `config.json`. Run `python "<skill>/scripts/hz.py" where` to print both.

## Modes

- Draft (default): the user gives facts or says "reply to X". Write the message.
- Rewrite: the user pastes text. Rewrite it to these rules. Same facts, far fewer words.
- `/humanize voice`: build the voice profile (bottom).
- `/humanize learn`: learn from sent mail (bottom).

## Step 0. First run

If `<home>/rules/corrections.md` does not exist, run `python "<skill>/scripts/hz.py" init`, then tell the user in two lines: their data lives in `<home>`, and on Windows with Outlook desktop `/humanize voice` makes drafts match how they write.

## Step 1. Load context (every run, before writing)

1. `<home>/rules/corrections.md`. Every line is a past correction from this user. These override anything else in this file.
2. `<home>/voice/profile.md`, and `<home>/voice/recipients.md` if it exists (the greeting the user uses with each person).
3. The incoming email, when this is a reply. Use the pasted text, or pull it with whatever mail tool the user has. From it, note: their first name, each question they asked (in order), and how long their email was.
4. Facts. This skill does not invent facts. Specs, prices, dates and part status come from the user, their files or their tools. Anything you cannot confirm goes in as `[CONFIRM: what]`.

## Step 2. Decide what goes in

List the asks from their email and the facts that answer them. Then cut:

- Anything they did not ask about and do not need to act on. No background, no "how it works", no trade-offs, no side notes on things they did not ask about, no alternatives they did not ask for. Exceptions: when the answer is "no", give the one alternative that gets them what they wanted; when they asked about options or cost, the alternative is the answer.
- "Why" paragraphs: sizing math, cost arguments, reasoning chains. Give the conclusion; give the reasoning only if they asked why.
- Part numbers, internal codes and per-item prices, unless they asked for them or the price is the answer.
- Questions with a sensible default. Pick the default and state it in one line ("Windows Server 2025 Standard added, CALs not included.") instead of asking. Ask at most 2 questions, only ones that block the next step.
- Anything already sent in this thread. Follow-ups carry only what changed.
- Anything about the drafting process: apologies, "I double-checked", "after reviewing", "I updated".

The most common real edit: the user keeps the 3-4 sentence answer and deletes everything after it. Do that before they have to.

## Step 3. Write it

### Shape

```
<Greeting>,

<Answer or main fact. 1-2 sentences.>

<Label: value lines, only if there is a list of specs or differences>

<One ask or next-step line, only if there is a real ask.>

Thanks <FirstName>,
```

The last line is "Thanks <FirstName>," with the same first name as the greeting. Groups: "Thanks Team,". Two people: "Thanks Sam and Alex,". Nothing after it: the email signature adds the user's name. Teams/chat one-liners mid-thread skip the greeting and the closer (lint with `--chat`). Users who do not want the closer set `"require_closer": false` in `<home>/config.json`.

Length: under 90 words of prose for one ask; 150 is the hard cap. With more asks the budget is about 30 words per ask (cap 45 per ask). Short "Label: value" spec lines (18 words or fewer) do not count but stay at 12 or fewer.

Sentences: 20 words or fewer, one fact each. Paragraphs: 1-2 sentences.

### Greeting

First name always: "Hi Sam," / "Hey Sam," / "Morning Sam," (before noon) / "Afternoon Sam,". Groups: "Hi Team,". Use the form the profile or recipients file says this user uses with that person. Never a bare "Hi,". Use `[Name]` only when the name is unknown, and say so in chat.

### Corrections

The first line after the greeting is the correct fact. Nothing before it.

- "Memory is 512GB per node (16x 32GB). Revised config attached."
- If the reader must know which number to replace: "Lead time is 3-4 weeks, not 10 days."
- Never: "you're right", "good catch", "thanks for catching that", "my mistake", "apologies", "I misspoke", "to clarify", "here is the corrected information below".

### When their premise is wrong

Answer first, then the fix in one plain line. "Yes, four cards fit. Both cards are 10/25GbE, so each port runs at the speed of its optic." Never "actually", "to clarify", "just so you know".

### Next step

If there is a next step, end with it in one line: what the user does next ("I will build the two-server option next.") or what they do ("Send it to distribution for pricing when they approve.").

### No qualifiers, no adverbs

Cut: just, really, very, actually, basically, definitely, certainly, simply, pretty, quite, totally, absolutely, honestly, hopefully, unfortunately, I think, I believe, probably, maybe, should be able to. State facts flat. If something is truly uncertain, say what is unknown ("Lead time is not confirmed yet.") or ask. Never hedge a fact you know.

### No framing, no filler

No sentence that comments on the information instead of giving it: "worth noting", "that said", "for context", "the good news is", "keep in mind", "short version", "here's the breakdown", "please see below", "hope this helps", "happy to help", "feel free to", "don't hesitate". Test: delete the sentence. If the reader knows exactly as much as before, it stays deleted.

### No AI tells

Scan the draft against `<skill>/references/ai-patterns.md`: every pattern from the original humanizer and Wikipedia's "Signs of AI writing", plus email-only tells and a "what not to flag" list so plain human writing is left alone. Zero em dashes or en dashes. No markdown. No bold. No emoji. No curly quotes. No rule-of-three padding. No "-ing" tails. No synonym cycling.

### The user's words

Use the shorthand, openers and ask lines in the voice profile. Quantities as digits ("2x 15.36TB", "8x"). Include identifiers the reader needs: deal reg, quote or ticket numbers, "spec sheet attached", @FirstName for whoever owns the next step. Capacity in TB, never TiB. Lenovo sellers: "Top Choice Express (TCE)" on first use, then TCE; never "quick-ship".

### Format (Outlook paste)

- Plain text. No markdown of any kind.
- One paragraph = one line. Never hard-wrap. Blank line between paragraphs and between "Label: value" lines.
- Labels in sentence case: "Data drives:", not "Data Drives:".
- No subject line when replying on a thread.

## Step 4. Check, deliver, log

1. Write the draft to a .txt file (the deal or project folder if the user keeps one, else a scratch folder). Overwrite in place on revisions.
2. Lint it and fix until it prints PASS:
   `python "<skill>/scripts/hz.py" lint "<file>" --asks <number of questions they asked>`
   Fix every ERROR. Fix every warn unless the word carries meaning in that sentence. `--long` only when the user asked for detail; `--chat` for Teams one-liners.
3. Self-audit, silently: ask "what makes this read as AI-written?" and fix every answer (the original humanizer's still-AI pass). Then read it once as the recipient and delete any sentence they would not miss. Never show the audit; the user gets the finished text only.
4. Log it so Learn mode can compare it with what gets sent: `python "<skill>/scripts/hz.py" log "<file>"`
5. Give the user the file (and the text, if they want to copy it from chat). Say nothing about the draft except one line per `[CONFIRM: ...]`. No "draft / still-AI / final" sections, no change summaries, no alternate versions unless asked.

Every time the user corrects a draft in chat ("too long", "remove that", "don't say X"), add a dated line to `<home>/rules/corrections.md`, and any phrase to `<home>/rules/banned.local.txt`, in the same turn.

## Examples

Correction. Before:

> Hi Sam, You're absolutely right, and thanks for catching that. That was my mistake. I had listed the memory as 256GB per node, but it should be 512GB per node. Here is the corrected information below: Memory: 512GB per node (16x 32GB). I've updated the config and attached the revised version. Let me know if you have any other questions!

After:

```
Hi Sam,

Memory is 512GB per node (16x 32GB). Revised config attached.

Thanks Sam,
```

Technical question ("will they have room to go above 10G?"). The real draft had five more paragraphs; the seller deleted all of them:

```
Morning Jordan,

Yes, they'll have room to go above 10G. Every SFP option on these nodes is a dual-rate 10/25GbE SFP28 card. It runs 10G optics and DAC today and 25G later on the same card. Only the RJ45 (10GBASE-T) cards are capped at 10G.

Thanks Jordan,
```

Differences email:

```
Hi Taylor,

Revised config attached, all Top Choice Express (TCE).

Processors: 2x 12C instead of 8C, 8C is not in TCE

Memory: 16x 16GB to match the 256GB requested

Drives: 4x 3.84TB instead of 7.68TB, 7.68TB is not in TCE

Let me know if you have any more questions.

Thanks Taylor,
```

Follow-up:

```
Hi Alex,

Did they get a chance to review the two configs from Thursday?

Thanks Alex,
```

## Voice mode (`/humanize voice`)

Windows with Outlook desktop only. Monthly, or on first setup.

1. `& "<skill>/scripts/export_sent.ps1" -Days 365 -Max 3000` (read-only; also saves the user's signature name to config.json)
2. `python "<skill>/scripts/hz.py" learn --scan "<folder where drafts are saved>"` (marks AI-written emails so they are left out of the voice)
3. `python "<skill>/scripts/hz.py" voice` (writes `<home>/voice/stats.md`, `recipients.md`, `samples.md`)
4. Read stats.md and samples.md, then write `<home>/voice/profile.md`: typical length, greetings, how they open, shorthand and words they use, ask lines, and "habits to drop" (their own apologies, hedges, typos and run-ons, which they would still edit out of a draft). Keep it under 40 lines.

## Learn mode (`/humanize learn`)

Windows with Outlook desktop only. Weekly, or when drafts still need edits.

1. `& "<skill>/scripts/export_sent.ps1" -Days 45`
2. `python "<skill>/scripts/hz.py" learn` (add `--scan "<folder>"` to include drafts that were never logged)
3. Read `<home>/learn/report.md`, then each edited pair in `<home>/learn/pairs/`.
4. For each edit: decide whether it is a rule (they would make it again) or a one-off fact fix. Rules go in as a dated line at the top of `<home>/rules/corrections.md`; phrases they deleted go in `<home>/rules/banned.local.txt`.
5. Tell the user in a few lines: drafts matched, sent unchanged, each new rule (one line each).

## Privacy

`<home>/data`, `learn` and `voice` hold real customer email text. They stay on this machine. Never send them to an outside service, and never quote one customer's details in another customer's email.
