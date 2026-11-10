#!/usr/bin/env python3
"""
Criterion 4 (the appeal path) and the /ping half of criterion 5, three trials.

    python app.py                                   # in one terminal
    python run_eval.py --label before               # criteria 1, 2, 3, 5
    python run_appeal_eval.py --label before        # criterion 4, then /ping

run_eval.py only calls /submit, and an appeal needs a content_id from a real
submission first, so this does the submit -> appeal -> read-the-log round trip
itself. Each trial:

  1. submits 5 texts, each under its own creator_id (so the rate limit
     doesn't eat the test), and appeals every content_id that came back
  2. checks /log holds an appeal entry for each one, with the reasoning sent
     and status under_review
  3. appeals a made-up content_id and checks it gets a 404 and that the log
     didn't grow

Then it checks /ping still answers.
"""

import argparse
import datetime as dt
import json
import uuid

import requests

import config

TEXTS = [
    "I walked to the market this morning and the bread was still warm, so I bought two loaves.",
    "My grandmother kept her buttons in an old biscuit tin, and we sorted them by colour for hours.",
    "The train was late again, so I read half a chapter standing on the platform in the cold.",
    "We painted the spare room green last weekend and it already feels like a different house.",
    "The cat has decided the laundry basket is hers now, and nobody in the house is arguing.",
]
REASONING = "I wrote this myself, on {when}. Eval trial {trial}, piece {i}."


def log_count(url):
    return requests.get(f"{url}/log", timeout=10).json()["count"]


def run_trial(url, trial):
    checks = []
    for i, text in enumerate(TEXTS, 1):
        creator = f"eval_appeal_t{trial}_{i}_{uuid.uuid4().hex[:6]}"
        sub = requests.post(f"{url}/submit", json={"text": text, "creator_id": creator}, timeout=90)
        content_id = sub.json().get("content_id") if sub.status_code == 200 else None
        reasoning = REASONING.format(when=dt.date.today().isoformat(), trial=trial, i=i)

        appeal = requests.post(f"{url}/appeal",
                               json={"content_id": content_id, "reasoning": reasoning}, timeout=30)
        entries = requests.get(f"{url}/log", timeout=10).json()["entries"]
        logged = [e for e in entries
                  if e.get("content_id") == content_id and e.get("event") == "appeal"]
        ok = (sub.status_code == 200 and appeal.status_code == 200
              and len(logged) == 1
              and logged[0].get("status") == "under_review"
              and logged[0].get("reasoning") == reasoning)
        checks.append({
            "content_id": content_id,
            "submit_status": sub.status_code,
            "appeal_status": appeal.status_code,
            "appeal_response": appeal.json(),
            "log_entry": logged[0] if logged else None,
            "pass": ok,
        })

    before = log_count(url)
    fake = f"c_doesnotexist{trial}"
    bogus = requests.post(f"{url}/appeal",
                          json={"content_id": fake, "reasoning": "This id was never issued."},
                          timeout=30)
    after = log_count(url)
    fake_check = {
        "content_id": fake,
        "status": bogus.status_code,
        "response": bogus.json(),
        "log_count_before": before,
        "log_count_after": after,
        "pass": bogus.status_code == 404 and before == after,
    }
    return checks, fake_check


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--label", default="")
    parser.add_argument("--url", default=f"http://{config.HOST}:{config.PORT}")
    args = parser.parse_args()

    trials = []
    for trial in range(1, args.trials + 1):
        checks, fake_check = run_trial(args.url, trial)
        passed = sum(c["pass"] for c in checks)
        print(f"  trial {trial}: {passed}/{len(checks)} appeals recorded, "
              f"fake id -> {fake_check['status']} "
              f"({'log unchanged' if fake_check['pass'] else 'FAILED'})")
        trials.append({"appeals": checks, "fake_id": fake_check})

    ping = requests.post(f"{args.url}/ping", json={"message": "still alive?"}, timeout=10)
    print(f"  /ping afterwards: {ping.status_code} {ping.json()}")

    config.RESULTS_DIR.mkdir(exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    label = f"_{args.label}" if args.label else ""
    path = config.RESULTS_DIR / f"appeal_run_{stamp}{label}.md"
    lines = [
        f"# Appeal path run{f' — {args.label}' if args.label else ''}",
        "",
        "- Produced by: `run_appeal_eval.py::run_trial`",
        "- Service: `app.py::submit`, `app.py::appeal`, `app.py::get_log`",
        f"- {args.trials} trials · {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
    ]
    for n, t in enumerate(trials, 1):
        passed = sum(c["pass"] for c in t["appeals"])
        lines += [f"## Trial {n}: {passed}/{len(t['appeals'])} appeals, "
                  f"fake id {'PASS' if t['fake_id']['pass'] else 'FAIL'}", "",
                  "```json", json.dumps(t, indent=2, ensure_ascii=False), "```", ""]
    lines += ["## /ping afterwards", "", "```json",
              json.dumps({"status": ping.status_code, "body": ping.json()}, indent=2), "```", ""]
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote {path.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
