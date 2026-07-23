#!/usr/bin/env python3
"""Post-deploy smoke test against the live production backend.

Run after every deploy to confirm the new build is actually serving
correctly, not just that Render reports "live". Exits non-zero on any
failure so it can gate a release.

Usage:
    python scripts/smoke_prod.py [base_url]
"""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "https://flat-rate.onrender.com"
TIMEOUT = 30


def _get(path: str) -> tuple[int, dict | None]:
    req = urllib.request.Request(f"{BASE_URL}{path}")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        # 4xx/5xx responses raise instead of returning normally in urllib —
        # surface the status code so callers can assert on it either way.
        try:
            body = json.loads(e.read())
        except Exception:
            body = None
        return e.code, body


def _post_json(path: str, body: dict) -> tuple[int, bytes]:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}{path}", data=data, method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.status, resp.read()


def check_health() -> None:
    status, body = _get("/api/health")
    assert status == 200, f"health returned {status}"
    assert body.get("status") == "ok", f"unexpected health body: {body}"
    print(f"  [ok] /api/health -> {body}")


def check_version() -> None:
    status, body = _get("/api/version")
    assert status == 200, f"version returned {status}"
    print(f"  [ok] /api/version -> {body}")


def check_query() -> None:
    status, body = _get("/api/query")
    # /api/query is POST-only with query params; a bare GET should 405, not 500 —
    # confirms routing didn't break, without needing a full POST call here.
    print(f"  [info] GET /api/query -> {status} (expected 405/404, not 500)")
    assert status < 500, f"query route returned server error {status}"


def check_chat_stream() -> None:
    status, body = _post_json("/api/chat/send", {"message": "smoke test", "lang": "en"})
    assert status == 200, f"chat send returned {status}"
    text = body.decode("utf-8", errors="replace")
    assert "data:" in text, "no SSE data lines in response"
    assert '"status"' in text, "no status event — streaming may be broken"
    print(f"  [ok] /api/chat/send streamed {len(text)} bytes with status events")


def main() -> None:
    print(f"Smoke testing {BASE_URL} ...")
    checks = [
        ("health", check_health),
        ("version", check_version),
        ("query routing", check_query),
        ("chat streaming", check_chat_stream),
    ]
    failures = []
    for name, fn in checks:
        try:
            fn()
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")
            failures.append(name)

    if failures:
        print(f"\nSMOKE TEST FAILED: {', '.join(failures)}")
        sys.exit(1)
    print("\nSMOKE TEST PASSED")


if __name__ == "__main__":
    main()
