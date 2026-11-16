#!/usr/bin/env python3
"""
The unit 9 criteria (criteria.md, "Unit 9 — the extension"), one trial per run.

    .venv/bin/gunicorn app:app --bind 127.0.0.1:5000 --workers 1 --timeout 120
    .venv/bin/python run_extension_eval.py --trial 1
    .venv/bin/python run_extension_eval.py --trial 2
    .venv/bin/python run_extension_eval.py --trial 3

Run it three separate times against the same server, changing nothing in
between. Each trial:

  1. sends 10 valid reviews (5 upheld, 5 overturned) for content_ids that are
     really under_review in the audit log                        -> criterion 1
  2. sends the 12 malformed review requests listed in criteria.md -> criterion 2
  3. checks the audit log didn't grow and those 10 items' latest
     status didn't change                                         -> criterion 3
  4. checks logs/runs.jsonl got exactly one matching line per
     review request                                               -> criterion 4
  5. submits the six samples/ files and compares guess and scores
     with the recorded session                                    -> criterion 5

It reads logs/runs.jsonl from disk, so run it on the machine the server runs on.
"""

import argparse
import datetime as dt
import json
import uuid

import requests

import config
import runlog

FIELDS = ("content_id", "reviewer_id", "outcome", "reasoning")

# Criterion 2: (name, raw body, field the message must name, or None for
# "Send a JSON object"). Raw strings so non-JSON and non-object bodies go out
# exactly as written.
BAD_REQUESTS = [
    ("not JSON", "hello", None),
    ("JSON list", '["upheld"]', None),
    ("JSON string", '"upheld"', None),
    ("content_id missing", '{"reviewer_id": "rev_eval", "outcome": "upheld", "reasoning": "x"}', "content_id"),
    ("reviewer_id missing", '{"content_id": "c_x", "outcome": "upheld", "reasoning": "x"}', "reviewer_id"),
    ("outcome missing", '{"content_id": "c_x", "reviewer_id": "rev_eval", "reasoning": "x"}', "outcome"),
    ("reasoning missing", '{"content_id": "c_x", "reviewer_id": "rev_eval", "outcome": "upheld"}', "reasoning"),
    ("reasoning only spaces", '{"content_id": "c_x", "reviewer_id": "rev_eval", "outcome": "upheld", "reasoning": "   "}', "reasoning"),
    ("content_id a number", '{"content_id": 42, "reviewer_id": "rev_eval", "outcome": "upheld", "reasoning": "x"}', "content_id"),
    ("reviewer_id null", '{"content_id": "c_x", "reviewer_id": null, "outcome": "upheld", "reasoning": "x"}', "reviewer_id"),
    ('outcome "maybe"', '{"content_id": "c_x", "reviewer_id": "rev_eval", "outcome": "maybe", "reasoning": "x"}', "outcome"),
    ('outcome "Upheld"', '{"content_id": "c_x", "reviewer_id": "rev_eval", "outcome": "Upheld", "reasoning": "x"}', "outcome"),
]

# Criterion 5: the recorded unit 9 session (README, Instrumentation).
EXPECTED = {
    "clearly_ai":    ("ai",     0.7544, 0.8115),
    "clearly_human": ("human",  0.4445, 0.0),
    "borderline":    ("unsure", 0.3489, 0.725),
    "formal_human":  ("unsure", 0.2681, 0.6848),
    "plain_human":   ("unsure", 0.6159, 0.172),
    "edited_ai":     ("ai",     0.5904, 0.7157),
}
TOLERANCE = 0.01

JSON = {"Content-Type": "application/json"}


def latest_statuses(url):
    entries = requests.get(f"{url}/log", timeout=10).json()["entries"]
    latest = {}
    for e in entries:
        if e.get("content_id"):
            latest[e["content_id"]] = e.get("status")
    return latest, len(entries)


