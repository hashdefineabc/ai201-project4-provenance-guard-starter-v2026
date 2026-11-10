# Attack run — after

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-10 10:48
- Auto-marked BROKE (5xx, crash, no response): **1**
- Left for you to judge: **55**

The Verdict column is blank where a script can't honestly decide. Whether
an evasion worked depends on where you put your thresholds — read the
`targets` column, look at what came back, and write HELD or BROKE yourself.

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `c_c542421eb3ae` | unsure | 0.582 || BROKE |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `c_1364f3492c83` | human | 0.340 || BROKE |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `c_88a766709751` | ai | 0.714 || HELD |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `c_03262f129def` | ai | 0.806 || HELD |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `c_fe7ebb93325b` | human | 0.348 || BROKE |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `c_b1b6eea60fdc` | human | 0.286 || BROKE |
| EV07 | evasion | signal two: padding with punctuation | 200 | `c_16b0edc1c4d8` | unsure | 0.543 || BROKE |
| EV08 | evasion | signal one: text below the token window | 200 | `c_42ae857cf24b` | unsure | 0.600 || BROKE |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `c_6c9440453b63` | ai | 0.713 || HELD |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `c_f93f85835c9d` | ai | 0.911 || HELD |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `c_9b4f6c1f9353` | ai | 0.677 || BROKE |
| FP02 | false_positive | human writing in a formal register | 200 | `c_9f3f3baf314f` | ai | 0.869 || BROKE |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `c_1daa5618a459` | ai | 0.879 || BROKE |
| FP04 | false_positive | a student essay written to a rubric | 200 | `c_4835330c0901` | ai | 0.861 || BROKE |
| FP05 | false_positive | technical documentation written by a person | 200 | `c_647381a962e1` | ai | 0.900 || BROKE |
| FP06 | false_positive | a person imitating a formal template | 200 | `c_6d2ef214efe7` | ai | 0.758 || BROKE |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `c_149c9875158f` | unsure | 0.582 || HELD |
| FP08 | false_positive | very short genuine human submission | 200 | `c_e13fbf32d622` | unsure | 0.550 || HELD |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `c_569192db0007` | unsure | 0.429 || BROKE |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `c_7a2f9b09d02f` | human | 0.309 || BROKE |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `c_50cd0c3faa13` | ai | 0.761 || HELD |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `c_953f8afeb9b6` | unsure | 0.600 || HELD |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `c_398c1b8289c7` | ai | 0.677 || HELD |
| PI06 | prompt_injection | instruction plus real human text | 200 | `c_183c1a6177b6` | ai | 0.658 || BROKE |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — || HELD |
| MF02 | malformed | text is a single character | 400 | `—` | — | — || HELD |
| MF03 | malformed | text is control characters | 200 | `c_07a4d8019257` | human | 0.250 || BROKE |
| MF04 | malformed | text is only punctuation | 200 | `c_0d5da257599c` | human | 0.256 || BROKE |
| MF05 | malformed | text is a very long single word | 200 | `c_9ce713d1b669` | unsure | 0.600 || HELD |
| MF06 | malformed | text is emoji only | 200 | `c_5f0cbce9462c` | unsure | 0.600 || HELD |
| MF07 | malformed | text is right-to-left script | 200 | `c_8f9d5cbd9d49` | unsure | 0.600 || HELD |
| MF08 | malformed | text is 60,000 characters | 200 | `c_5d0e0a705462` | ai | 0.887 || BROKE |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — || HELD |
| RQ02 | malformed | no creator_id | 200 | `c_1fed9b30579c` | unsure | 0.370 || HELD |
| RQ03 | malformed | text is a number | 400 | `—` | — | — || HELD |
| RQ04 | malformed | text is a list | 400 | `—` | — | — || HELD |
| RQ05 | malformed | text is null | 400 | `—` | — | — || HELD |
| RQ06 | malformed | creator_id is an object | 200 | `c_bfd1000f0e4f` | human | 0.275 || BROKE |
| RQ07 | malformed | body is a JSON array, not an object | 500 | `—` | — | — | BROKE |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — || HELD |
| RQ09 | malformed | body is empty | 400 | `—` | — | — || HELD |
| RQ10 | malformed | body is form-encoded, not JSON | 429 | `—` | — | — || HELD |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | `—` | — | — || HELD |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — || HELD |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_ad476fe64e46` | human | 0.264 || HELD |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_0229b477c34b` | human | 0.264 || HELD |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_0048e1ac0473` | human | 0.264 || HELD |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_c1c25b09e706` | human | 0.264 || HELD |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_6e2cb51cbfd0` | human | 0.264 || HELD |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — || HELD |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — || HELD |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — || HELD |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — || HELD |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — || HELD |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — || HELD |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — || HELD |

---

## By family

| Family | Attacks | Auto-BROKE | Left to judge |
|---|---|---|---|
| `evasion` | 10 | 0 | 10 |
| `false_positive` | 8 | 0 | 8 |
| `flood_same_creator` | 12 | 0 | 12 |
| `malformed` | 20 | 1 | 19 |
| `prompt_injection` | 6 | 0 | 6 |

> The **false_positive** family is the one to look at hardest. Those are
> written to be genuine human writing that reads as machine-like. Every one
> your service calls AI is a real writer it would have accused.

---

## What came back

The detail behind the table. Paste the interesting failures into your
README — the ones that show something, not the ten easiest.

### EV01 — `evasion`

*Targeting:* signal two: typos raise word variety

```json
{
  "id": "EV01",
  "status": 200,
  "content_id": "c_c542421eb3ae",
  "creator_id": "attacker_EV01",
  "guess": "unsure",
  "confidence": 0.5817,
  "model_score": 0.1635,
  "style_score": 1.0,
  "label": "We can't tell from the writing alone whether this was written by a person or with help from AI. That happens often, especially with short or plainly written pieces, and it isn't a judgement about the writer.",
  "error": null,
  "verdict": ""
}
```

### EV02 — `evasion`

*Targeting:* signal two: broken-up sentences raise length spread

```json
{
  "id": "EV02",
  "status": 200,
  "content_id": "c_1364f3492c83",
  "creator_id": "attacker_EV02",
  "guess": "human",
  "confidence": 0.3395,
  "model_score": 0.5943,
  "style_score": 0.0847,
  "label": "This reads like it was written by a person.",
  "error": null,
  "verdict": ""
}
```

### EV03 — `evasion`

*Targeting:* signal two: a pasted quotation changes the shape

```json
{
  "id": "EV03",
  "status": 200,
  "content_id": "c_88a766709751",
  "creator_id": "attacker_EV03",
  "guess": "ai",
  "confidence": 0.7136,
  "model_score": 0.6662,
  "style_score": 0.761,
  "label": "Our checks suggest this was probably written with AI. Automated checks can be wrong, and they are wrong more often about plain, simple writing. If you wrote this yourself, you can ask for a person to review it.",
  "error": null,
  "verdict": ""
}
```

### EV04 — `evasion`

*Targeting:* signal one: unusual words raise perplexity

```json
{
  "id": "EV04",
  "status": 200,
  "content_id": "c_03262f129def",
  "creator_id": "attacker_EV04",
  "guess": "ai",
  "confidence": 0.8057,
  "model_score": 0.6114,
  "style_score": 1.0,
  "label": "Our checks suggest this was probably written with AI. Automated checks can be wrong, and they are wrong more often about plain, simple writing. If you wrote this yourself, you can ask for a person to review it.",
  "error": null,
  "verdict": ""
}
```

### EV05 — `evasion`

*Targeting:* both signals: heavy human editing pass

```json
{
  "id": "EV05",
  "status": 200,
  "content_id": "c_fe7ebb93325b",
  "creator_id": "attacker_EV05",
  "guess": "human",
  "confidence": 0.3478,
  "model_score": 0.3212,
  "style_score": 0.3745,
  "label": "This reads like it was written by a person.",
  "error": null,
  "verdict": ""
}
```

### EV06 — `evasion`

*Targeting:* signal two: one very long sentence and one very short

```json
{
  "id": "EV06",
  "status": 200,
  "content_id": "c_b1b6eea60fdc",
  "creator_id": "attacker_EV06",
  "guess": "human",
  "confidence": 0.2863,
  "model_score": 0.5727,
  "style_score": 0.0,
  "label": "This reads like it was written by a person.",
  "error": null,
  "verdict": ""
}
```

### EV07 — `evasion`

*Targeting:* signal two: padding with punctuation

```json
{
  "id": "EV07",
  "status": 200,
  "content_id": "c_16b0edc1c4d8",
  "creator_id": "attacker_EV07",
  "guess": "unsure",
  "confidence": 0.5431,
  "model_score": 0.5862,
  "style_score": 0.5,
  "label": "We can't tell from the writing alone whether this was written by a person or with help from AI. That happens often, especially with short or plainly written pieces, and it isn't a judgement about the writer.",
  "error": null,
  "verdict": ""
}
```

### EV08 — `evasion`

*Targeting:* signal one: text below the token window

```json
{
  "id": "EV08",
  "status": 200,
  "content_id": "c_42ae857cf24b",
  "creator_id": "attacker_EV08",
  "guess": "unsure",
  "confidence": 0.6,
  "model_score": 0.2452,
  "style_score": 1.0,
  "label": "We can't tell from the writing alone whether this was written by a person or with help from AI. That happens often, especially with short or plainly written pieces, and it isn't a judgement about the writer.",
  "error": null,
  "verdict": ""
}
```

### EV09 — `evasion`

*Targeting:* both: AI text with a human opening paragraph bolted on

```json
{
  "id": "EV09",
  "status": 200,
  "content_id": "c_6c9440453b63",
  "creator_id": "attacker_EV09",
  "guess": "ai",
  "confidence": 0.7125,
  "model_score": 0.7042,
  "style_score": 0.7208,
  "label": "Our checks suggest this was probably written with AI. Automated checks can be wrong, and they are wrong more often about plain, simple writing. If you wrote this yourself, you can ask for a person to review it.",
  "error": null,
  "verdict": ""
}
```

### EV10 — `evasion`

*Targeting:* signal two: repeated stanza structure

```json
{
  "id": "EV10",
  "status": 200,
  "content_id": "c_f93f85835c9d",
  "creator_id": "attacker_EV10",
  "guess": "ai",
  "confidence": 0.9113,
  "model_score": 0.9792,
  "style_score": 0.8435,
  "label": "Our checks suggest this was probably written with AI. Automated checks can be wrong, and they are wrong more often about plain, simple writing. If you wrote this yourself, you can ask for a person to review it.",
  "error": null,
  "verdict": ""
}
```

### FP01 — `false_positive`

*Targeting:* plain, clear human writing with no flourishes

```json
{
  "id": "FP01",
  "status": 200,
  "content_id": "c_9b4f6c1f9353",
  "creator_id": "attacker_FP01",
  "guess": "ai",
  "confidence": 0.6775,
  "model_score": 0.6175,
  "style_score": 0.7375,
  "label": "Our checks suggest this was probably written with AI. Automated checks can be wrong, and they are wrong more often about plain, simple writing. If you wrote this yourself, you can ask for a person to review it.",
  "error": null,
  "verdict": ""
}
```

### FP02 — `false_positive`

*Targeting:* human writing in a formal register

```json
{
  "id": "FP02",
  "status": 200,
  "content_id": "c_9f3f3baf314f",
  "creator_id": "attacker_FP02",
  "guess": "ai",
  "confidence": 0.8694,
  "model_score": 0.7387,
  "style_score": 1.0,
  "label": "Our checks suggest this was probably written with AI. Automated checks can be wrong, and they are wrong more often about plain, simple writing. If you wrote this yourself, you can ask for a person to review it.",
  "error": null,
  "verdict": ""
}
```

### FP03 — `false_positive`

*Targeting:* a non-native English speaker writing carefully

```json
{
  "id": "FP03",
  "status": 200,
  "content_id": "c_1daa5618a459",
  "creator_id": "attacker_FP03",
  "guess": "ai",
  "confidence": 0.879,
  "model_score": 0.8051,
  "style_score": 0.953,
  "label": "Our checks suggest this was probably written with AI. Automated checks can be wrong, and they are wrong more often about plain, simple writing. If you wrote this yourself, you can ask for a person to review it.",
  "error": null,
  "verdict": ""
}
```

### FP04 — `false_positive`

*Targeting:* a student essay written to a rubric

```json
{
  "id": "FP04",
  "status": 200,
  "content_id": "c_4835330c0901",
  "creator_id": "attacker_FP04",
  "guess": "ai",
  "confidence": 0.8609,
  "model_score": 0.8329,
  "style_score": 0.8888,
  "label": "Our checks suggest this was probably written with AI. Automated checks can be wrong, and they are wrong more often about plain, simple writing. If you wrote this yourself, you can ask for a person to review it.",
  "error": null,
  "verdict": ""
}
```

### FP05 — `false_positive`

*Targeting:* technical documentation written by a person

```json
{
  "id": "FP05",
  "status": 200,
  "content_id": "c_647381a962e1",
  "creator_id": "attacker_FP05",
  "guess": "ai",
  "confidence": 0.9002,
  "model_score": 0.8005,
  "style_score": 1.0,
  "label": "Our checks suggest this was probably written with AI. Automated checks can be wrong, and they are wrong more often about plain, simple writing. If you wrote this yourself, you can ask for a person to review it.",
  "error": null,
  "verdict": ""
}
```

### FP06 — `false_positive`

*Targeting:* a person imitating a formal template

```json
{
  "id": "FP06",
  "status": 200,
  "content_id": "c_6d2ef214efe7",
  "creator_id": "attacker_FP06",
  "guess": "ai",
  "confidence": 0.7581,
  "model_score": 0.8814,
  "style_score": 0.6347,
  "label": "Our checks suggest this was probably written with AI. Automated checks can be wrong, and they are wrong more often about plain, simple writing. If you wrote this yourself, you can ask for a person to review it.",
  "error": null,
  "verdict": ""
}
```

### FP07 — `false_positive`

*Targeting:* human writing that repeats a phrase deliberately

```json
{
  "id": "FP07",
  "status": 200,
  "content_id": "c_149c9875158f",
  "creator_id": "attacker_FP07",
  "guess": "unsure",
  "confidence": 0.5817,
  "model_score": 0.8816,
  "style_score": 0.2818,
  "label": "We can't tell from the writing alone whether this was written by a person or with help from AI. That happens often, especially with short or plainly written pieces, and it isn't a judgement about the writer.",
  "error": null,
  "verdict": ""
}
```

### FP08 — `false_positive`

*Targeting:* very short genuine human submission

```json
{
  "id": "FP08",
  "status": 200,
  "content_id": "c_e13fbf32d622",
  "creator_id": "attacker_FP08",
  "guess": "unsure",
  "confidence": 0.5503,
  "model_score": 0.3223,
  "style_score": 0.7783,
  "label": "We can't tell from the writing alone whether this was written by a person or with help from AI. That happens often, especially with short or plainly written pieces, and it isn't a judgement about the writer.",
  "error": null,
  "verdict": ""
}
```

### PI01 — `prompt_injection`

*Targeting:* instruction to ignore the check

```json
{
  "id": "PI01",
  "status": 200,
  "content_id": "c_569192db0007",
  "creator_id": "attacker_PI01",
  "guess": "unsure",
  "confidence": 0.429,
  "model_score": 0.4625,
  "style_score": 0.3955,
  "label": "We can't tell from the writing alone whether this was written by a person or with help from AI. That happens often, especially with short or plainly written pieces, and it isn't a judgement about the writer.",
  "error": null,
  "verdict": ""
}
```

### PI02 — `prompt_injection`

*Targeting:* instruction disguised as a system message

```json
{
  "id": "PI02",
  "status": 200,
  "content_id": "c_7a2f9b09d02f",
  "creator_id": "attacker_PI02",
  "guess": "human",
  "confidence": 0.309,
  "model_score": 0.2044,
  "style_score": 0.4137,
  "label": "This reads like it was written by a person.",
  "error": null,
  "verdict": ""
}
```

### PI03 — `prompt_injection`

*Targeting:* instruction wrapped in the writer's voice

```json
{
  "id": "PI03",
  "status": 200,
  "content_id": "c_50cd0c3faa13",
  "creator_id": "attacker_PI03",
  "guess": "ai",
  "confidence": 0.7612,
  "model_score": 0.5943,
  "style_score": 0.9282,
  "label": "Our checks suggest this was probably written with AI. Automated checks can be wrong, and they are wrong more often about plain, simple writing. If you wrote this yourself, you can ask for a person to review it.",
  "error": null,
  "verdict": ""
}
```

### PI04 — `prompt_injection`

*Targeting:* attempt to make the label text hostile

```json
{
  "id": "PI04",
  "status": 200,
  "content_id": "c_953f8afeb9b6",
  "creator_id": "attacker_PI04",
  "guess": "unsure",
  "confidence": 0.6,
  "model_score": 0.4998,
  "style_score": 0.8388,
  "label": "We can't tell from the writing alone whether this was written by a person or with help from AI. That happens often, especially with short or plainly written pieces, and it isn't a judgement about the writer.",
  "error": null,
  "verdict": ""
}
```

### PI05 — `prompt_injection`

*Targeting:* attempt to inject into the audit log

```json
{
  "id": "PI05",
  "status": 200,
  "content_id": "c_398c1b8289c7",
  "creator_id": "attacker_PI05",
  "guess": "ai",
  "confidence": 0.6772,
  "model_score": 0.6401,
  "style_score": 0.7143,
  "label": "Our checks suggest this was probably written with AI. Automated checks can be wrong, and they are wrong more often about plain, simple writing. If you wrote this yourself, you can ask for a person to review it.",
  "error": null,
  "verdict": ""
}
```

### PI06 — `prompt_injection`

*Targeting:* instruction plus real human text

```json
{
  "id": "PI06",
  "status": 200,
  "content_id": "c_183c1a6177b6",
  "creator_id": "attacker_PI06",
  "guess": "ai",
  "confidence": 0.658,
  "model_score": 0.5583,
  "style_score": 0.7577,
  "label": "Our checks suggest this was probably written with AI. Automated checks can be wrong, and they are wrong more often about plain, simple writing. If you wrote this yourself, you can ask for a person to review it.",
  "error": null,
  "verdict": ""
}
```

### MF01 — `malformed`

*Targeting:* text is only whitespace

```json
{
  "id": "MF01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF02 — `malformed`

*Targeting:* text is a single character

```json
{
  "id": "MF02",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF02",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF03 — `malformed`

*Targeting:* text is control characters

```json
{
  "id": "MF03",
  "status": 200,
  "content_id": "c_07a4d8019257",
  "creator_id": "attacker_MF03",
  "guess": "human",
  "confidence": 0.25,
  "model_score": 0.0,
  "style_score": 0.5,
  "label": "This reads like it was written by a person.",
  "error": null,
  "verdict": ""
}
```

### MF04 — `malformed`

*Targeting:* text is only punctuation

```json
{
  "id": "MF04",
  "status": 200,
  "content_id": "c_0d5da257599c",
  "creator_id": "attacker_MF04",
  "guess": "human",
  "confidence": 0.2556,
  "model_score": 0.0112,
  "style_score": 0.5,
  "label": "This reads like it was written by a person.",
  "error": null,
  "verdict": ""
}
```

### MF05 — `malformed`

*Targeting:* text is a very long single word

```json
{
  "id": "MF05",
  "status": 200,
  "content_id": "c_9ce713d1b669",
  "creator_id": "attacker_MF05",
  "guess": "unsure",
  "confidence": 0.6,
  "model_score": 0.9976,
  "style_score": 0.5,
  "label": "We can't tell from the writing alone whether this was written by a person or with help from AI. That happens often, especially with short or plainly written pieces, and it isn't a judgement about the writer.",
  "error": null,
  "verdict": ""
}
```

### MF06 — `malformed`

*Targeting:* text is emoji only

```json
{
  "id": "MF06",
  "status": 200,
  "content_id": "c_5f0cbce9462c",
  "creator_id": "attacker_MF06",
  "guess": "unsure",
  "confidence": 0.6,
  "model_score": 0.9969,
  "style_score": 0.5,
  "label": "We can't tell from the writing alone whether this was written by a person or with help from AI. That happens often, especially with short or plainly written pieces, and it isn't a judgement about the writer.",
  "error": null,
  "verdict": ""
}
```

### MF07 — `malformed`

*Targeting:* text is right-to-left script

```json
{
  "id": "MF07",
  "status": 200,
  "content_id": "c_8f9d5cbd9d49",
  "creator_id": "attacker_MF07",
  "guess": "unsure",
  "confidence": 0.6,
  "model_score": 0.9064,
  "style_score": 0.5,
  "label": "We can't tell from the writing alone whether this was written by a person or with help from AI. That happens often, especially with short or plainly written pieces, and it isn't a judgement about the writer.",
  "error": null,
  "verdict": ""
}
```

### MF08 — `malformed`

*Targeting:* text is 60,000 characters

```json
{
  "id": "MF08",
  "status": 200,
  "content_id": "c_5d0e0a705462",
  "creator_id": "attacker_MF08",
  "guess": "ai",
  "confidence": 0.887,
  "model_score": 0.9876,
  "style_score": 0.7863,
  "label": "Our checks suggest this was probably written with AI. Automated checks can be wrong, and they are wrong more often about plain, simple writing. If you wrote this yourself, you can ask for a person to review it.",
  "error": null,
  "verdict": ""
}
```

### RQ01 — `malformed`

*Targeting:* no text field at all

```json
{
  "id": "RQ01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ02 — `malformed`

*Targeting:* no creator_id

```json
{
  "id": "RQ02",
  "status": 200,
  "content_id": "c_1fed9b30579c",
  "creator_id": null,
  "guess": "unsure",
  "confidence": 0.3698,
  "model_score": 0.2395,
  "style_score": 0.5,
  "label": "We can't tell from the writing alone whether this was written by a person or with help from AI. That happens often, especially with short or plainly written pieces, and it isn't a judgement about the writer.",
  "error": null,
  "verdict": ""
}
```

### RQ03 — `malformed`

*Targeting:* text is a number

```json
{
  "id": "RQ03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ04 — `malformed`

*Targeting:* text is a list

```json
{
  "id": "RQ04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ05 — `malformed`

*Targeting:* text is null

```json
{
  "id": "RQ05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ06 — `malformed`

*Targeting:* creator_id is an object

```json
{
  "id": "RQ06",
  "status": 200,
  "content_id": "c_bfd1000f0e4f",
  "creator_id": {
    "id": "x"
  },
  "guess": "human",
  "confidence": 0.2746,
  "model_score": 0.0492,
  "style_score": 0.5,
  "label": "This reads like it was written by a person.",
  "error": null,
  "verdict": ""
}
```

### RQ07 — `malformed`

*Targeting:* body is a JSON array, not an object

```json
{
  "id": "RQ07",
  "status": 500,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": "response wasn't JSON: <!doctype html>\n<html lang=en>\n<title>500 Internal Server Error</title>\n<h1>Internal Server Error</h1>\n<p>The server encountered an internal error and was unable to complete your request. Either the s",
  "verdict": "BROKE"
}
```

### RQ08 — `malformed`

*Targeting:* body is unparseable JSON

```json
{
  "id": "RQ08",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ09 — `malformed`

*Targeting:* body is empty

```json
{
  "id": "RQ09",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ10 — `malformed`

*Targeting:* body is form-encoded, not JSON

```json
{
  "id": "RQ10",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ11 — `malformed`

*Targeting:* body is JSON claiming to be plain text

```json
{
  "id": "RQ11",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ12 — `malformed`

*Targeting:* deeply nested JSON

```json
{
  "id": "RQ12",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ12",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_01 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_01",
  "status": 200,
  "content_id": "c_ad476fe64e46",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2643,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "This reads like it was written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_02 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_02",
  "status": 200,
  "content_id": "c_0229b477c34b",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2643,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "This reads like it was written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_03 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_03",
  "status": 200,
  "content_id": "c_0048e1ac0473",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2643,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "This reads like it was written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_04 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_04",
  "status": 200,
  "content_id": "c_c1c25b09e706",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2643,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "This reads like it was written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_05 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_05",
  "status": 200,
  "content_id": "c_6e2cb51cbfd0",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2643,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "This reads like it was written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_06 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_06",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_07 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_07",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_08 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_08",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_09 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_09",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_10 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_10",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_11 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_11",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_12 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_12",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```
