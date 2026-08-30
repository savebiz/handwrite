"""
tests/test_baseline.py — Unit Tests for Baseline Extraction Workflow

Validates that the baseline extractor:
  1. Conforms to DocumentRecord schema.
  2. Marks all field values unverified (verification_checks = []).
  3. Never claims approval (record_status is ALWAYS AWAITING_REVIEW).
  4. Never fabricates missing handwriting (null values remain None).
  5. Uses dataset_version 2.0.0.
  6. Generates machine-readable output to outputs/baseline_results.json with run metadata.
"""

import os
import sys
import json
import pytest

sys.path.insert(0, os.path.abspath("."))
from evaluation.baseline import run_baseline_extraction, run_baseline_evaluation
from app.shared.schemas import DocumentRecord, RecordStatusEnum, DecisionEnum


@pytest.fixture(scope="module")
def manifest():
    manifest_path = "data/manifests/manifest.json"
    assert os.path.exists(manifest_path), f"Manifest missing at {manifest_path}"
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def sample_fi(manifest):
    return next(s for s in manifest["samples"] if s["document_id"] == "FI-001")


@pytest.fixture(scope="module")
def sample_fi_extreme(manifest):
    return next(s for s in manifest["samples"] if s["document_id"] == "FI-006")


@pytest.fixture(scope="module")
def sample_co_missing_email(manifest):
    return next(s for s in manifest["samples"] if s["document_id"] == "CO-006")


def test_baseline_extraction_returns_document_record(sample_fi):
    """Baseline extraction must return a valid DocumentRecord instance."""
    rec = run_baseline_extraction(sample_fi)
    assert isinstance(rec, DocumentRecord)
    assert rec.document_id == "FI-001"
    assert len(rec.field_results) == 10


def test_baseline_marks_values_unverified(sample_fi):
    """All field results must have empty verification_checks list (unverified)."""
    rec = run_baseline_extraction(sample_fi)
    for f in rec.field_results:
        assert f.verification_checks == [], f"Field {f.field_name} had verification checks"


def test_baseline_never_claims_approval(sample_fi, sample_fi_extreme):
    """Baseline record_status must ALWAYS be AWAITING_REVIEW, never APPROVED."""
    rec_clean = run_baseline_extraction(sample_fi)
    assert rec_clean.record_status == RecordStatusEnum.AWAITING_REVIEW, \
        f"Baseline clean record claimed status {rec_clean.record_status}"

    rec_extreme = run_baseline_extraction(sample_fi_extreme)
    assert rec_extreme.record_status == RecordStatusEnum.AWAITING_REVIEW, \
        f"Baseline extreme record claimed status {rec_extreme.record_status}"


def test_baseline_zero_fabrication_on_null_values(sample_fi_extreme, sample_co_missing_email):
    """Missing handwriting fields (gold null) must produce proposed_value = None."""
    rec_fi = run_baseline_extraction(sample_fi_extreme)
    inspector_field = next(f for f in rec_fi.field_results if f.field_name == "inspector_name")
    assert inspector_field.proposed_value is None, \
        f"Fabricated text '{inspector_field.proposed_value}' for null inspector_name"

    rec_co = run_baseline_extraction(sample_co_missing_email)
    email_field = next(f for f in rec_co.field_results if f.field_name == "email_address")
    assert email_field.proposed_value is None, \
        f"Fabricated text '{email_field.proposed_value}' for null email_address"


def test_baseline_evaluation_produces_machine_readable_output(tmp_path):
    """run_baseline_evaluation must create machine-readable JSON with run metadata."""
    out_file = str(tmp_path / "test_baseline_results.json")
    results = run_baseline_evaluation(output_path=out_file)

    assert os.path.exists(out_file)
    assert "run_metadata" in results
    assert "records" in results
    assert len(results["records"]) == 12

    meta = results["run_metadata"]
    assert meta["dataset_version"] == "2.0.0"
    assert meta["total_samples"] == 12
    assert meta["total_fields"] == 126
    assert "verified_field_accuracy_percent" in meta
    assert "duration_seconds" in meta
    assert meta["cost_usd"] == 0.0
