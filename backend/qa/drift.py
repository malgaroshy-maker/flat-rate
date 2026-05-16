"""Drift detection: PSI (Population Stability Index) across time windows.

Inspired by Model QA Specialist: variable stability monitoring.
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from ingestion.xlsx_parser import LaborRecord, parse_xlsx


@dataclass
class DriftReport:
    total_groups: int = 0
    flagged_groups: int = 0
    psi_threshold: float = 0.25
    per_group: list[dict] = field(default_factory=list)


def _percentile(sorted_values: list[float], p: float) -> float:
    if not sorted_values:
        return 0.0
    idx = (p / 100.0) * (len(sorted_values) - 1)
    lo = int(idx)
    hi = min(lo + 1, len(sorted_values) - 1)
    frac = idx - lo
    return sorted_values[lo] * (1.0 - frac) + sorted_values[hi] * frac


def _compute_psi(expected: list[float], actual: list[float], bins: int = 10) -> float:
    if not expected or not actual:
        return 0.0
    n_bins = min(bins, len(expected), len(actual))
    if n_bins < 2:
        return 0.0

    all_vals = sorted(expected + actual)
    breakpoints = [_percentile(all_vals, p) for p in [100.0 * i / n_bins for i in range(n_bins + 1)]]

    exp_counts = [0] * n_bins
    act_counts = [0] * n_bins
    for v in expected:
        for i in range(n_bins):
            if breakpoints[i] <= v <= breakpoints[i + 1]:
                exp_counts[i] += 1
                break
    for v in actual:
        for i in range(n_bins):
            if breakpoints[i] <= v <= breakpoints[i + 1]:
                act_counts[i] += 1
                break

    exp_pct = [(c + 1) / (sum(exp_counts) + n_bins) for c in exp_counts]
    act_pct = [(c + 1) / (sum(act_counts) + n_bins) for c in act_counts]

    psi = sum((a - e) * math.log(a / e) for a, e in zip(act_pct, exp_pct) if a > 0 and e > 0)
    return round(psi, 6)


def _month_key(d: date) -> str:
    return d.strftime("%Y-%m")


def run_drift_analysis(
    records: list[LaborRecord],
    min_records_per_window: int = 5,
) -> DriftReport:
    """Compute PSI for each (Model, Code) group across monthly time windows.

    Compares earliest month (baseline) vs latest month for each group.
    Flags groups with PSI >= 0.25.
    """
    dated = [r for r in records if r.invoice_date is not None]
    if not dated:
        return DriftReport()

    monthly: dict[str, dict[tuple[str, str], list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for r in dated:
        monthly[_month_key(r.invoice_date)][(r.model, r.code)].append(r.qty)  # type: ignore[arg-type]

    sorted_months = sorted(monthly.keys())
    if len(sorted_months) < 2:
        return DriftReport()

    baseline_month = sorted_months[0]
    latest_month = sorted_months[-1]

    report = DriftReport()
    all_keys = set(monthly[baseline_month].keys()) | set(monthly[latest_month].keys())

    for key in all_keys:
        baseline = monthly[baseline_month].get(key, [])
        latest = monthly[latest_month].get(key, [])
        if len(baseline) < min_records_per_window or len(latest) < min_records_per_window:
            continue

        psi = _compute_psi(baseline, latest)
        report.total_groups += 1

        entry = {
            "model": key[0],
            "code": key[1],
            "baseline_count": len(baseline),
            "latest_count": len(latest),
            "baseline_month": baseline_month,
            "latest_month": latest_month,
            "psi": psi,
            "flagged": psi >= report.psi_threshold,
        }
        report.per_group.append(entry)
        if entry["flagged"]:
            report.flagged_groups += 1

    report.per_group.sort(key=lambda g: g["psi"], reverse=True)
    return report


def run_drift_from_xlsx(xlsx_path: str | Path) -> DriftReport:
    records = parse_xlsx(xlsx_path)
    return run_drift_analysis(records)
