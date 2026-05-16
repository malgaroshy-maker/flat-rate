"""API performance benchmarking — SLA validation and concurrent load testing.

Inspired by API Tester agent: performance excellence standards.
"""

from __future__ import annotations

import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

from fastapi.testclient import TestClient


@dataclass
class PerformanceReport:
    endpoint: str = ""
    method: str = "GET"
    iterations: int = 0
    mean_ms: float = 0.0
    median_ms: float = 0.0
    p95_ms: float = 0.0
    p99_ms: float = 0.0
    min_ms: float = 0.0
    max_ms: float = 0.0
    sla_ms: float = 0.0
    sla_passed: bool = False
    concurrent_max_ms: float = 0.0
    concurrent_mean_ms: float = 0.0
    concurrent_failures: int = 0


def _percentile(sorted_values: list[float], p: float) -> float:
    if not sorted_values:
        return 0.0
    idx = (p / 100.0) * (len(sorted_values) - 1)
    lo = int(idx)
    hi = min(lo + 1, len(sorted_values) - 1)
    frac = idx - lo
    return sorted_values[lo] * (1.0 - frac) + sorted_values[hi] * frac


def benchmark_endpoint(
    client: TestClient,
    method: str,
    endpoint: str,
    params: dict | None = None,
    json_body: dict | None = None,
    iterations: int = 10,
    sla_ms: float = 200.0,
) -> PerformanceReport:
    timings: list[float] = []
    for _ in range(iterations):
        start = time.perf_counter()
        if method == "POST":
            if json_body:
                client.post(endpoint, json=json_body, params=params or {})
            else:
                client.post(endpoint, params=params or {})
        else:
            client.get(endpoint, params=params or {})
        elapsed = (time.perf_counter() - start) * 1000
        timings.append(elapsed)

    sorted_t = sorted(timings)
    mean_val = statistics.mean(timings)
    median_val = statistics.median(timings)

    return PerformanceReport(
        endpoint=endpoint,
        method=method,
        iterations=iterations,
        mean_ms=round(mean_val, 2),
        median_ms=round(median_val, 2),
        p95_ms=round(_percentile(sorted_t, 95), 2),
        p99_ms=round(_percentile(sorted_t, 99), 2),
        min_ms=round(min(timings), 2),
        max_ms=round(max(timings), 2),
        sla_ms=sla_ms,
        sla_passed=median_val <= sla_ms,
    )


def benchmark_concurrent(
    client_factory,
    method: str,
    endpoint: str,
    params: dict | None = None,
    json_body: dict | None = None,
    concurrency: int = 10,
    sla_ms: float = 400.0,
) -> PerformanceReport:
    def _single_request():
        client = client_factory()
        start = time.perf_counter()
        if method == "POST":
            if json_body:
                client.post(endpoint, json=json_body, params=params or {})
            else:
                client.post(endpoint, params=params or {})
        else:
            client.get(endpoint, params=params or {})
        return (time.perf_counter() - start) * 1000

    timings: list[float] = []
    failures = 0
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(_single_request) for _ in range(concurrency)]
        for f in as_completed(futures):
            try:
                timings.append(f.result())
            except Exception:
                failures += 1

    if not timings:
        return PerformanceReport(
            endpoint=endpoint,
            method=method,
            concurrent_failures=failures,
        )

    sorted_t = sorted(timings)
    return PerformanceReport(
        endpoint=endpoint,
        method=method,
        iterations=concurrency,
        concurrent_mean_ms=round(statistics.mean(timings), 2),
        concurrent_max_ms=round(max(timings), 2),
        concurrent_failures=failures,
        sla_ms=sla_ms,
        sla_passed=max(timings) <= sla_ms,
    )