def run_trial(url, trial):
    tag = f"t{trial}_{uuid.uuid4().hex[:6]}"
    statuses_before, audit_before = latest_statuses(url)
    under_review = [cid for cid, s in statuses_before.items() if s == "under_review"][:10]
    runs_before = len(runlog.read_runs())

    # Criterion 1 — ten valid reviews.
    valid, sent = [], []
    for i, cid in enumerate(under_review):
        body = {
            "content_id": cid,
            "reviewer_id": f"rev_eval_{tag}",
            "outcome": "upheld" if i < 5 else "overturned",
            "reasoning": f"Eval {tag}, review {i + 1}: checked against the writer's drafts.",
        }
        r = requests.post(f"{url}/review", json=body, timeout=10)
        got = r.json()
        ok = (r.status_code == 200 and got.get("recorded") is False
              and all(got.get(f) == body[f] for f in FIELDS))
        valid.append({"sent": body, "status": r.status_code, "response": got, "pass": ok})
        sent.append(r.status_code)

    # Criterion 2 — twelve malformed requests.
    bad = []
    for name, raw, field in BAD_REQUESTS:
        r = requests.post(f"{url}/review", data=raw, headers=JSON, timeout=10)
        got = r.json() if r.headers.get("Content-Type", "").startswith("application/json") else r.text
        message = got.get("message", "") if isinstance(got, dict) else ""
        names_it = (message == "Send a JSON object") if field is None else (f'"{field}"' in message)
        ok = (r.status_code == 400 and isinstance(got, dict)
              and got.get("error") == "bad_request" and names_it)
        bad.append({"case": name, "sent": raw, "status": r.status_code, "response": got, "pass": ok})
        sent.append(r.status_code)

    # Criterion 3 — nothing recorded, no status changed.
    statuses_after, audit_after = latest_statuses(url)
    changed = [cid for cid in under_review if statuses_after.get(cid) != statuses_before.get(cid)]
    c3 = {
        "audit_lines_before": audit_before,
        "audit_lines_after": audit_after,
        "content_ids_checked": len(under_review),
        "statuses_changed": changed,
        "pass": audit_after == audit_before and not changed and len(under_review) == 10,
    }

    # Criterion 4 — exactly one matching run-log line per review request.
    new_runs = runlog.read_runs()[runs_before:]
    review_runs = [r for r in new_runs if r.get("route") == "/review"]
    matched = 0
    for status, run in zip(sent, review_runs):
        has_error = run.get("error") is not None
        if run.get("status") == status and has_error == (status >= 400):
            matched += 1
    c4 = {
        "requests_sent": len(sent),
        "review_lines_written": len(review_runs),
        "lines_matching": matched,
        "example_lines": [review_runs[0], review_runs[-1]] if review_runs else [],
        "pass": len(review_runs) == len(sent) and matched == len(sent),
    }

    # Criterion 5 — the original /submit decides the same way.
    samples = []
    for name, (guess, model, style) in EXPECTED.items():
        body = json.loads((config.ROOT / "samples" / f"{name}.json").read_text(encoding="utf-8"))
        body["creator_id"] = f"eval9_{name}_{tag}"
        r = requests.post(f"{url}/submit", json=body, timeout=120)
        got = r.json()
        ok = (r.status_code == 200 and got.get("guess") == guess
              and abs(got.get("model_score", -9) - model) <= TOLERANCE
              and abs(got.get("style_score", -9) - style) <= TOLERANCE)
        samples.append({
            "sample": name, "status": r.status_code,
            "expected": {"guess": guess, "model_score": model, "style_score": style},
            "got": {k: got.get(k) for k in ("content_id", "guess", "confidence", "model_score", "style_score")},
            "pass": ok,
        })

    return {"valid": valid, "bad": bad, "c3": c3, "c4": c4, "samples": samples}


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--trial", type=int, required=True)
    parser.add_argument("--url", default=f"http://{config.HOST}:{config.PORT}")
    args = parser.parse_args()

    t = run_trial(args.url, args.trial)
    score = {
        "1. Valid reviews are accepted": f"{sum(v['pass'] for v in t['valid'])}/{len(t['valid'])}",
        "2. Bad review requests are refused, never crash": f"{sum(b['pass'] for b in t['bad'])}/{len(t['bad'])}",
        "3. /review changes nothing": (
            f"{t['c3']['audit_lines_after'] - t['c3']['audit_lines_before']} new lines, "
            f"{len(t['c3']['statuses_changed'])} statuses changed"),
        "4. Every review attempt leaves a trace": f"{t['c4']['lines_matching']}/{t['c4']['requests_sent']}",
        "5. Original system decides the same way": f"{sum(s['pass'] for s in t['samples'])}/{len(t['samples'])}",
    }
    for k, v in score.items():
        print(f"  {k}: {v}")

    config.RESULTS_DIR.mkdir(exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    path = config.RESULTS_DIR / f"extension_run_{stamp}_trial{args.trial}.md"
    lines = [
        f"# Extension run — trial {args.trial}",
        "",
        "- Produced by: `run_extension_eval.py::run_trial`",
        "- Service: `app.py::review`, `app.py::submit`, `app.py::get_log`, run log from `app.py::log_run`",
        f"- {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} · {args.url}",
        "",
        "| Criterion | Result |",
        "|---|---|",
        *[f"| {k} | {v} |" for k, v in score.items()],
        "",
    ]
    for key, title in [("valid", "Criterion 1 — valid reviews"), ("bad", "Criterion 2 — malformed requests"),
                       ("c3", "Criterion 3 — audit log and statuses"), ("c4", "Criterion 4 — run log"),
                       ("samples", "Criterion 5 — samples")]:
        lines += [f"## {title}", "", "```json", json.dumps(t[key], indent=2, ensure_ascii=False), "```", ""]
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote {path.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
