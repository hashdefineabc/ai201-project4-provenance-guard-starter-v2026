"""
The run log — one line per HTTP request, unit 9.

`audit.jsonl` records *decisions* (what the service concluded about a piece of
writing). This records *runs* (what the service did with each request): which
route, what came in, what went out, how long it took, and what broke. Every
request is written, including 400s, 429s and crashes — a failure that shows
up only as an absence is one you'll never find.

    from runlog import log_run, read_runs

    read_runs(limit=10)
"""

import json
import threading
from datetime import datetime, timezone

import config

_lock = threading.Lock()

# Long submissions are cut down to this many characters in the log. The
# length is recorded separately, so nothing about the size is lost.
PREVIEW_CHARS = 80


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def summarise_input(payload) -> dict | None:
    """What came in, without copying a whole essay into the log."""
    if payload is None:
        return None
    if not isinstance(payload, dict):
        return {"non_object_body": type(payload).__name__}

    summary = {}
    for key, value in payload.items():
        if key == "text" and isinstance(value, str):
            summary["text_chars"] = len(value)
            summary["text_preview"] = value[:PREVIEW_CHARS]
        else:
            summary[key] = value
    return summary


def summarise_output(body) -> dict | None:
    """What went out. `/log` responses are reduced to a count."""
    if not isinstance(body, dict):
        return None
    if "entries" in body:
        return {"count": body.get("count")}
    return body


def log_run(**fields) -> dict:
    entry = {"timestamp": _now(), **fields}
    config.LOG_DIR.mkdir(parents=True, exist_ok=True)
    line = json.dumps(entry, ensure_ascii=False, default=str)
    with _lock:
        with config.RUN_LOG.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    return entry


def read_runs(limit: int | None = None) -> list[dict]:
    """Read the run log back, oldest first. A malformed line is skipped."""
    if not config.RUN_LOG.exists():
        return []
    runs = []
    for line in config.RUN_LOG.read_text(encoding="utf-8").splitlines():
        try:
            runs.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return runs[-limit:] if limit else runs
