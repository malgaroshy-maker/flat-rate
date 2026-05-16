"""RAG Quality Assurance — Model QA Specialist + AI Engineer patterns.

Calibration testing: validates that P10/P50/P90 confidence intervals
are actually calibrated against held-out historical data.
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional

from ingestion.xlsx_parser import LaborRecord, parse_xlsx


@dataclass
class CalibrationReport:
    within_range_pct: float = 0.0
    over_estimate_pct: float = 0.0
    under_estimate_pct: float = 0.0
    total_test_records: int = 0
    groups_tested: int = 0
    mean_absolute_error: float = 0.0
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
    """Population Stability Index between two distributions."""
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


def run_calibration(
    records: list[LaborRecord],
    split_date: Optional[date] = None,
) -> CalibrationReport:
    """Split records by date into train/test, compare predicted ranges vs actuals.

    If split_date is None, uses the median date of all records.
    """
    dated = [r for r in records if r.invoice_date is not None]
    if not dated:
        return CalibrationReport()

    if split_date is None:
        all_dates = sorted(r.invoice_date for r in dated)  # type: ignore[arg-type]
        split_date = all_dates[len(all_dates) // 2]

    train = [r for r in dated if r.invoice_date < split_date]  # type: ignore[operator]
    test = [r for r in dated if r.invoice_date >= split_date]  # type: ignore[operator]

    train_groups: dict[tuple[str, str], list[float]] = defaultdict(list)
    for r in train:
        train_groups[(r.model, r.code)].append(r.qty)

    test_groups: dict[tuple[str, str], list[float]] = defaultdict(list)
    for r in test:
        test_groups[(r.model, r.code)].append(r.qty)

    report = CalibrationReport()
    within_count = 0
    over_count = 0
    under_count = 0
    abs_errors: list[float] = []

    for (model, code), test_qtys in test_groups.items():
        train_qtys = train_groups.get((model, code), [])
        if len(train_qtys) < 3:
            continue

        sorted_train = sorted(train_qtys)
        p10 = _percentile(sorted_train, 10)
        p50 = _percentile(sorted_train, 50)
        p90 = _percentile(sorted_train, 90)

        for actual in test_qtys:
            report.total_test_records += 1
            if p10 <= actual <= p90:
                within_count += 1
            elif actual > p90:
                over_count += 1
            else:
                under_count += 1
            abs_errors.append(abs(actual - p50))

        report.groups_tested += 1
        report.per_group.append({
            "model": model,
            "code": code,
            "train_count": len(train_qtys),
            "test_count": len(test_qtys),
            "p10": round(p10, 2),
            "p50": round(p50, 2),
            "p90": round(p90, 2),
            "within_pct": round(
                sum(1 for a in test_qtys if p10 <= a <= p90) / len(test_qtys) * 100, 1
            ) if test_qtys else 0.0,
        })

    if report.total_test_records > 0:
        report.within_range_pct = round(within_count / report.total_test_records * 100, 1)
        report.over_estimate_pct = round(over_count / report.total_test_records * 100, 1)
        report.under_estimate_pct = round(under_count / report.total_test_records * 100, 1)
        report.mean_absolute_error = round(sum(abs_errors) / len(abs_errors), 2)

    return report


def run_calibration_from_xlsx(xlsx_path: str | Path) -> CalibrationReport:
    records = parse_xlsx(xlsx_path)
    return run_calibration(records)
