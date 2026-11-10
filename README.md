# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- The path a submission takes, from arriving to the label a reader sees.
     Six or seven steps — this is the trace you wrote in Milestone 1. -->

1. POST /submit (app.py) receives {text, creator_id}. It adds input checks: missing, empty or very long text gets rejected here.
2. detector.model_signal adds model_score, a 0–1 number from GPT‑2 perplexity.
3. stylometry.style_signal adds style_score, a 0–1 number from the shape of the text.
4. scoring.combine_signals adds one combined score.
5. scoring.score_to_label adds guess (ai/human/unsure) and the sentence a person reads.
6. audit.log_decision adds a content_id and a permanent record with status decided.
7. The response goes back to the site, and the reader sees the label. If the writer disagrees, /appeal moves the status to under_review.

---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

**What it measures:** Predictability

**Why that might differ between human and AI writing:** Models pick likely next words, so their text is easy to predict

**What it can't see:** Plain writing by people who write simply like second-language writers, young writers. IT also misses ornate AI text full of rare words.

### Signal two — the style signal

**What it measures:** The shape of the text, without reading it. Two measures count: how much sentence length varies (standard deviation ÷ mean of words per sentence) and punctuation density (commas, `; : — ( ) " ! ?` per word, full stops not counted). Each is mapped onto 0–1 AI-ness with a straight line between a human-looking and an AI-looking value, then the two are averaged. A third measure, type-token ratio (unique ÷ total words, averaged over 50-word windows), is computed but given zero weight — on my calibration inputs it pointed the wrong way: the clearly-AI sample had more varied vocabulary (0.91) than any of the longer human texts, and my own plain paragraph had the least (0.71).

> **Changed in unit 8:** punctuation density now has weight 0, so signal two is sentence-length spread alone. It pointed the wrong way for plain human writing; see **The Improvement**. The original design is left above unchanged.

**Why that might differ between human and AI writing:** AI writes even, mid-length sentences with tidy, sparse punctuation. Humans are lumpier — a two-word sentence next to a forty-word one, asides in dashes, a colon where a list starts.

**What it can't see:** Meaning. Typos, chopped-up sentences or a pasted quotation change the score without changing who wrote it. And it shares signal one's blind spot: plain writing — short sentences with few commas — leans machine-like to it (my own plain paragraph scored 0.59).

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:** Average the two signals equally. Then one asymmetric rule for disagreement: if *either* signal leans human, the combined score is capped inside the unsure band. So a high-confidence AI label needs both signals to lean AI, while a human label only needs the average to be low. Wrongly calling a writer human costs the site a little; wrongly calling them AI costs that person a lot, so a split between the signals is never allowed to become an accusation.

**The numbers:** (all in `config.py`)
- `WEIGHT_MODEL_SIGNAL = 0.5`, `WEIGHT_STYLE_SIGNAL = 0.5`
- `LEANS_HUMAN = 0.5` — a signal at or below this leans human
- `DISAGREEMENT_CAP = 0.6` — the most the combined score can be when a signal leans human (below `AI_THRESHOLD = 0.65`)
- Style-signal anchors (in `stylometry.style_signal`): sentence spread 0.90 → 0, 0.30 → 1; punctuation density 0.12 → 0, 0.03 → 1 (weight 0 since unit 8)

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule does with it:**

The `clearly_human` sample (a first-person paragraph about a sleepless night). The model signal gave it **0.45** — near the middle, because ordinary words in a personal story are fairly predictable to GPT-2. The style signal gave it **0.02**, strongly human: sentence lengths swing from two words to forty, and it is full of dashes, colons and commas. The average is **0.23**, which lands in high-confidence human. The cap doesn't fire because the combined score is already low — it only matters when a split would otherwise push a text toward AI.

**Calibration run** (both signals printed separately). All six are files in `samples/`. `formal_human.json` and `plain_human.json` are my own writing, and `edited_ai.json` is chatbot text I edited lightly:

| Input | model | style | combined |
|---|---|---|---|
| clearly AI | 0.75 | 0.83 | 0.79 |
| clearly human | 0.45 | 0.02 | 0.23 |
| borderline | 0.35 | 0.53 | 0.44 |
| formal human | 0.27 | 0.63 | 0.45 |
| plain human | 0.62 | 0.59 | 0.60 |
| lightly-edited AI | 0.59 | 0.59 | 0.59 |

The formal human text is a post I wrote, with technical vocabulary (MCP servers, micro-services, gratuity) that GPT-2 finds surprising, so the model signal reads it as human (0.27). The style signal leans the other way (0.63) because its bullet points are even, mid-length lines. The disagreement puts it in unsure. The lightly-edited AI also lands in unsure: a miss, but the cheap kind.
**What the rule can't fix:** my own plain paragraph — short sentences, everyday words, written by me — scores 0.60. It lands in unsure, but only 0.05 below the AI line (0.65). Both signals lean AI on it (model 0.62, style 0.59), so they *agree*, and agreement is exactly when the disagreement cap doesn't apply. A slightly plainer paragraph would cross the line and get the AI label. This is the false-positive writer from Milestone 1, and it's the case my criterion 1 is most likely to fail on.



---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human | 0.00 – 0.35 | This reads like it was written by a person. |
| unsure | 0.35 – 0.65 | We can't tell from the writing alone whether this was written by a person or with help from AI. That happens often, especially with short or plainly written pieces, and it isn't a judgement about the writer. |
| high-confidence AI | 0.65 – 1.00 | Our checks suggest this was probably written with AI. Automated checks can be wrong, and they are wrong more often about plain, simple writing. If you wrote this yourself, you can ask for a person to review it. |

The bands meet exactly (`<= 0.35` is human, `>= 0.65` is AI, everything between is unsure), so there's no gap. All three were reached with the `samples/` files: clearly_human → 0.23, borderline → 0.44, clearly_ai → 0.79.

**Why I worded the "unsure" one this way:**
<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->

It puts the limit on the tool ("we can't tell from the writing alone"), not on the writer. It says this is common, so a writer who gets it doesn't read it as being singled out. And it says outright that it isn't a judgement, because the person most likely to see it is a real writer whose plain style confused both signals.

The AI label is the one that can actually hurt someone, so it says "probably", admits the check can be wrong, names the kind of writing it gets wrong most (my own plain paragraph came within 0.05 of the AI line), and points straight to the appeal.



---

## Sample Run

<!-- One submission and one appeal, pasted as text: the request, the response,
     and the log entries. -->

**A submission**

<!-- The response needs content_id, guess, confidence, label, AND both
     signal scores - model_score and style_score. Unit 8's tools read those
     two off the response, so leaving them out costs you next unit's
     diagnostics. -->

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d @samples/clearly_ai.json
```

```json
{
  "confidence": 0.7925,
  "content_id": "c_47dbce47d028",
  "creator_id": "demo_instructor",
  "guess": "ai",
  "label": "Our checks suggest this was probably written with AI. Automated checks can be wrong, and they are wrong more often about plain, simple writing. If you wrote this yourself, you can ask for a person to review it.",
  "model_score": 0.7544,
  "style_score": 0.8307
}
```

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "c_47dbce47d028", "reasoning": "I wrote this myself for a workplace newsletter. I write formally because English is my second language."}'
```

