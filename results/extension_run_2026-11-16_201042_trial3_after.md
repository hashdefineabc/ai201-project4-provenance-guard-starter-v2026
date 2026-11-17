# Extension run — trial 3 — after

- Produced by: `run_extension_eval.py::run_trial`
- Service: `app.py::review`, `app.py::submit`, `app.py::get_log`, run log from `app.py::log_run`
- 2026-11-16 20:10:42 · http://127.0.0.1:5050

| Criterion | Result |
|---|---|
| 1. Valid reviews are accepted | 10/10 |
| 2. Bad review requests are refused, never crash | 12/12 |
| 3. /review changes nothing | 0 new lines, 0 statuses changed |
| 4. Every review attempt leaves a trace | 22/22 |
| 4 (tightened). 25 traces, each at most 8 KB | 25/25 within 8 KB, 25/25 matching, largest 1,127 B |
| 5. Original system decides the same way | 6/6 |

## Criterion 1 — valid reviews

```json
[
  {
    "sent": {
      "content_id": "c_47dbce47d028",
      "reviewer_id": "rev_eval_t3_3f8ffc",
      "outcome": "upheld",
      "reasoning": "Eval t3_3f8ffc, review 1: checked against the writer's drafts."
    },
    "status": 200,
    "response": {
      "content_id": "c_47dbce47d028",
      "message": "Review received. It is not written to the audit log yet.",
      "outcome": "upheld",
      "reasoning": "Eval t3_3f8ffc, review 1: checked against the writer's drafts.",
      "recorded": false,
      "reviewer_id": "rev_eval_t3_3f8ffc"
    },
    "pass": true
  },
  {
    "sent": {
      "content_id": "c_4ce2860da77c",
      "reviewer_id": "rev_eval_t3_3f8ffc",
      "outcome": "upheld",
      "reasoning": "Eval t3_3f8ffc, review 2: checked against the writer's drafts."
    },
    "status": 200,
    "response": {
      "content_id": "c_4ce2860da77c",
      "message": "Review received. It is not written to the audit log yet.",
      "outcome": "upheld",
      "reasoning": "Eval t3_3f8ffc, review 2: checked against the writer's drafts.",
      "recorded": false,
      "reviewer_id": "rev_eval_t3_3f8ffc"
    },
    "pass": true
  },
  {
    "sent": {
      "content_id": "c_1a6e89fce486",
      "reviewer_id": "rev_eval_t3_3f8ffc",
      "outcome": "upheld",
      "reasoning": "Eval t3_3f8ffc, review 3: checked against the writer's drafts."
    },
    "status": 200,
    "response": {
      "content_id": "c_1a6e89fce486",
      "message": "Review received. It is not written to the audit log yet.",
      "outcome": "upheld",
      "reasoning": "Eval t3_3f8ffc, review 3: checked against the writer's drafts.",
      "recorded": false,
      "reviewer_id": "rev_eval_t3_3f8ffc"
    },
    "pass": true
  },
  {
    "sent": {
      "content_id": "c_74008c4d554a",
      "reviewer_id": "rev_eval_t3_3f8ffc",
      "outcome": "upheld",
      "reasoning": "Eval t3_3f8ffc, review 4: checked against the writer's drafts."
    },
    "status": 200,
    "response": {
      "content_id": "c_74008c4d554a",
      "message": "Review received. It is not written to the audit log yet.",
      "outcome": "upheld",
      "reasoning": "Eval t3_3f8ffc, review 4: checked against the writer's drafts.",
      "recorded": false,
      "reviewer_id": "rev_eval_t3_3f8ffc"
    },
    "pass": true
  },
  {
    "sent": {
      "content_id": "c_6c752740f515",
      "reviewer_id": "rev_eval_t3_3f8ffc",
      "outcome": "upheld",
      "reasoning": "Eval t3_3f8ffc, review 5: checked against the writer's drafts."
    },
    "status": 200,
    "response": {
      "content_id": "c_6c752740f515",
      "message": "Review received. It is not written to the audit log yet.",
      "outcome": "upheld",
      "reasoning": "Eval t3_3f8ffc, review 5: checked against the writer's drafts.",
      "recorded": false,
      "reviewer_id": "rev_eval_t3_3f8ffc"
    },
    "pass": true
  },
  {
    "sent": {
      "content_id": "c_082d279987fe",
      "reviewer_id": "rev_eval_t3_3f8ffc",
      "outcome": "overturned",
      "reasoning": "Eval t3_3f8ffc, review 6: checked against the writer's drafts."
    },
    "status": 200,
    "response": {
      "content_id": "c_082d279987fe",
      "message": "Review received. It is not written to the audit log yet.",
      "outcome": "overturned",
      "reasoning": "Eval t3_3f8ffc, review 6: checked against the writer's drafts.",
      "recorded": false,
      "reviewer_id": "rev_eval_t3_3f8ffc"
    },
    "pass": true
  },
  {
    "sent": {
      "content_id": "c_a7256a8dab28",
      "reviewer_id": "rev_eval_t3_3f8ffc",
      "outcome": "overturned",
      "reasoning": "Eval t3_3f8ffc, review 7: checked against the writer's drafts."
    },
    "status": 200,
    "response": {
      "content_id": "c_a7256a8dab28",
      "message": "Review received. It is not written to the audit log yet.",
      "outcome": "overturned",
      "reasoning": "Eval t3_3f8ffc, review 7: checked against the writer's drafts.",
      "recorded": false,
      "reviewer_id": "rev_eval_t3_3f8ffc"
    },
    "pass": true
  },
  {
    "sent": {
      "content_id": "c_437cb95941c7",
      "reviewer_id": "rev_eval_t3_3f8ffc",
      "outcome": "overturned",
      "reasoning": "Eval t3_3f8ffc, review 8: checked against the writer's drafts."
    },
    "status": 200,
    "response": {
      "content_id": "c_437cb95941c7",
      "message": "Review received. It is not written to the audit log yet.",
      "outcome": "overturned",
      "reasoning": "Eval t3_3f8ffc, review 8: checked against the writer's drafts.",
      "recorded": false,
      "reviewer_id": "rev_eval_t3_3f8ffc"
    },
    "pass": true
  },
  {
    "sent": {
      "content_id": "c_2d0d6c799f90",
      "reviewer_id": "rev_eval_t3_3f8ffc",
      "outcome": "overturned",
      "reasoning": "Eval t3_3f8ffc, review 9: checked against the writer's drafts."
    },
    "status": 200,
    "response": {
      "content_id": "c_2d0d6c799f90",
      "message": "Review received. It is not written to the audit log yet.",
      "outcome": "overturned",
      "reasoning": "Eval t3_3f8ffc, review 9: checked against the writer's drafts.",
      "recorded": false,
      "reviewer_id": "rev_eval_t3_3f8ffc"
    },
    "pass": true
  },
  {
    "sent": {
      "content_id": "c_5e4b1bf057c9",
      "reviewer_id": "rev_eval_t3_3f8ffc",
      "outcome": "overturned",
      "reasoning": "Eval t3_3f8ffc, review 10: checked against the writer's drafts."
    },
    "status": 200,
    "response": {
      "content_id": "c_5e4b1bf057c9",
      "message": "Review received. It is not written to the audit log yet.",
      "outcome": "overturned",
      "reasoning": "Eval t3_3f8ffc, review 10: checked against the writer's drafts.",
      "recorded": false,
      "reviewer_id": "rev_eval_t3_3f8ffc"
    },
    "pass": true
  }
]
```

