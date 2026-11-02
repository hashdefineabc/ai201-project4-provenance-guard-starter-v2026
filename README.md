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

**What it measures:** The shape of the text, without reading it. Two measures count: how much sentence length varies (standard deviation ÷ mean of words per sentence) and punctuation density (commas, `; : — ( ) " ! ?` per word, full stops not counted). Each is mapped onto 0–1 AI-ness with a straight line between a human-looking and an AI-looking value, then the two are averaged. A third measure, type-token ratio (unique ÷ total words, averaged over 50-word windows), is computed but given zero weight — on my calibration inputs it pointed the wrong way: the AI text had the *most* varied vocabulary (0.92–0.96) and the plain human text the least (0.71).

**Why that might differ between human and AI writing:** AI writes even, mid-length sentences with tidy, sparse punctuation. Humans are lumpier — a two-word sentence next to a forty-word one, asides in dashes, a colon where a list starts.

**What it can't see:** Meaning. Typos, chopped-up sentences or a pasted quotation change the score without changing who wrote it. And it shares signal one's blind spot: plain writing — short, even sentences with few commas — looks *more* machine-like to it than real AI text does (my plain human paragraph scored 0.99, the clearly-AI sample 0.83).

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

**Calibration run** (both signals printed separately). The first three rows are the files in `samples/`. The formal-human, plain-human and lightly-edited-AI rows are stand-in texts written with AI help, not by a person — to be replaced with my own writing and rerun:

| Input | model | style | combined |
|---|---|---|---|
| clearly AI | 0.75 | 0.83 | 0.79 |
| clearly human | 0.45 | 0.02 | 0.23 |
| borderline | 0.35 | 0.53 | 0.44 |
| formal human | 0.53 | 0.66 | 0.60 |
| plain human | 0.85 | 0.99 | 0.92 |
| lightly-edited AI | 0.65 | 0.69 | 0.67 |

**What the rule can't fix:** the plain human paragraph scores 0.92 — higher than the real AI text. Both signals share the same blind spot, so they *agree*, and agreement is exactly when the rule lets an AI label through. No threshold separates it from clearly-AI text either, since it scores above it. This is the false-positive writer from Milestone 1, and with the current signals my criterion 1 would fail on plain writing.



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

The AI label is the one that can actually hurt someone, so it says "probably", admits the check can be wrong, names the kind of writing it gets wrong most (my own calibration showed plain human writing scoring above real AI text), and points straight to the appeal.



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

- *What I asked for:*
- *What came back:*
- *What I changed:*

**Moment 2**

- *What I asked for:*
- *What came back:*
- *What I changed:*

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** ___ per minute, ___ per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```

```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

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