```json
{
  "content_id": "c_47dbce47d028",
  "message": "Thanks. Your appeal has been recorded and this piece is now waiting for a person to review it.",
  "original_guess": "ai",
  "status": "under_review"
}
```

An unknown id returns `404 {"error": "not_found", ...}` and a missing `reasoning` returns `400 {"error": "bad_request", ...}` — neither writes to the log.

**What the log shows afterwards**

```bash
$ curl "http://127.0.0.1:5000/log?limit=3"
```

```json
{
  "count": 3,
  "entries": [
    {
      "combined_score": 0.4401,
      "content_id": "c_6b16505e2252",
      "creator_id": "demo_instructor",
      "guess": "unsure",
      "label": "We can't tell from the writing alone whether this was written by a person or with help from AI. That happens often, especially with short or plainly written pieces, and it isn't a judgement about the writer.",
      "model_score": 0.3489,
      "status": "decided",
      "style_score": 0.5314,
      "timestamp": "2026-11-02T11:44:00+00:00"
    },
    {
      "combined_score": 0.7925,
      "content_id": "c_47dbce47d028",
      "creator_id": "demo_instructor",
      "guess": "ai",
      "label": "Our checks suggest this was probably written with AI. Automated checks can be wrong, and they are wrong more often about plain, simple writing. If you wrote this yourself, you can ask for a person to review it.",
      "model_score": 0.7544,
      "status": "decided",
      "style_score": 0.8307,
      "timestamp": "2026-11-02T11:44:00+00:00"
    },
    {
      "content_id": "c_47dbce47d028",
      "creator_id": "demo_instructor",
      "event": "appeal",
      "reasoning": "I wrote this myself for a workplace newsletter. I write formally because English is my second language.",
      "status": "under_review",
      "timestamp": "2026-11-02T11:44:04+00:00"
    }
  ]
}
```

The original decision for `c_47dbce47d028` stays in the log unchanged, and the appeal sits after it with status `under_review`.

---

## How I Used AI

**Moment 1**

- *What I asked for:* I missed attending this week's class, and I just went through a layoff, so I couldn't read, understand and makesense of the assignment. I asked AI to explain me what this project it about and what I should do.
- *What came back:* It gave me clear explanation of the project and laid out step by step guide of what I should do.
- *What I changed:* I followed it

**Moment 2**

- *What I asked for:* I asked it to build the second signal and the combining rule, and then to write the results into the readme.
- *What came back:* Working code and a calibration run that changed the picture of the signals. Type-token ratio pointed the opposite way from what the brief predicted, so it was given zero weight. The combining rule caps the score inside 'unsure' whenever the two signals disagree.
- *What I changed:* I kept the code as it was. 

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** 5 per minute, 50 per day

**Why those numbers and not others:**
A real writer submits their own work a few times an hour at most. Even someone pasting in a revision, checking the result, and trying again won't send more than five pieces in a minute, and fifty in a day is far more than any one person writes. A script trying to map my thresholds needs hundreds or thousands of near-identical variations to find where `unsure` turns into `ai`. At 5 a minute it gets 50 probes a day, so a thousand variations takes three weeks instead of a few seconds. The per-minute limit stops bursts, and the per-day limit stops a slow script that waits out each minute. I went lower than 10 a minute because every submission runs GPT-2 inline, so a burst also costs real compute.

**What a caller counts as:** Per `creator_id`, falling back to the caller's IP address when the request doesn't send one. This is fair to a household or classroom sharing one address, because each writer gets their own limit. The weakness is that `creator_id` is whatever the caller says it is. A script that sends a new `creator_id` with every request gets a fresh limit each time, so the limit only stops an attacker who uses one name. Limiting per address as well would close that gap, but it would also start blocking people who share a network.

**What a rejection leaves behind:** Every 429 writes a `rejected` entry to the audit log with `reason: rate_limited` and the limit that was hit. A 400 from `/submit` (missing text, or text too short to score) writes one too, with `reason: missing_text` or `text_too_short`. A flood shows up in `GET /log` as a run of rejections against one `creator_id`, not as silence.

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```
200 200 200 200 200 429 429 429 429 429 429 429 429 429 429
```

---

## Attack Run — Before

Run with `python run_attacks.py --set attack_set --label before` against the service as it stood after Milestone 1, with no fixes. Full output is in `results/attack_run_2026-11-10_0813_before.md`.

How I marked them. **Evasion** and AI-text **prompt injection** hold only if the text still gets the AI label. Moving AI text into `unsure` counts as broke, because the writer no longer gets flagged. **False positive** holds only if real human writing is *not* labelled AI. **Malformed** holds if the service refuses it, or answers without a crash and without a confident label it has no business giving. **Flood** holds if the limit fires and the rejections are logged.

| Family | Attacks | Held | Broke |
|---|---|---|---|
| evasion | 10 | 4 | 6 |
| false_positive | 8 | 1 | 7 |
| prompt_injection | 6 | 3 | 3 |
| malformed (text) | 8 | 5 | 3 |
| malformed (request) | 12 | 10 | 2 |
| flood_same_creator | 12 | 12 | 0 |
| **Total** | **56** | **35** | **21** |

