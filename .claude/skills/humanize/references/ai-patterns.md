# AI-writing tells (condensed for business email)

Covers all 33 patterns and the detection guidance from the original anthropic-skills humanizer, every email-relevant sign on Wikipedia's "Signs of AI writing" page (checked 2026-10-21; wiki-markup and citation-format signs left out), plus email-only tells. Two things are reversed on purpose: the original keeps every paragraph and adds personality; /humanize cuts, and stays plain. Scan every draft against this list. A hit is a fix, not a judgment call.

## Content tells

1. Inflated significance: "marks a pivotal moment", "plays a key role", "sets the stage for", "reflects a broader". Fix: state the fact.
2. Name-dropping notability: "recognized by Gartner, Forrester and IDC", "featured in major outlets". Fix: the one fact that matters, with its source ("#1 in x86 uptime, ITIC 2025").
3. Superficial -ing tails: ", ensuring...", ", highlighting...", ", allowing you to...", ", giving you...". Fix: cut the tail, or make it a short sentence if it carries a fact.
4. Promotional words: boasts, robust, powerful, best-in-class, industry-leading, seamless, game-changer. Fix: the spec or number.
5. Vague authority: "industry experts", "many customers find", "it's widely known". Fix: name the source or cut.
6. "Challenges and outlook" wrap-ups, "despite these challenges". Fix: cut.
7. Generic upbeat endings: "exciting times", "looking forward to a great partnership", "this sets you up well". Fix: cut.
8. Speculative gap-fill and cutoff disclaimers: inventing a reason, date or spec to cover a gap; "as of my last update", "based on available information", "details are limited". Fix: write [CONFIRM: what is missing] and flag it to the user in one line.
9. Invented links and identifiers: a URL, quote #, deal reg #, part number or ticket ID that is not in the inputs. Fix: only copy identifiers from the incoming email, the files or the user; never construct one.
10. Vague association: "in connection with", "associated with", "connected with" in place of the real relationship. Fix: say it ("for the Acme refresh", "on the same deal reg").

## Language tells

11. AI vocabulary (full list in rules/banned.txt): delve, leverage, robust, comprehensive, seamless, crucial, pivotal, key (adjective), landscape, ensure, enhance, foster, showcase, underscore, testament, additionally, moreover, furthermore.
12. Copula avoidance: "serves as", "stands as", "features", "offers", "boasts". Fix: is / has.
13. Negative parallelism: "It's not just X, it's Y", "not only... but also", tailing "no guessing" fragments. Fix: say Y.
14. Rule of three: lists padded to three items, "fast, reliable, and scalable". Fix: keep the items that are true and asked about.
15. Synonym cycling: server / node / system / platform / box for the same thing. Fix: pick one word and repeat it.
16. False ranges: "from edge to core", "from small offices to large data centers". Fix: cut.
17. Passive voice and subjectless fragments: "the config was updated", "no driver needed". Fix: "I updated the config", "Windows needs no driver", or "Revised config attached."
18. Hedge stacks: "could potentially", "may possibly", "should be able to". Fix: one verb. If it is uncertain, say what is unknown.
19. Filler phrases: "in order to" (to), "due to the fact that" (because), "at this point in time" (now), "has the ability to" (can), "it is important to note that" (cut).
20. Stiff word swaps: utilized (used), attempted (tried), relocated (moved), as a result of (because), the fact that (cut), a part of (part of), all of the (all the).
21. "Y rather than X" reversals stacked through an email. One is normal English; a pattern of them is a tell.
22. Uniform hyphenation: hyphenate a compound before a noun ("a high-quality build") but not after it ("the build is high quality"). AI hyphenates both.

## Style tells

23. Em dashes and en dashes. Zero. Also no " -- ". Use a period, comma, colon or parentheses.
24. Bold, headings, emoji, markdown bullets. Zero in an email. Lists are "Label: value" lines, one short line each. A bold label, or a label followed by a whole paragraph, is the AI version.
25. Markdown structure that pastes as junk: thematic breaks ("---", "* * *"), tables, and [text](url) links. Write a URL bare on its own line.
26. Title Case labels. Sentence case: "Data drives:", not "Data Drives:".
27. A label or opening line restated by the next sentence ("Networking: Here is the networking."). Fix: give the content.
28. Curly quotes. Straight quotes only.
29. Every sentence the same length and rhythm. Mix a 5-word sentence with a 15-word one.
30. Staccato drama: a run of short punchy fragments for effect. Fix: plain sentences.
31. Aphorisms: "X is the currency of Y", "speed is the new uptime". Fix: cut.
32. Persuasive authority tropes: "the real question is", "at its core", "what really matters", "fundamentally". Fix: say the point.
33. Fake-candid openers: "Honestly?", "Here's the thing", "The short answer:", "Bottom line:". Fix: give the answer.

## Chatbot tells (the worst ones in email)

34. Grading the question or the person: "Great question", "Good catch", "You're right". Fix: answer.
35. Apologizing, or narrating the process or the change: "My mistake", "I double-checked and", "After reviewing", "I went back and re-ran it", "this was changed from", "Here is the corrected info below". Fix: describe how things are now.
36. Announcing content: "Below is a summary", "Here's what you need to know", "Please see below", "Let's dive in". Fix: the content.
37. Offering more help: "Happy to help", "Feel free to reach out", "Don't hesitate", "Would you like me to", "Hope this helps". Fix: one concrete ask, or nothing.
38. Restating their question back to them before answering. Fix: answer first.
39. Summarizing what you just said at the end. Fix: cut the last paragraph if it repeats.
40. Chat-tool residue pasted into the email: citation tokens ("contentReference", "citeturn", "[cite: 1]"), tracking tags on links ("utm_source=chatgpt.com"), a leftover "Claude responded:" line. Fix: delete; strip the tracking tag from the URL.
41. Unfilled placeholders of any kind: "[Your Email Address]", "[link]", "PASTE_URL_HERE", "2026-11-XX". The only allowed placeholder is [CONFIRM: ...], and each one is flagged to the user.
42. Letter templates: "I am writing to", "I hope this message finds you well", "Is there anything else", "Let's connect". Fix: start with the content.
43. Volunteering trade-offs, alternatives, caveats or next steps nobody asked for. Fix: cut unless the answer is "no" and the alternative is the only way forward.

## What NOT to flag

These are not AI tells on their own. Do not "fix" them:

- Clean grammar and a consistent style. Polish is not AI.
- A greeting and a closing line. Letters have had them for centuries.
- One transition word ("however", "also") or one short sentence for emphasis. Tells come in clusters.
- Formal or technical vocabulary that is the right word ("redundant", "throughput").
- Mixed casual and formal register in the same email.
- Digits, part numbers, specs, @mentions, one exclamation mark confirming good news ("Done!").

Style shift is a tell of its own: a draft far more polished, formal or long than the user's own sent mail (see the voice profile) reads as AI even with zero banned words. Match the profile.

Look for clusters. One em dash plus rule-of-three plus "robust" plus a summary paragraph is AI. Any one alone may not be.

## Signs of a human writer (keep these)

- Specific, hard-to-fake detail: real names, dates, quantities, deal or quote numbers, the exact part that changed.
- The user's own shorthand from their voice profile (disti, configs, DR#, TCE, KYD, "2x 32GB", "3yr-4hr").
- A real aside in parentheses that carries a fact ("(smallest size that still does RAID 10)").
- Uneven sentence length.
- A direct question to a named person ("@Sam can you send this to distribution?").
