"""Pipeline observability: per-stage latency tracking.

Inspired by AI Engineer: inference latency tracking, bottleneck identification.
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Callable


_STAGE_TIMINGS: dict[str, list[float]] = defaultdict(list)


def reset_timings() -> None:
    _STAGE_TIMINGS.clear()


def track_latency(stage_name: str) -> Callable:
    """Decorator that records execution time for a pipeline stage."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                elapsed = time.perf_counter() - start
                _STAGE_TIMINGS[stage_name].append(round(elapsed, 6))

        return wrapper

    return decorator


@dataclass
class LatencyReport:
    stages: dict[str, dict] = field(default_factory=dict)
    total_mean: float = 0.0


def _percentile(sorted_values: list[float], p: float) -> float:
    if not sorted_values:
        return 0.0
    idx = (p / 100.0) * (len(sorted_values) - 1)
    lo = int(idx)
    hi = min(lo + 1, len(sorted_values) - 1)
    frac = idx - lo
    return sorted_values[lo] * (1.0 - frac) + sorted_values[hi] * frac


def get_latency_report() -> LatencyReport:
    """Generate latency statistics for all tracked pipeline stages."""
    report = LatencyReport()
    total_times: list[float] = []

    for stage, timings in sorted(_STAGE_TIMINGS.items()):
        if not timings:
            continue
        sorted_t = sorted(timings)
        report.stages[stage] = {
            "count": len(timings),
            "mean": round(sum(timings) / len(timings), 6),
            "p50": round(_percentile(sorted_t, 50), 6),
            "p95": round(_percentile(sorted_t, 95), 6),
            "p99": round(_percentile(sorted_t, 99), 6),
            "min": round(min(timings), 6),
            "max": round(max(timings), 6),
            "total": round(sum(timings), 4),
        }
        total_times.append(sum(timings))

    if total_times:
        report.total_mean = round(sum(total_times) / len(total_times), 4)

    return report