| ID | Family | Targeting | Status | Guess | Score | Verdict | What happened |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | unsure | 0.567 | **BROKE** | AI text escaped the AI label (unsure) |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | unsure | 0.560 | **BROKE** | AI text escaped the AI label (unsure) |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | ai | 0.673 | **HELD** | still labelled AI |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | ai | 0.792 | **HELD** | still labelled AI |
| EV05 | evasion | both signals: heavy human editing pass | 200 | unsure | 0.418 | **BROKE** | AI text landed near the human line (0.418) |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | unsure | 0.529 | **BROKE** | AI text escaped the AI label (unsure) |
| EV07 | evasion | signal two: padding with punctuation | 200 | unsure | 0.418 | **BROKE** | AI text escaped the AI label (0.418) |
| EV08 | evasion | signal one: text below the token window | 200 | unsure | 0.600 | **BROKE** | too short to judge, so unsure |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | ai | 0.741 | **HELD** | still labelled AI |
| EV10 | evasion | signal two: repeated stanza structure | 200 | ai | 0.951 | **HELD** | still labelled AI |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | ai | 0.743 | **BROKE** | human writing labelled AI |
| FP02 | false_positive | human writing in a formal register | 200 | ai | 0.869 | **BROKE** | human writing labelled AI |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | ai | 0.891 | **BROKE** | non-native writer labelled AI at 0.891 |
| FP04 | false_positive | a student essay written to a rubric | 200 | ai | 0.889 | **BROKE** | human writing labelled AI |
| FP05 | false_positive | technical documentation written by a person | 200 | ai | 0.900 | **BROKE** | human writing labelled AI |
| FP06 | false_positive | a person imitating a formal template | 200 | ai | 0.849 | **BROKE** | human writing labelled AI |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | ai | 0.750 | **BROKE** | human writing labelled AI |
| FP08 | false_positive | very short genuine human submission | 200 | unsure | 0.600 | **HELD** | unsure, not accused |
| PI01 | prompt_injection | instruction to ignore the check | 200 | unsure | 0.580 | **BROKE** | AI text moved from AI to unsure |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | unsure | 0.416 | **BROKE** | AI text moved from AI to unsure |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | ai | 0.711 | **HELD** | still labelled AI |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | unsure | 0.575 | **HELD** | label is a fixed string; nothing echoed |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | unsure | 0.499 | **HELD** | fake fields stayed inside the text; log entry intact |
| PI06 | prompt_injection | instruction plus real human text | 200 | ai | 0.719 | **BROKE** | the human part got labelled AI |
| MF01 | malformed | text is only whitespace | 400 | — | — | **HELD** | 400, logged |
| MF02 | malformed | text is a single character | 400 | — | — | **HELD** | 400, logged |
| MF03 | malformed | text is control characters | 200 | unsure | 0.375 | **HELD** | no crash, unsure |
| MF04 | malformed | text is only punctuation | 200 | human | 0.256 | **BROKE** | punctuation labelled human |
| MF05 | malformed | text is a very long single word | 200 | ai | 0.874 | **BROKE** | one repeated letter labelled AI at 0.874 |
| MF06 | malformed | text is emoji only | 200 | unsure | 0.600 | **HELD** | no crash, unsure |
| MF07 | malformed | text is right-to-left script | 200 | unsure | 0.600 | **HELD** | no crash, unsure |
| MF08 | malformed | text is 60,000 characters | 200 | ai | 0.940 | **BROKE** | 60k chars accepted; human text labelled AI at 0.940 |
| RQ01 | malformed | no text field at all | 400 | — | — | **HELD** | 400, logged |
| RQ02 | malformed | no creator_id | 200 | unsure | 0.495 | **HELD** | scored as `unknown` |
| RQ03 | malformed | text is a number | 400 | — | — | **HELD** | 400, logged |
| RQ04 | malformed | text is a list | 400 | — | — | **HELD** | 400, logged |
| RQ05 | malformed | text is null | 400 | — | — | **HELD** | 400, logged |
| RQ06 | malformed | creator_id is an object | 200 | unsure | 0.400 | **BROKE** | object written into the log as creator_id |
| RQ07 | malformed | body is a JSON array, not an object | 500 | — | — | **BROKE** | 500 crash, no log entry |
| RQ08 | malformed | body is unparseable JSON | 400 | — | — | **HELD** | 400, logged |
| RQ09 | malformed | body is empty | 400 | — | — | **HELD** | 400, logged |
| RQ10 | malformed | body is form-encoded, not JSON | 429 | — | — | **HELD** | 429 by IP; never reached the route |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | — | — | **HELD** | 429 by IP; never reached the route |
| RQ12 | malformed | deeply nested JSON | 400 | — | — | **HELD** | 400, logged |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | unsure | 0.389 | **HELD** | limit not reached |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | unsure | 0.389 | **HELD** | limit not reached |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | unsure | 0.389 | **HELD** | limit not reached |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | unsure | 0.389 | **HELD** | limit not reached |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | unsure | 0.389 | **HELD** | limit not reached |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | **HELD** | 429, logged |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | **HELD** | 429, logged |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | **HELD** | 429, logged |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | **HELD** | 429, logged |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | **HELD** | 429, logged |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | **HELD** | 429, logged |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | **HELD** | 429, logged |

What stands out:

- **False positives are the biggest hole.** 7 of 8 pieces of genuine human writing were labelled AI, all with combined scores between 0.74 and 0.90. In every case both signals were high: style above 0.86 and model score above 0.6. Plain, formal, rubric-shaped or careful second-language writing reads to both signals as "predictable and even".
- **Evasion mostly worked against signal one.** EV01 (typos) dropped the model score to 0.16 while style stayed at 0.97. The disagreement rule then capped the result at unsure, so a handful of typos was enough to escape the AI label.
- **The prompt injections didn't work as instructions.** Nothing in the pipeline reads the text as instructions. But PI01 and PI02 still moved AI text into unsure, just by adding unusual words that lowered signal one. PI04 and PI05 (hostile label, fake JSON fields) held: the label is a fixed string, and `json.dumps` escapes the fake fields so they stay inside the text.
- **Junk gets confident labels.** A line of punctuation (MF04) was called human at 0.256, and 4,000 copies of the letter `a` (MF05) were called AI at 0.874. The route only rejects text that is empty or under 3 tokens.
- **MF08, 60,000 characters, was accepted.** It was scored on its first 400 tokens only, and the repeated human camping text came back AI at 0.940.
- **RQ07, a JSON array as the body, crashed the route with a 500.** `request.get_json(silent=True) or {}` returns the list, and `.get` on a list raises. It's also the one request that left **no audit entry**, so it shows up only as an absence.
- **RQ06, `creator_id` as an object, was scored, and the object was written into the log** as the creator_id.
- **The rate limit held.** FL01 got 5 through and then 7 × 429, each one logged. RQ10 and RQ11 also came back 429. They have no usable creator_id, so they counted against my IP address, which the earlier creator-less malformed rows had already used up. Those two never reached the route.

**Ten audit log entries from the run**

From `logs/audit.jsonl` (`GET /log`), one entry per line, chosen for the failures, plus two rejections:

```json
{"timestamp": "2026-11-10T02:43:40+00:00", "content_id": "c_be1e1ccf66b0", "creator_id": "attacker_FP03", "guess": "ai", "model_score": 0.8051, "style_score": 0.9765, "combined_score": 0.8908, "label": "Our checks suggest this was probably written with AI. Automated checks can be wrong, and they are wrong more often about plain, simple writing. If you wrote this yourself, you can ask for a person to review it.", "status": "decided"}
{"timestamp": "2026-11-10T02:43:40+00:00", "content_id": "c_fc04b13bfc5b", "creator_id": "attacker_FP01", "guess": "ai", "model_score": 0.6175, "style_score": 0.8687, "combined_score": 0.7431, "label": "Our checks suggest this was probably written with AI. Automated checks can be wrong, and they are wrong more often about plain, simple writing. If you wrote this yourself, you can ask for a person to review it.", "status": "decided"}
{"timestamp": "2026-11-10T02:43:42+00:00", "content_id": "c_1acedc3e47ed", "creator_id": "attacker_MF08", "guess": "ai", "model_score": 0.9876, "style_score": 0.8932, "combined_score": 0.9404, "label": "Our checks suggest this was probably written with AI. Automated checks can be wrong, and they are wrong more often about plain, simple writing. If you wrote this yourself, you can ask for a person to review it.", "status": "decided"}
{"timestamp": "2026-11-10T02:43:41+00:00", "content_id": "c_7ffcba54eb0b", "creator_id": "attacker_PI06", "guess": "ai", "model_score": 0.5583, "style_score": 0.8788, "combined_score": 0.7186, "label": "Our checks suggest this was probably written with AI. Automated checks can be wrong, and they are wrong more often about plain, simple writing. If you wrote this yourself, you can ask for a person to review it.", "status": "decided"}
{"timestamp": "2026-11-10T02:43:40+00:00", "content_id": "c_0e979c3ae1db", "creator_id": "attacker_PI02", "guess": "unsure", "model_score": 0.2044, "style_score": 0.6268, "combined_score": 0.4156, "label": "We can't tell from the writing alone whether this was written by a person or with help from AI. That happens often, especially with short or plainly written pieces, and it isn't a judgement about the writer.", "status": "decided"}
{"timestamp": "2026-11-10T02:43:39+00:00", "content_id": "c_b0ecd6c9b70b", "creator_id": "attacker_EV01", "guess": "unsure", "model_score": 0.1635, "style_score": 0.9706, "combined_score": 0.5671, "label": "We can't tell from the writing alone whether this was written by a person or with help from AI. That happens often, especially with short or plainly written pieces, and it isn't a judgement about the writer.", "status": "decided"}
{"timestamp": "2026-11-10T02:43:41+00:00", "content_id": "c_6b1f79b52c0d", "creator_id": "attacker_MF05", "guess": "ai", "model_score": 0.9976, "style_score": 0.75, "combined_score": 0.8738, "label": "Our checks suggest this was probably written with AI. Automated checks can be wrong, and they are wrong more often about plain, simple writing. If you wrote this yourself, you can ask for a person to review it.", "status": "decided"}
{"timestamp": "2026-11-10T02:43:41+00:00", "content_id": "c_6964099ba389", "creator_id": "attacker_MF04", "guess": "human", "model_score": 0.0112, "style_score": 0.5, "combined_score": 0.2556, "label": "This reads like it was written by a person.", "status": "decided"}
{"timestamp": "2026-11-10T02:43:42+00:00", "content_id": "c_4d3f95c0156c", "creator_id": {"id": "x"}, "guess": "unsure", "model_score": 0.0492, "style_score": 0.75, "combined_score": 0.3996, "label": "We can't tell from the writing alone whether this was written by a person or with help from AI. That happens often, especially with short or plainly written pieces, and it isn't a judgement about the writer.", "status": "decided"}
{"timestamp": "2026-11-10T02:43:42+00:00", "content_id": "c_66810e6bfde3", "creator_id": "attacker_flood", "guess": "unsure", "model_score": 0.0287, "style_score": 0.75, "combined_score": 0.3893, "label": "We can't tell from the writing alone whether this was written by a person or with help from AI. That happens often, especially with short or plainly written pieces, and it isn't a judgement about the writer.", "status": "decided"}
{"timestamp": "2026-11-10T02:43:42+00:00", "creator_id": "unknown", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "5 per 1 minute"}
```

