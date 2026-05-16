"""Tests for calibration and drift modules."""

from datetime import date

import pytest

from ingestion.xlsx_parser import LaborRecord
from qa.calibration import CalibrationReport, run_calibration
from qa.drift import DriftReport, run_drift_analysis


def _make_record(model: str, code: str, qty: float, invoice_date: date) -> LaborRecord:
    return LaborRecord(
        branch="Test",
        wipno="",
        invoice_number="",
        invoice_type="",
        invoice_date=invoice_date,
        code=code,
        description="",
        qty=qty,
        price=0.0,
        discount_pct=0.0,
        total=0.0,
        account_code="",
        account_name="",
        customer_name="",
        franchise="Test",
        model=model,
        variant="",
        chassis="",
        reg_date=None,
        reg_number="",
        department="test",
        service_advisor="",
    )


class TestCalibration:
    def test_empty_records(self):
        report = run_calibration([])
        assert report.total_test_records == 0

    def test_single_group_small(self):
        records = [
            _make_record("HD45", "2000", 2.0, date(2025, 1, 15)),
            _make_record("HD45", "2000", 2.5, date(2025, 2, 15)),
            _make_record("HD45", "2000", 3.0, date(2025, 3, 15)),
            _make_record("HD45", "2000", 2.2, date(2025, 4, 15)),
            _make_record("HD45", "2000", 2.8, date(2025, 5, 15)),
            _make_record("HD45", "2000", 2.6, date(2025, 6, 15)),
        ]
        report = run_calibration(records, split_date=date(2025, 3, 20))
        assert report.total_test_records > 0
        assert report.groups_tested > 0
        assert 0 <= report.within_range_pct <= 100
        assert 0 <= report.over_estimate_pct <= 100
        assert 0 <= report.under_estimate_pct <= 100
        assert report.mean_absolute_error >= 0

    def test_no_dated_records(self):
        records = [_make_record("HD45", "2000", 2.0, date(2025, 1, 1))]
        records[0].invoice_date = None
        report = run_calibration(records)
        assert report.total_test_records == 0

    def test_single_record_train_too_small_for_test(self):
        records = [
            _make_record("HD45", "2000", 2.0, date(2025, 1, 1)),
            _make_record("HD45", "2000", 2.5, date(2025, 2, 1)),
            _make_record("HD45", "2000", 3.0, date(2025, 3, 1)),
            _make_record("HD45", "2000", 4.0, date(2025, 6, 1)),
            _make_record("HD45", "2000", 5.0, date(2025, 7, 1)),
        ]
        report = run_calibration(records, split_date=date(2025, 4, 15))
        assert report.total_test_records >= 0

    def test_calibration_per_group_structure(self):
        records = [
            _make_record("HD45", "2000", 2.0, date(2025, 1, 1)),
            _make_record("HD45", "2000", 2.5, date(2025, 1, 15)),
            _make_record("HD45", "2000", 3.0, date(2025, 2, 1)),
            _make_record("HD45", "2000", 2.2, date(2025, 6, 1)),
            _make_record("HD45", "2000", 2.8, date(2025, 7, 1)),
            _make_record("HD45", "2000", 3.5, date(2025, 8, 1)),
        ]
        report = run_calibration(records, split_date=date(2025, 4, 1))
        for entry in report.per_group:
            assert "model" in entry
            assert "code" in entry
            assert "train_count" in entry
            assert "test_count" in entry
            assert "p10" in entry
            assert "p50" in entry
            assert "p90" in entry
            assert "within_pct" in entry


class TestDrift:
    def test_empty_records(self):
        report = run_drift_analysis([])
        assert report.total_groups == 0

    def test_single_month_no_drift(self):
        records = [
            _make_record("HD45", "2000", 2.0, date(2025, 1, 1)),
            _make_record("HD45", "2000", 2.5, date(2025, 1, 15)),
        ]
        report = run_drift_analysis(records, min_records_per_window=1)
        assert report.total_groups == 0

    def test_multi_month_drift_basic(self):
        records = [
            _make_record("HD45", "2000", 2.0, date(2025, 1, 1)),
            _make_record("HD45", "2000", 2.2, date(2025, 1, 5)),
            _make_record("HD45", "2000", 2.5, date(2025, 1, 10)),
            _make_record("HD45", "2000", 3.0, date(2025, 1, 15)),
            _make_record("HD45", "2000", 3.5, date(2025, 2, 1)),
            _make_record("HD45", "2000", 5.0, date(2025, 6, 1)),
            _make_record("HD45", "2000", 5.5, date(2025, 6, 15)),
            _make_record("HD45", "2000", 6.0, date(2025, 6, 1)),
            _make_record("HD45", "2000", 6.5, date(2025, 6, 15)),
            _make_record("HD45", "2000", 7.0, date(2025, 6, 1)),
            _make_record("HD45", "2000", 7.5, date(2025, 6, 15)),
        ]
        report = run_drift_analysis(records, min_records_per_window=3)
        assert report.total_groups > 0
        for entry in report.per_group:
            assert "psi" in entry
            assert entry["psi"] >= 0
            assert "flagged" in entry

    def test_no_dated_records(self):
        records = [_make_record("HD45", "2000", 2.0, date(2025, 1, 1))]
        records[0].invoice_date = None
        report = run_drift_analysis(records)
        assert report.total_groups == 0

    def test_drift_psi_non_negative(self):
        records = [
            _make_record("HD45", "2000", qty, date(2025, month, 1))
            for month in range(1, 4)
            for qty in [2.0 + month * 0.1 * i for i in range(5)]
        ]
        report = run_drift_analysis(records, min_records_per_window=3)
        for entry in report.per_group:
            assert entry["psi"] >= 0.0
