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

# Milestone 6: every other value is bounded too, whatever its field is called.
# Before this only `text` was cut, and a 1 MB `reasoning` sent to /review was
# copied into its log line twice (input, and the echoed output) — 2 MB a line.
# 300 keeps every label whole (the longest is ~215 characters).
MAX_FIELD_CHARS = 300
MAX_ITEMS = 50
MAX_SECTION_CHARS = 3000


def _bounded(value):
    """A copy of `value` with every string, key and list cut down to size."""
    if isinstance(value, str):
        if len(value) <= MAX_FIELD_CHARS:
            return value
        return f"{value[:MAX_FIELD_CHARS]}…[+{len(value) - MAX_FIELD_CHARS} chars]"
    if isinstance(value, dict):
        items = list(value.items())
        out = {_bounded(str(k)): _bounded(v) for k, v in items[:MAX_ITEMS]}
        if len(items) > MAX_ITEMS:
            out["…"] = f"+{len(items) - MAX_ITEMS} more keys"
        return out
    if isinstance(value, list):
        out = [_bounded(v) for v in value[:MAX_ITEMS]]
        if len(value) > MAX_ITEMS:
            out.append(f"…[+{len(value) - MAX_ITEMS} items]")
        return out
    return value


def _capped(section):
    """The last guard: a section still too big after _bounded is cut whole."""
    section = _bounded(section)
    as_json = json.dumps(section, ensure_ascii=False, default=str)
    if len(as_json) <= MAX_SECTION_CHARS:
        return section
    return {"truncated": as_json[:MAX_SECTION_CHARS], "json_chars": len(as_json)}


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
    return _capped(summary)


def summarise_output(body) -> dict | None:
    """What went out. `/log` responses are reduced to a count."""
    if not isinstance(body, dict):
        return None
    if "entries" in body:
        return {"count": body.get("count")}
    return _capped(body)


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