In order: FP03, FP01, MF08 and PI06 are human writing labelled AI. PI02 and EV01 are AI text that escaped. MF05 and MF04 are junk given confident labels. RQ06 has an object as its creator_id. The last two are 429s, one from the flood rows and one from a creator-less request counted by IP. RQ07's 500 isn't here because it never wrote anything.

**The single worst outcome**: the one I'd least want to explain to a writer whose work got caught by it.

**FP03, a non-native English speaker writing carefully about their first month in a new country, labelled AI at 0.891.** That's the highest-confidence false accusation in the run. Both signals agreed (model 0.805, style 0.977), so the disagreement rule that was meant to protect people couldn't step in. Their writing scored as machine-like for exactly the reasons a second-language writer writes the way they do: short, regular sentences, common words, and no risks. The label does tell them they can appeal, but they'd be appealing against a system that is most confident about them precisely because of how they learned the language.

---

## Run Log and Verdicts

Criteria 1, 2, 3 and 5 were run with `python run_eval.py --label before`; their inputs are in `scenarios.py`. `run_eval.py` can only call `/submit`, so criterion 4 (the appeal path) and the `/ping` half of criterion 5 were run with `python run_appeal_eval.py --label before`, a script I added. It submits, appeals the content_id that came back, and reads `/log` to check. Both ran three trials back to back with nothing changed in between. Raw output: `results/run_2026-11-10_1027_before.md` and `results/appeal_run_2026-11-10_1027_before.md`.

All three trials came out identical, to four decimal places. Neither signal has any randomness in it, so this is what a stable result looks like.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. My own writing flagged as AI | 0 of 10 labelled AI | 7/10 | 7/10 | 7/10 | **MISSED** |
| 2. Score spread, AI set vs human set | gap ≥ 0.30 | 0.179 | 0.179 | 0.179 | **MISSED** |
| 3. All three labels reachable | 3 of 3 labels, every trial | 3/3 | 3/3 | 3/3 | **MET** |
| 4. Appeal always recorded; fake id gets 404 | 5 of 5 + 404, log unchanged | 5/5 + 404 | 5/5 + 404 | 5/5 + 404 | **MET** |
| 5. Bad input gets 4xx with an error field, never 500; `/ping` still answers | 3 of 3 + ping 200 | 3/3 | 3/3 | 3/3, ping 200 | **MET** |

- **Criterion 1.** Seven of my ten pieces got the AI label, with scores from 0.686 to 0.826. The other three (plain_human, formal_human, and the Ramayan movie paragraph) landed in unsure. None got the human label. All ten have a style score of 0.586 or higher, and six are above 0.79.
- **Criterion 2.** The AI set averaged **0.786** and the human set **0.607**, so the gap is 0.179. The human set's average is dragged up by my own pieces: the staff's clearly_human sample scored 0.231, but my four scored 0.610 to 0.793.
- **Criterion 3.** Every trial got ai, ai, human, unsure, unsure, ai. The one human label came from the staff's clearly_human sample. `lightly_edited_ai` (meant as a borderline input) was labelled AI at 0.670.

**Real output from trial 1 of each criterion**

Criterion 1, from `run_eval.py::main`, scenario `c1 my own writing` in `scenarios.py`. These are the first 4 of 10 entries; all 10 are in the results file. The `label` text is left out here for length.

```json
[
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6009,
    "model_score": 0.6159,
    "style_score": 0.586,
    "sent": "India is amazing. Everyone should visit atleast once. It has such diff"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4469,
    "model_score": 0.2681,
    "style_score": 0.6257,
    "sent": "The company invested heavily in exposing micro-services as MCP servers"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.6857,
    "model_score": 0.5142,
    "style_score": 0.8572,
    "sent": "I love pottery. I picked it up last year."
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.7928,
    "model_score": 0.7934,
    "style_score": 0.7922,
    "sent": "Meditation has been of great help to me. I started doing it regularly "
  }
]
```

Criterion 2, from `run_eval.py::main`, scenarios `c2 spread: AI set` and `c2 spread: human set`. Average 0.7862 vs 0.6074:

```json
{
  "ai_set": [
    {
      "status": 200,
      "guess": "ai",
      "confidence": 0.7925,
      "model_score": 0.7544,
      "style_score": 0.8307,
      "sent": "The importance of effective time management cannot be overstated in to"
    },
    {
      "status": 200,
      "guess": "ai",
      "confidence": 0.895,
      "model_score": 0.9194,
      "style_score": 0.8706,
      "sent": "Regular physical activity offers a wide range of benefits for both phy"
    },
    {
      "status": 200,
      "guess": "ai",
      "confidence": 0.709,
      "model_score": 0.7019,
      "style_score": 0.7161,
      "sent": "Remote work has fundamentally transformed the modern workplace. Organi"
    },
    {
      "status": 200,
      "guess": "ai",
      "confidence": 0.7913,
      "model_score": 0.9416,
      "style_score": 0.6411,
      "sent": "Climate change is one of the most pressing challenges facing humanity "
    },
    {
      "status": 200,
      "guess": "ai",
      "confidence": 0.7434,
      "model_score": 0.731,
      "style_score": 0.7558,
      "sent": "Reading is a valuable habit that offers numerous cognitive and emotion"
    }
  ],
  "human_set": [
    {
      "status": 200,
      "guess": "human",
      "confidence": 0.2306,
      "model_score": 0.4445,
      "style_score": 0.0167,
      "sent": "I didn't sleep. Not properly, anyway — I lay there listening to the bo"
    },
    {
      "status": 200,
      "guess": "ai",
      "confidence": 0.6857,
      "model_score": 0.5142,
      "style_score": 0.8572,
      "sent": "I love pottery. I picked it up last year."
    },
    {
      "status": 200,
      "guess": "ai",
      "confidence": 0.7928,
      "model_score": 0.7934,
      "style_score": 0.7922,
      "sent": "Meditation has been of great help to me. I started doing it regularly "
    },
    {
      "status": 200,
      "guess": "unsure",
      "confidence": 0.6095,
      "model_score": 0.6046,
      "style_score": 0.6143,
      "sent": "I watched Ramayan movie yesterday with family. It was the best movie I"
    },
    {
      "status": 200,
      "guess": "ai",
      "confidence": 0.7183,
      "model_score": 0.5926,
      "style_score": 0.844,
      "sent": "I was working in the US at a big tech company. I recently joined a mic"
    }
  ]
}
```

