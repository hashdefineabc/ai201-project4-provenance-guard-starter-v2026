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
- Style-signal anchors (in `stylometry.style_signal`): sentence spread 0.90 → 0, 0.30 → 1; punctuation density 0.12 → 0, 0.03 → 1

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

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



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
