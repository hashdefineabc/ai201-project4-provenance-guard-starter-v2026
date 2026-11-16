# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. *"The
detector is accurate"* is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. *"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"* is a criterion.

Under each, write a sentence or two on **why that target**. *"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"* is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area | A question it could answer |
|---|---|
| False positives | How often may a human's writing get called AI? |
| Score spread | How far apart should clearly-AI and clearly-human text score? |
| Label coverage | Is every one of your three labels actually reachable? |
| The appeal path | Does an appeal always change status and always get recorded? |
| Bad input | What happens when `text` is missing, empty, or enormous? |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---
## 1. False positives

Of 10 pieces I wrote myself, atleast 3 of them deliberately plain (short sentences, common words), none gets the high-confidence AI label in any of the three trials.

**Why this target:** A wrong accusation costs a real writer far more than a missed AI text costs the site. The plain pieces are there because that's the writer the model signal is most likely to accuse.

---

## 2. Score spread
Across 5 texts I'm confident are AI and 5 I'm confident are human, the average combined score of the AI set is atleast 0.30 higher than the human set's.

**Why this target:** If the gap is smaller than the unsure band, the clear cases can't land in different labels, and the system is effectively always unsure.

---

## 3. Label coverage
Using a set of 6 inputs (2 clearly AI, 2 clearly human, 2 borderline), each of the three labels (human, ai, unsure) shows up atleast once in every trial.

**Why this target:** A label no score can reach is a gap in the ranges. "unsure" matters most because it's the safe answer for the false-positive writer.

---

## 4. The appeal path
For 5 submissions I appeal, 5 of 5 return succes, and /log shows an appeal entry with my reasoning and status under_review. An appeal with a made-up content_id returns 404 and changes nothing in the log.

**Why this target:** The appeal is the only thing between a wrong label and the writer having no recourse. If it fails silently even once, that writer is stuck.

---

## 5. Bad input
The malformed requests (empty text, missing text, text: null) each get a 4xx response with an error field. None returns a 500, and /ping still answers afterward.

**Why this target:** A crash on bad input is one of the most common real failures.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 9 — the extension

The extension is `POST /review`: a reviewer sends `content_id`, `reviewer_id`, `outcome` (`upheld` or `overturned`) and `reasoning`, and the route checks that input. It doesn't write to the audit log or change an item's status (see **Out of Scope** in the README). Criteria 1–4 are about `/review`; criterion 5 checks that adding it, and the run log, didn't change what already worked.

Each target has to hold in **all three trials**.

---

## 1. Valid reviews are accepted

Of 10 well-formed review requests (5 `upheld`, 5 `overturned`, each with a different `content_id`), 10 of 10 return 200. Each response echoes back all four fields exactly as sent (surrounding spaces trimmed), plus `"recorded": false`.

**Why this target:** There's no model in this route, only string checks, so the same input should always give the same answer. Anything short of 10/10 is a bug, not noise. A reviewer whose valid decision gets refused has no way to close the appeal, and the writer waiting on it stays stuck.

---

## 2. Bad review requests are refused, never crash (the bad path)

These 12 malformed requests each return **400** with `"error": "bad_request"` and a message naming the field at fault. None returns 200 or 500:

1. a body that isn't JSON (`hello`)
2. a JSON list
3. a JSON string (`"upheld"`)
4. `content_id` missing
5. `reviewer_id` missing
6. `outcome` missing
7. `reasoning` missing
8. `reasoning` that's only spaces
9. `content_id` given as a number
10. `reviewer_id` given as `null`
11. `outcome` of `"maybe"`
12. `outcome` of `"Upheld"` (wrong case)

**Why this target:** 12/12 and not "most", because a review is the last decision about a writer. Once reviews are logged (the next step after this unit), a malformed one that slips through becomes a permanent, wrong outcome on someone's record. Wrong case is on the list deliberately: `"Upheld"` and `"upheld"` would look like one outcome to a person but count as two to a script reading the log. A 500 is a fail even though it also refuses the request. `/submit` still crashes on a list body (RQ07), and this new route must not repeat that.

---

## 3. `/review` changes nothing it says it doesn't

After all 22 requests from criteria 1 and 2, `logs/audit.jsonl` has **0 new lines**, and `GET /log` shows the same latest status for every `content_id` used as before the run.

**Why this target:** The README promises this route records nothing yet. A route that wrote half a record, say an entry with no status change, would leave an appeal history that looks reviewed when it isn't. That's worse than a route that plainly does nothing. Zero is the only number that keeps that promise.

---

## 4. Every review attempt leaves a trace

Each of those 22 `/review` requests writes **exactly one** line to `logs/runs.jsonl`. That line has `route` set to `/review`, the same `status` the caller received, and a non-null `error` if and only if the status was 400 or above. That's 22 of 22 lines, with no missing or duplicated ones.

**Why this target:** Because of criterion 3, `runs.jsonl` is the *only* evidence a review was ever attempted. If a line is missing, a reviewer's decision vanished with no trace, and nobody could find out later that it happened. That's the failure the run log exists to prevent. Duplicates count as failures too, because they'd make one review look like two.

---

## 5. The original system still decides the same way

The six files in `samples/` each get the **same `guess`** as in the unit 9 recorded session, in every trial. Each also gets a `model_score` and `style_score` within **±0.01** of that session's values:

| Sample | guess | confidence | model_score | style_score |
|---|---|---|---|---|
| clearly_ai | ai | 0.783 | 0.7544 | 0.8115 |
| clearly_human | human | 0.2223 | 0.4445 | 0.0 |
| borderline | unsure | 0.537 | 0.3489 | 0.725 |
| formal_human | unsure | 0.4764 | 0.2681 | 0.6848 |
| plain_human | unsure | 0.394 | 0.6159 | 0.172 |
| edited_ai | ai | 0.6531 | 0.5904 | 0.7157 |

**Why this target:** This unit added a route and request hooks that run on *every* request, `/submit` included. If a hook changed what `/submit` sees, the labels would shift without anyone touching the detector, which the README rules out. ±0.01 and not "exactly equal": in the recorded session, every text sent twice scored identically to four decimals (clearly_ai gave 0.7544 both times), so the noise I've seen is zero. The 0.01 only leaves room for rounding and a different CPU, and anything beyond it is a real change. Not looser, because the label check alone catches a change only after it flips a label. edited_ai sits at 0.653, just 0.003 over the AI line, so a score drifting toward that line is the early warning, and a wide tolerance would hide it.