Criterion 3, from `run_eval.py::main`, scenario `c3 label coverage`:

```json
[
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.7925,
    "model_score": 0.7544,
    "style_score": 0.8307,
    "sent": "The importance of effective time management cannot be overstated in to"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.895,
    "model_score": 0.9194,
    "style_score": 0.8706,
    "sent": "Regular physical activity offers a wide range of benefits for both phy"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.2306,
    "model_score": 0.4445,
    "style_score": 0.0167,
    "sent": "I didn't sleep. Not properly, anyway — I lay there listening to the bo"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6009,
    "model_score": 0.6159,
    "style_score": 0.586,
    "sent": "India is amazing. Everyone should visit atleast once. It has such diff"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4401,
    "model_score": 0.3489,
    "style_score": 0.5314,
    "sent": "Time management matters more than people admit, especially now that wo"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.6702,
    "model_score": 0.5813,
    "style_score": 0.7591,
    "sent": "Time management matters a lot in todays fast-paced work environment. P"
  }
]
```

Criterion 4, from `run_appeal_eval.py::run_trial`. One appeal from trial 1 (all 5 look the same), then the fake id:

```json
{
  "appeal": {
    "content_id": "c_a7256a8dab28",
    "submit_status": 200,
    "appeal_status": 200,
    "appeal_response": {
      "content_id": "c_a7256a8dab28",
      "message": "Thanks. Your appeal has been recorded and this piece is now waiting for a person to review it.",
      "original_guess": "unsure",
      "status": "under_review"
    },
    "log_entry": {
      "content_id": "c_a7256a8dab28",
      "creator_id": "eval_appeal_t1_1_ca3e31",
      "event": "appeal",
      "reasoning": "I wrote this myself, on 2026-11-10. Eval trial 1, piece 1.",
      "status": "under_review",
      "timestamp": "2026-11-10T04:57:43+00:00"
    },
    "pass": true
  },
  "fake_id": {
    "content_id": "c_doesnotexist1",
    "status": 404,
    "response": {
      "error": "not_found",
      "message": "No submission with content_id 'c_doesnotexist1'. Check the id from your /submit response."
    },
    "log_count_before": 257,
    "log_count_after": 257,
    "pass": true
  }
}
```

Criterion 5, from `run_eval.py::main`, scenario `c5 bad input`, then `/ping` from `run_appeal_eval.py::main`:

```json
{
  "bad_input": [
    {
      "status": 400,
      "error": "bad_request",
      "sent": "(empty text)"
    },
    {
      "status": 400,
      "error": "bad_request",
      "sent": "{\"creator_id\": \"eval_bad_missing\"}"
    },
    {
      "status": 400,
      "error": "bad_request",
      "sent": "{\"text\": null, \"creator_id\": \"eval_bad_null\"}"
    }
  ],
  "ping_afterwards": {
    "status": 200,
    "body": {
      "ok": true,
      "service": "provenance-guard",
      "you_sent": "still alive?"
    }
  }
}
```

**Verdicts against the unit 7 targets**

- **Criterion 1, false positives: MISSED.** The target was that none of my 10 pieces gets the AI label in any trial. 7 of 10 got it in every trial.
- **Criterion 2, score spread: MISSED.** The target was a gap of 0.30 or more. The gap was 0.179 in every trial.
- **Criterion 3, label coverage: MET.** All three labels appeared in every trial.
- **Criterion 4, appeal path: MET.** 5 of 5 appeals were recorded and the fake id got a 404, in every trial.
- **Criterion 5, bad input: MET.** 3 of 3 bad inputs got a 400 with an error field, and `/ping` answered afterwards.

**Diagnoses**

The two misses and the 21 broken attacks come down to **five problems**, not 23. To get these numbers I re-ran every failing input through `stylometry.py` and `detector.py` and recorded what each part of each signal measured. "Spread" is sentence-length spread and "punct" is punctuation density; both are part of signal two.

**Pattern A: plain human writing reads as AI to *both* signals, so the disagreement rule never fires.**
*Covers criterion 1, criterion 2, FP01–FP07 and PI06 (10 failures).*
*Stages: signal two (main), signal one, and the combining rule.*

- **Signal two.** Its punctuation measure counts commas, dashes, semicolons, colons and so on per word, and treats *less* punctuation as more AI. Plain human writing mostly uses full stops, which the measure skips. FP01–FP07 averaged 0.018 marks per word, and FP03 had none at all. That is below the 0.03 "AI end", so this half of signal two maxed out at 0.96–1.00 on all seven. My AI-labelled pieces scored the same: 0.76–1.00.
- **The AI text did the opposite.** My five generated AI paragraphs averaged 0.067 marks per word, nearly four times as much, so they scored *less* AI-like on punctuation (0.28–0.85).
- **Why the measure points the wrong way.** I set its anchors from calibration inputs where the "human" example was the staff's voicey paragraph, full of dashes and colons. For plain writers it runs backwards, the same failure I'd already found in type-token ratio and gave zero weight.
- **Sentence spread.** Plain writing in short, even sentences scored spreads of 0.24–0.52 on FP02–FP06, which is close to the 0.30 AI end. So that half of signal two adds to the problem rather than balancing it.
- **Signal one.** Common words in ordinary order are easy for GPT-2 to predict. Perplexity on FP02–FP07 was 12.8–23.5, which gives a model score of 0.74–0.88. That's the blind spot I named for signal one in unit 7.
- **The combining rule.** It caps the score at 0.60 only when *one* signal leans human (≤ 0.50). That protection assumes the two signals fail independently. On plain writing they fail *together*. Both read "plain" as "machine", so neither drops below 0.50, the cap never fires, and the average lands at 0.74–0.90. My own pieces did the same: style 0.66–0.99, model 0.51–0.81.
- **Criterion 2** is the same pattern measured as an average. The AI set scored 0.786. The human set scored 0.607 because four of its five texts were my plain pieces (0.610–0.793). The staff's voicey sample was the only one that scored low (0.231).

**Pattern B: one fooled signal is enough to escape, because of the disagreement cap.**
*Covers EV01, EV05, EV08, PI01 and PI02 (5 failures).*
*Stages: signal one, then the combining rule.*