## Criterion 2 — malformed requests

```json
[
  {
    "case": "not JSON",
    "sent": "hello",
    "status": 400,
    "response": {
      "error": "bad_request",
      "message": "Send a JSON object"
    },
    "pass": true
  },
  {
    "case": "JSON list",
    "sent": "[\"upheld\"]",
    "status": 400,
    "response": {
      "error": "bad_request",
      "message": "Send a JSON object"
    },
    "pass": true
  },
  {
    "case": "JSON string",
    "sent": "\"upheld\"",
    "status": 400,
    "response": {
      "error": "bad_request",
      "message": "Send a JSON object"
    },
    "pass": true
  },
  {
    "case": "content_id missing",
    "sent": "{\"reviewer_id\": \"rev_eval\", \"outcome\": \"upheld\", \"reasoning\": \"x\"}",
    "status": 400,
    "response": {
      "error": "bad_request",
      "message": "Send JSON with a non-empty \"content_id\""
    },
    "pass": true
  },
  {
    "case": "reviewer_id missing",
    "sent": "{\"content_id\": \"c_x\", \"outcome\": \"upheld\", \"reasoning\": \"x\"}",
    "status": 400,
    "response": {
      "error": "bad_request",
      "message": "Send JSON with a non-empty \"reviewer_id\""
    },
    "pass": true
  },
  {
    "case": "outcome missing",
    "sent": "{\"content_id\": \"c_x\", \"reviewer_id\": \"rev_eval\", \"reasoning\": \"x\"}",
    "status": 400,
    "response": {
      "error": "bad_request",
      "message": "Send JSON with a non-empty \"outcome\""
    },
    "pass": true
  },
  {
    "case": "reasoning missing",
    "sent": "{\"content_id\": \"c_x\", \"reviewer_id\": \"rev_eval\", \"outcome\": \"upheld\"}",
    "status": 400,
    "response": {
      "error": "bad_request",
      "message": "Send JSON with a non-empty \"reasoning\""
    },
    "pass": true
  },
  {
    "case": "reasoning only spaces",
    "sent": "{\"content_id\": \"c_x\", \"reviewer_id\": \"rev_eval\", \"outcome\": \"upheld\", \"reasoning\": \"   \"}",
    "status": 400,
    "response": {
      "error": "bad_request",
      "message": "Send JSON with a non-empty \"reasoning\""
    },
    "pass": true
  },
  {
    "case": "content_id a number",
    "sent": "{\"content_id\": 42, \"reviewer_id\": \"rev_eval\", \"outcome\": \"upheld\", \"reasoning\": \"x\"}",
    "status": 400,
    "response": {
      "error": "bad_request",
      "message": "Send JSON with a non-empty \"content_id\""
    },
    "pass": true
  },
  {
    "case": "reviewer_id null",
    "sent": "{\"content_id\": \"c_x\", \"reviewer_id\": null, \"outcome\": \"upheld\", \"reasoning\": \"x\"}",
    "status": 400,
    "response": {
      "error": "bad_request",
      "message": "Send JSON with a non-empty \"reviewer_id\""
    },
    "pass": true
  },
  {
    "case": "outcome \"maybe\"",
    "sent": "{\"content_id\": \"c_x\", \"reviewer_id\": \"rev_eval\", \"outcome\": \"maybe\", \"reasoning\": \"x\"}",
    "status": 400,
    "response": {
      "error": "bad_request",
      "message": "\"outcome\" must be one of upheld, overturned"
    },
    "pass": true
  },
  {
    "case": "outcome \"Upheld\"",
    "sent": "{\"content_id\": \"c_x\", \"reviewer_id\": \"rev_eval\", \"outcome\": \"Upheld\", \"reasoning\": \"x\"}",
    "status": 400,
    "response": {
      "error": "bad_request",
      "message": "\"outcome\" must be one of upheld, overturned"
    },
    "pass": true
  }
]
```