- **Signal one is fooled by anything unusual in the text.** Typos (EV01), a heavy human edit (EV05), and odd framing tokens like "SYSTEM:" (PI02) all make the next word harder to predict. Perplexity rose to 124.8, 71.8 and 105.2, so the model score fell to 0.16, 0.32 and 0.20. EV08 (10 words) and PI01 did the same at smaller sizes.
- **Signal two wasn't fooled.** It still read EV01 as 0.97 AI. This differs from the brief's example: in my system, typos fool signal *one*, not signal two.
- **The combining rule then hands that one signal a veto.** Once either signal is ≤ 0.50, the score is capped at 0.60, inside unsure. This is the same rule that's meant to protect writers. It's built so that one signal leaning human is enough to block an AI label, and attackers only need to fool the cheaper signal. None of these reached the human label; they all stopped at unsure.

**Pattern C: signal two only measures shape, and the shape is cheap to forge.**
*Covers EV02, EV06 and EV07 (3 failures).*
*Stage: signal two.*

- **EV02** broke the AI text into short sentences ("Really."). Spread went to 0.85, so that half of the style score fell to 0.08. Combined: (0.594 + 0.53) / 2 = 0.56, which is unsure, with no cap needed.
- **EV06** added one very long and one very short sentence. Spread went to 1.19 and style to 0.49, which triggered the cap.
- **EV07** padded the text with semicolons and "moreover," until it was one sentence with 0.216 marks per word. Punctuation then scored fully human (0.00) and style fell to 0.25.

This is exactly the blind spot named in `stylometry.py`: the signal can't read, so anything that changes the shape without changing the words moves it.

**Pattern D: the route scores text that isn't writing.**
*Covers MF04, MF05 and MF08 (3 failures).*
*Stage: the route, which lets these through to the signals.*

- **MF04, punctuation only.** It has zero words. Signal two returns its "no evidence" 0.5. Signal one sees GPT-2 perplexity of 738, so the model score is 0.011, and the average of 0.256 is a *human* label.
- **MF05, 4,000 copies of `a`.** It's perfectly predictable (perplexity 1.0, model score 0.998), so it gets an *AI* label at 0.874.
- **MF08, 60,000 characters.** It was accepted, then cut to the first 400 tokens. Those tokens are the same human camping paragraph repeated, and GPT-2 predicts a repeat almost perfectly (perplexity 2.9). So human text got the AI label at 0.940.

The route checks only that `text` is a non-empty string of at least 3 tokens. It never asks whether the text contains words, or whether it's too long to score honestly.

**Pattern E: the route trusts the shape of the request body.**
*Covers RQ07 and RQ06 (2 failures).*
*Stage: the route.*

- **RQ07** sends a JSON array. `request.get_json(silent=True) or {}` returns the list, because a non-empty list is truthy. Then `payload.get("text")` raises `AttributeError`, and Flask returns a 500.
- **RQ07 also left nothing in the audit log**, because the crash happens before any `log_rejection` call. The worst kind of failure here is one that shows up only as an absence.
- **RQ06** sends `creator_id` as an object. The route never checks its type, so `{"id": "x"}` was written into the audit log as a creator_id, and the rate limiter fell back to counting by IP address for it.

**The pattern that matters most is A.** Patterns B, C and D are ways AI text or junk gets the wrong label. Pattern A is the one that accuses real people: 7 of 8 human attack pieces and 7 of my own 10. Its root is in signal two. Its punctuation measure points the wrong way for plain writers, and that turns signal two into a second copy of signal one's blind spot, when it should be a check on it.

**Criteria I'd tighten, even though they were met**

- **Criterion 5 was too easy.** It covered only empty, missing and null `text`, and the attack set found a 500 (RQ07) with a body shape it never tried. Next time it should include non-object bodies, wrong types for `creator_id`, and an oversized `text`.
- **Criterion 3 was met only through the staff sample.** None of my own writing reached the human label. It technically shows the label is reachable, but not reachable by the writers it's meant for.

I'm not revising either criterion in `criteria.md`. Both were measurable, so neither counts as broken.

---

## The Improvement

**What I changed:** I dropped **punctuation density** from signal two, taking its weight from 0.5 to **0**. Signal two is now sentence-length spread alone, using the same 0.90 → 0 and 0.30 → 1 anchors. Punctuation density is still computed, the same way type-token ratio already was, but it no longer counts.

It's one change, in `stylometry.py::style_signal`. Nothing in `config.py`, `scoring.py` or `app.py` changed. All the after runs went against the same service, restarted with only this edit.

**Which diagnosis pointed at it:** Pattern A. Punctuation density treated *less* punctuation as more AI-like. That's backwards for plain human writing, which uses almost nothing but full stops:

- The false-positive attacks averaged 0.018 marks per word, and the AI text I generated averaged 0.067.
- The measure maxed out at "AI" (0.96–1.00) on all 7 false-positive attacks.
- On my own writing it was 0.76–1.00 for every piece labelled AI.

It was the one part of the system that actively pointed the wrong way, and I had already zeroed type-token ratio for the same reason. So this is the same fix applied consistently, not a new idea.

Before choosing it, I simulated three options offline on the inputs I'd already scored, with nothing sent to the service:

- **No change.** This is the before-run.
- **Punctuation at weight 0.** This is what I did.
- **Punctuation fixed at a neutral 0.5.**

The simulation predicted what the real re-run then showed: this fixes less than the diagnosis implied, because **signal one also reads plain writing as AI**. That's in the results below.

### Attack Run — After

`python run_attacks.py --set attack_set --label after`. Full output: `results/attack_run_2026-11-10_1048_after.md`. Same marking rules as the before-run.

**Before and after, side by side**

| Family | Before: held / broke | After: held / broke |
|---|---|---|
| evasion | 4 / 6 | 4 / 6, but **3 now reach the human label** |
| false_positive | 1 / 7 | **2 / 6** |
| prompt_injection | 3 / 3 | 3 / 3 |
| malformed (text) | 5 / 3 | 5 / 3 (MF05 fixed, MF03 newly broke) |
| malformed (request) | 10 / 2 | 10 / 2 |
| flood_same_creator | 12 / 0 | 12 / 0 |
| **Total** | **35 / 21** | **36 / 20** |

| Criterion | Target | Before (runs 1/2/3) | After (runs 1/2/3) | Before → After |
|---|---|---|---|---|
| 1. My own writing flagged as AI | 0 of 10 | 7/10 · 7/10 · 7/10 | 6/10 · 6/10 · 6/10 | MISSED → **MISSED** |
| 2. Score spread, AI vs human | gap ≥ 0.30 | 0.179 · 0.179 · 0.179 | 0.311 · 0.311 · 0.311 | MISSED → **MET** |
| 3. All three labels reachable | 3 of 3 | 3/3 · 3/3 · 3/3 | 3/3 · 3/3 · 3/3 | MET → **MET** |
| 4. Appeal recorded; fake id 404 | 5/5 + 404 | 5/5 + 404 ×3 | 5/5 + 404 ×3 | MET → **MET** |
| 5. Bad input 4xx, never 500; `/ping` ok | 3/3 + 200 | 3/3 ×3, ping 200 | 3/3 ×3, ping 200 | MET → **MET** |

**Every attack, after**