## Criterion 3 — audit log and statuses

```json
{
  "audit_lines_before": 517,
  "audit_lines_after": 517,
  "content_ids_checked": 10,
  "statuses_changed": [],
  "pass": true
}
```

## Criterion 4 — run log

```json
{
  "requests_sent": 22,
  "review_lines_written": 22,
  "lines_matching": 22,
  "pass": true,
  "tightened_requests_sent": 25,
  "tightened_lines_written": 25,
  "tightened_lines_matching": 25,
  "lines_within_8kb": 25,
  "largest_line_bytes": 1127,
  "normal_line_bytes": 657,
  "oversized": [
    {
      "case": "reasoning 1,000,000 chars",
      "bytes_sent": 1000086,
      "status": 200,
      "log_line_bytes": 1127
    },
    {
      "case": "reviewer_id 100,000 chars",
      "bytes_sent": 100079,
      "status": 200,
      "log_line_bytes": 1111
    },
    {
      "case": "JSON list of 100,000 items",
      "bytes_sent": 1000000,
      "status": 400,
      "log_line_bytes": 322
    }
  ],
  "tightened_pass": true,
  "example_lines": [
    {
      "timestamp": "2026-11-16T14:40:41.969+00:00",
      "run_id": "r_a057fdd45b08",
      "method": "POST",
      "route": "/review",
      "status": 200,
      "duration_ms": 0.2,
      "cpu_ms": 0.2,
      "detector_was_loaded": true,
      "input": {
        "content_id": "c_47dbce47d028",
        "reviewer_id": "rev_eval_t3_3f8ffc",
        "outcome": "upheld",
        "reasoning": "Eval t3_3f8ffc, review 1: checked against the writer's drafts."
      },
      "output": {
        "content_id": "c_47dbce47d028",
        "message": "Review received. It is not written to the audit log yet.",
        "outcome": "upheld",
        "reasoning": "Eval t3_3f8ffc, review 1: checked against the writer's drafts.",
        "recorded": false,
        "reviewer_id": "rev_eval_t3_3f8ffc"
      },
      "error": null
    },
    {
      "timestamp": "2026-11-16T14:40:41.989+00:00",
      "run_id": "r_61f10344db1f",
      "method": "POST",
      "route": "/review",
      "status": 400,
      "duration_ms": 0.1,
      "cpu_ms": 0.1,
      "detector_was_loaded": true,
      "input": {
        "content_id": "c_x",
        "reviewer_id": "rev_eval",
        "outcome": "Upheld",
        "reasoning": "x"
      },
      "output": {
        "error": "bad_request",
        "message": "\"outcome\" must be one of upheld, overturned"
      },
      "error": "bad_request"
    }
  ],
  "oversized_line_example": "{\"timestamp\": \"2026-11-16T14:40:41.995+00:00\", \"run_id\": \"r_7cb423d26b63\", \"method\": \"POST\", \"route\": \"/review\", \"status\": 200, \"duration_ms\": 4.9, \"cpu_ms\": 4.9, \"detector_was_loaded\": true, \"input\": {\"content_id\": \"c_x\", \"reviewer_id\": \"rev_eval\", \"outcome\": \"upheld\", \"reasoning\": \"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa…[+999700 chars"
}
```

## Criterion 5 — samples

```json
[
  {
    "sample": "clearly_ai",
    "status": 200,
    "expected": {
      "guess": "ai",
      "model_score": 0.7544,
      "style_score": 0.8115
    },
    "got": {
      "content_id": "c_27800874e775",
      "guess": "ai",
      "confidence": 0.783,
      "model_score": 0.7544,
      "style_score": 0.8115
    },
    "pass": true
  },
  {
    "sample": "clearly_human",
    "status": 200,
    "expected": {
      "guess": "human",
      "model_score": 0.4445,
      "style_score": 0.0
    },
    "got": {
      "content_id": "c_e0e4d05b82c0",
      "guess": "human",
      "confidence": 0.2223,
      "model_score": 0.4445,
      "style_score": 0.0
    },
    "pass": true
  },
  {
    "sample": "borderline",
    "status": 200,
    "expected": {
      "guess": "unsure",
      "model_score": 0.3489,
      "style_score": 0.725
    },
    "got": {
      "content_id": "c_ef88e87ef06e",
      "guess": "unsure",
      "confidence": 0.537,
      "model_score": 0.3489,
      "style_score": 0.725
    },
    "pass": true
  },
  {
    "sample": "formal_human",
    "status": 200,
    "expected": {
      "guess": "unsure",
      "model_score": 0.2681,
      "style_score": 0.6848
    },
    "got": {
      "content_id": "c_32d7284f6c82",
      "guess": "unsure",
      "confidence": 0.4764,
      "model_score": 0.2681,
      "style_score": 0.6848
    },
    "pass": true
  },
  {
    "sample": "plain_human",
    "status": 200,
    "expected": {
      "guess": "unsure",
      "model_score": 0.6159,
      "style_score": 0.172
    },
    "got": {
      "content_id": "c_debe79a2fb33",
      "guess": "unsure",
      "confidence": 0.394,
      "model_score": 0.6159,
      "style_score": 0.172
    },
    "pass": true
  },
  {
    "sample": "edited_ai",
    "status": 200,
    "expected": {
      "guess": "ai",
      "model_score": 0.5904,
      "style_score": 0.7157
    },
    "got": {
      "content_id": "c_60a7f44da88b",
      "guess": "ai",
      "confidence": 0.6531,
      "model_score": 0.5904,
      "style_score": 0.7157
    },
    "pass": true
  }
]
```