| ID | Family | Status | Guess | Score | Verdict | Change from before |
|---|---|---|---|---|---|---|
| EV01 | evasion | 200 | unsure | 0.582 | **BROKE** | still unsure |
| EV02 | evasion | 200 | human | 0.340 | **BROKE** | AI text now labelled **human** |
| EV03 | evasion | 200 | ai | 0.714 | **HELD** | still labelled AI |
| EV04 | evasion | 200 | ai | 0.806 | **HELD** | still labelled AI |
| EV05 | evasion | 200 | human | 0.348 | **BROKE** | AI text now labelled **human** |
| EV06 | evasion | 200 | human | 0.286 | **BROKE** | AI text now labelled **human** |
| EV07 | evasion | 200 | unsure | 0.543 | **BROKE** | still unsure |
| EV08 | evasion | 200 | unsure | 0.600 | **BROKE** | still unsure |
| EV09 | evasion | 200 | ai | 0.713 | **HELD** | still labelled AI |
| EV10 | evasion | 200 | ai | 0.911 | **HELD** | still labelled AI |
| FP01 | false_positive | 200 | ai | 0.677 | **BROKE** | still AI, 0.743 → 0.677 |
| FP02 | false_positive | 200 | ai | 0.869 | **BROKE** | still AI, unchanged |
| FP03 | false_positive | 200 | ai | 0.879 | **BROKE** | still AI, 0.891 → 0.879 |
| FP04 | false_positive | 200 | ai | 0.861 | **BROKE** | still AI |
| FP05 | false_positive | 200 | ai | 0.900 | **BROKE** | still AI, unchanged |
| FP06 | false_positive | 200 | ai | 0.758 | **BROKE** | still AI, 0.849 → 0.758 |
| FP07 | false_positive | 200 | unsure | 0.582 | **HELD** | **fixed**: AI → unsure |
| FP08 | false_positive | 200 | unsure | 0.550 | **HELD** | unsure, not accused |
| PI01 | prompt_injection | 200 | unsure | 0.429 | **BROKE** | still unsure |
| PI02 | prompt_injection | 200 | human | 0.309 | **BROKE** | AI text now labelled **human** |
| PI03 | prompt_injection | 200 | ai | 0.761 | **HELD** | still labelled AI |
| PI04 | prompt_injection | 200 | unsure | 0.600 | **HELD** | label is a fixed string; nothing echoed |
| PI05 | prompt_injection | 200 | ai | 0.677 | **HELD** | now labelled AI; log entry intact |
| PI06 | prompt_injection | 200 | ai | 0.658 | **BROKE** | still AI, 0.719 → 0.658 |
| MF01 | malformed | 400 | — | — | **HELD** | 400, logged |
| MF02 | malformed | 400 | — | — | **HELD** | 400, logged |
| MF03 | malformed | 200 | human | 0.250 | **BROKE** | control characters now labelled **human** |
| MF04 | malformed | 200 | human | 0.256 | **BROKE** | punctuation labelled human |
| MF05 | malformed | 200 | unsure | 0.600 | **HELD** | **fixed**: AI → unsure |
| MF06 | malformed | 200 | unsure | 0.600 | **HELD** | no crash, unsure |
| MF07 | malformed | 200 | unsure | 0.600 | **HELD** | no crash, unsure |
| MF08 | malformed | 200 | ai | 0.887 | **BROKE** | still AI, 0.940 → 0.887 |
| RQ01 | malformed | 400 | — | — | **HELD** | 400, logged |
| RQ02 | malformed | 200 | unsure | 0.370 | **HELD** | scored as `unknown` |
| RQ03 | malformed | 400 | — | — | **HELD** | 400, logged |
| RQ04 | malformed | 400 | — | — | **HELD** | 400, logged |
| RQ05 | malformed | 400 | — | — | **HELD** | 400, logged |
| RQ06 | malformed | 200 | human | 0.275 | **BROKE** | still accepted; now labelled human |
| RQ07 | malformed | 500 | — | — | **BROKE** | still 500, no log entry |
| RQ08 | malformed | 400 | — | — | **HELD** | 400, logged |
| RQ09 | malformed | 400 | — | — | **HELD** | 400, logged |
| RQ10 | malformed | 429 | — | — | **HELD** | 429 by IP; never reached the route |
| RQ11 | malformed | 429 | — | — | **HELD** | 429 by IP; never reached the route |
| RQ12 | malformed | 400 | — | — | **HELD** | 400, logged |
| FL01_01 | flood_same_creator | 200 | human | 0.264 | **HELD** | limit not reached |
| FL01_02 | flood_same_creator | 200 | human | 0.264 | **HELD** | limit not reached |
| FL01_03 | flood_same_creator | 200 | human | 0.264 | **HELD** | limit not reached |
| FL01_04 | flood_same_creator | 200 | human | 0.264 | **HELD** | limit not reached |
| FL01_05 | flood_same_creator | 200 | human | 0.264 | **HELD** | limit not reached |
| FL01_06 | flood_same_creator | 429 | — | — | **HELD** | 429, logged |
| FL01_07 | flood_same_creator | 429 | — | — | **HELD** | 429, logged |
| FL01_08 | flood_same_creator | 429 | — | — | **HELD** | 429, logged |
| FL01_09 | flood_same_creator | 429 | — | — | **HELD** | 429, logged |
| FL01_10 | flood_same_creator | 429 | — | — | **HELD** | 429, logged |
| FL01_11 | flood_same_creator | 429 | — | — | **HELD** | 429, logged |
| FL01_12 | flood_same_creator | 429 | — | — | **HELD** | 429, logged |

**Run log — after**

`python run_eval.py --label after` and `python run_appeal_eval.py --label after`. Raw output: `results/run_2026-11-10_1048_after.md` and `results/appeal_run_2026-11-10_1048_after.md`. All three trials were again identical.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. My own writing flagged as AI | 0 of 10 labelled AI | 6/10 | 6/10 | 6/10 | **MISSED** |
| 2. Score spread, AI set vs human set | gap ≥ 0.30 | 0.311 | 0.311 | 0.311 | **MET** |
| 3. All three labels reachable | 3 of 3 labels, every trial | 3/3 | 3/3 | 3/3 | **MET** |
| 4. Appeal always recorded; fake id gets 404 | 5 of 5 + 404, log unchanged | 5/5 + 404 | 5/5 + 404 | 5/5 + 404 | **MET** |
| 5. Bad input gets 4xx with an error field, never 500; `/ping` still answers | 3 of 3 + ping 200 | 3/3 | 3/3 | 3/3, ping 200 | **MET** |

Real output from trial 1. Criterion 1, from `run_eval.py::main`, scenario `c1 my own writing`. These are the first 4 of 10 entries; piece 3, the pottery paragraph, moved from AI (0.686) to unsure (0.614):

```json
[
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.394,
    "model_score": 0.6159,
    "style_score": 0.172,
    "sent": "India is amazing. Everyone should visit atleast once. It has such diff"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4764,
    "model_score": 0.2681,
    "style_score": 0.6848,
    "sent": "The company invested heavily in exposing micro-services as MCP servers"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6142,
    "model_score": 0.5142,
    "style_score": 0.7143,
    "sent": "I love pottery. I picked it up last year."
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.7539,
    "model_score": 0.7934,
    "style_score": 0.7143,
    "sent": "Meditation has been of great help to me. I started doing it regularly "
  }
]
```

Criterion 2, from `run_eval.py::main`. Average 0.8759 vs 0.565, a gap of 0.311:

```json
{
  "ai_set": [
    {
      "status": 200,
      "guess": "ai",
      "confidence": 0.783,
      "model_score": 0.7544,
      "style_score": 0.8115,
      "sent": "The importance of effective time management cannot be overstated in to"
    },
    {
      "status": 200,
      "guess": "ai",
      "confidence": 0.9597,
      "model_score": 0.9194,
      "style_score": 1.0,
      "sent": "Regular physical activity offers a wide range of benefits for both phy"
    },
    {
      "status": 200,
      "guess": "ai",
      "confidence": 0.8509,
      "model_score": 0.7019,
      "style_score": 1.0,
      "sent": "Remote work has fundamentally transformed the modern workplace. Organi"
    },
    {
      "status": 200,
      "guess": "ai",
      "confidence": 0.9708,
      "model_score": 0.9416,
      "style_score": 1.0,
      "sent": "Climate change is one of the most pressing challenges facing humanity "
    },
    {
      "status": 200,
      "guess": "ai",
      "confidence": 0.8152,
      "model_score": 0.731,
      "style_score": 0.8993,
      "sent": "Reading is a valuable habit that offers numerous cognitive and emotion"
    }
  ],
  "human_set": [
    {
      "status": 200,
      "guess": "human",
      "confidence": 0.2223,
      "model_score": 0.4445,
      "style_score": 0.0,
      "sent": "I didn't sleep. Not properly, anyway — I lay there listening to the bo"
    },
    {
      "status": 200,
      "guess": "unsure",
      "confidence": 0.6142,
      "model_score": 0.5142,
      "style_score": 0.7143,
      "sent": "I love pottery. I picked it up last year."
    },
    {
      "status": 200,
      "guess": "ai",
      "confidence": 0.7539,
      "model_score": 0.7934,
      "style_score": 0.7143,
      "sent": "Meditation has been of great help to me. I started doing it regularly "
    },
    {
      "status": 200,
      "guess": "unsure",
      "confidence": 0.5727,
      "model_score": 0.6046,
      "style_score": 0.5408,
      "sent": "I watched Ramayan movie yesterday with family. It was the best movie I"
    },
    {
      "status": 200,
      "guess": "ai",
      "confidence": 0.662,
      "model_score": 0.5926,
      "style_score": 0.7313,
      "sent": "I was working in the US at a big tech company. I recently joined a mic"
    }
  ]
}
```

Criterion 3, from `run_eval.py::main`:

```json
[
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.783,
    "model_score": 0.7544,
    "style_score": 0.8115,
    "sent": "The importance of effective time management cannot be overstated in to"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.9597,
    "model_score": 0.9194,
    "style_score": 1.0,
    "sent": "Regular physical activity offers a wide range of benefits for both phy"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.2223,
    "model_score": 0.4445,
    "style_score": 0.0,
    "sent": "I didn't sleep. Not properly, anyway — I lay there listening to the bo"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.394,
    "model_score": 0.6159,
    "style_score": 0.172,
    "sent": "India is amazing. Everyone should visit atleast once. It has such diff"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.537,
    "model_score": 0.3489,
    "style_score": 0.725,
    "sent": "Time management matters more than people admit, especially now that wo"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.7175,
    "model_score": 0.5813,
    "style_score": 0.8537,
    "sent": "Time management matters a lot in todays fast-paced work environment. P"
  }
]
```

Criterion 4, from `run_appeal_eval.py::run_trial`. One appeal from trial 1, then the fake id:

```json
{
  "appeal": {
    "content_id": "c_673f8b4976d2",
    "submit_status": 200,
    "appeal_status": 200,
    "appeal_response": {
      "content_id": "c_673f8b4976d2",
      "message": "Thanks. Your appeal has been recorded and this piece is now waiting for a person to review it.",
      "original_guess": "unsure",
      "status": "under_review"
    },
    "log_entry": {
      "content_id": "c_673f8b4976d2",
      "creator_id": "eval_appeal_t1_1_46ad08",
      "event": "appeal",
      "reasoning": "I wrote this myself, on 2026-11-10. Eval trial 1, piece 1.",
      "status": "under_review",
      "timestamp": "2026-11-10T05:18:13+00:00"
    },
    "pass": true
  },
  "fake_id": {
    "content_id": "c_doesnotexist1",
    "status": 404,
    "response": {
      "error": "not_found",
      "message": "No submission with content_id 'c_doesnotexist1'. Check the id from your /submit response."
    },
    "log_count_before": 374,
    "log_count_after": 374,
    "pass": true
  }
}
```

Criterion 5, from `run_eval.py::main`, then `/ping` from `run_appeal_eval.py::main`:

```json
{
  "bad_input": [
    {
      "status": 400,
      "error": "bad_request",
      "sent": "(empty text)"
    },
    {
      "status": 400,
      "error": "bad_request",
      "sent": "{\"creator_id\": \"eval_bad_missing\"}"
    },
    {
      "status": 400,
      "error": "bad_request",
      "sent": "{\"text\": null, \"creator_id\": \"eval_bad_null\"}"
    }
  ],
  "ping_afterwards": {
    "status": 200,
    "body": {
      "ok": true,
      "service": "provenance-guard",
      "you_sent": "still alive?"
    }
  }
}
```

**Did it help, and how do I know:**

**A little, and it cost something real.**

What it fixed:
- **Criterion 2 went from MISSED to MET.** The gap went from 0.179 to 0.311. The AI set rose from 0.786 to 0.876, because generated text uses commas and no longer gets credit for them. The human set fell from 0.607 to 0.565.
- **One false-positive attack was fixed.** FP07 went from AI to unsure.
- **One of my own pieces stopped being accused.** The pottery paragraph went from AI to unsure.
- **Every other false positive scored lower.** For example, FP06 went from 0.849 to 0.758 and FP01 from 0.743 to 0.677.
- **MF05** (4,000 copies of `a`) went from AI to unsure.

What it didn't fix:
- **Criterion 1 is still MISSED,** at 6 of 10.
- **Six of eight human attack pieces are still labelled AI.** That includes FP03, the non-native writer, which only went from 0.891 to 0.879, so the worst outcome is still there.

The reason is in the signal scores. For FP02–FP05, sentence spread on its own still reads plain writing as AI (style 0.89–1.00). Signal one gives them 0.74–0.83. Both signals still lean AI, so the cap still never fires. Pattern A had two causes, and I removed only the smaller one. The remaining one is signal one's blind spot, plus a spread measure that also reads short, even sentences as AI.

What it cost:
- **Signal two lost half of what it measured, and that made it easier to fool.**
- **Three evasion attacks moved from unsure to *human*.** EV02 went to 0.340, EV05 to 0.348 and EV06 to 0.286. Breaking up sentences or adding one very long and one very short sentence now moves signal two all the way to "human". Before, punctuation held it near the middle.
- **PI02 moved to human (0.309).**
- **MF03** (control characters) moved to human.
- **The evasion count stayed at 6 broke, but the breaks are worse.** Before, AI text escaped into unsure. Now three AI pieces get a confident "this reads like it was written by a person".

**Is it a good trade?** I'd keep it, on the rule I set in unit 7: wrongly calling a writer human costs the site a little, and wrongly calling them AI costs that person a lot. The change made one fewer person accused in the attack set and one fewer in my own writing, and it met criterion 2. It also let three AI texts be called human. That's the direction I said I'd rather be wrong in. But it's a small gain bought with a visible loss. The real false-positive fix has to come from signal one, or from a combining rule that doesn't trust two signals that are both fooled by plainness. One change can't do that.

---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
