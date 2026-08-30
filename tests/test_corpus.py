"""
tests/test_corpus.py — Manifest & Gold-Label Validation Tests

Validates the synthetic evaluation corpus for structural integrity,
field completeness, and schema compliance. Run via pytest or
scripts/run_corpus_tests.py.
"""
import os
import sys
import json
import re
from datetime import datetime

import pytest

sys.path.insert(0, os.path.abspath("."))
from app.shared.metadata import (
    get_metadata_for_family,
    FIELD_INSPECTION_METADATA,
    CUSTOMER_ONBOARDING_METADATA,
)
from app.shared.schemas import DocumentType


# ─── Fixtures ──────────────────────────────────────────────────

MANIFEST_PATH = os.path.join("data", "manifests", "manifest.json")
GOLD_DIR = os.path.join("data", "gold-labels")

VALID_DIFFICULTIES = {"clean", "medium", "hard", "extreme"}
VALID_DOC_TYPES = {"field_inspection", "customer_onboarding"}
VALID_FIELD_DIFFICULTIES = {"easy", "medium", "hard"}
VALID_ESCALATION_DECISIONS = {"human_review", "rescan_required"}

FI_FIELD_COUNT = len(FIELD_INSPECTION_METADATA)   # 10
CO_FIELD_COUNT = len(CUSTOMER_ONBOARDING_METADATA)  # 11

FI_FIELD_NAMES = set(FIELD_INSPECTION_METADATA.keys())
CO_FIELD_NAMES = set(CUSTOMER_ONBOARDING_METADATA.keys())


@pytest.fixture(scope="module")
def manifest():
    assert os.path.exists(MANIFEST_PATH), f"Manifest not found at {MANIFEST_PATH}"
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def samples(manifest):
    return manifest["samples"]


# ─── Manifest Structure Tests ─────────────────────────────────


def test_manifest_has_version(manifest):
    """Manifest must include a dataset_version field."""
    assert "dataset_version" in manifest
    assert isinstance(manifest["dataset_version"], str)
    assert len(manifest["dataset_version"]) > 0


def test_manifest_has_data_policy(manifest):
    """Manifest must include a synthetic data policy note."""
    assert "data_policy" in manifest
    policy = manifest["data_policy"].lower()
    assert "synthetic" in policy
    assert "real" not in policy or "zero real" in policy


def test_manifest_sample_count(manifest, samples):
    """Manifest total_samples must match actual samples array length."""
    assert manifest["total_samples"] == len(samples)


def test_manifest_has_12_samples(samples):
    """Corpus must contain exactly 12 samples."""
    assert len(samples) == 12


# ─── Coverage Distribution Tests ──────────────────────────────


def test_document_type_distribution(samples):
    """Must have 6 field_inspection and 6 customer_onboarding."""
    fi_count = sum(1 for s in samples if s["document_type"] == "field_inspection")
    co_count = sum(1 for s in samples if s["document_type"] == "customer_onboarding")
    assert fi_count == 6, f"Expected 6 FI, got {fi_count}"
    assert co_count == 6, f"Expected 6 CO, got {co_count}"


def test_difficulty_distribution(samples):
    """Must have >= 4 clean, >= 4 medium, >= 4 hard/extreme."""
    clean = sum(1 for s in samples if s["difficulty"] == "clean")
    medium = sum(1 for s in samples if s["difficulty"] == "medium")
    hard_or_extreme = sum(1 for s in samples if s["difficulty"] in ("hard", "extreme"))
    assert clean >= 4, f"Expected >= 4 clean, got {clean}"
    assert medium >= 4, f"Expected >= 4 medium, got {medium}"
    assert hard_or_extreme >= 4, f"Expected >= 4 hard/extreme, got {hard_or_extreme}"


def test_extreme_case_exists(samples):
    """At least one sample must be classified as extreme."""
    extreme = [s for s in samples if s["difficulty"] == "extreme"]
    assert len(extreme) >= 1, "No extreme difficulty sample found"


# ─── Per-Sample Structural Tests ──────────────────────────────


def test_all_image_files_exist(samples):
    """Every sample's image_path must reference an existing file."""
    for s in samples:
        path = s["image_path"]
        assert os.path.exists(path), f"Image not found: {path} (doc {s['document_id']})"


def test_all_gold_label_files_exist(samples):
    """Every sample's gold_label_path must reference an existing file."""
    for s in samples:
        path = s["gold_label_path"]
        assert os.path.exists(path), f"Gold label not found: {path} (doc {s['document_id']})"


def test_all_samples_have_required_keys(samples):
    """Every sample must have document_id, document_type, difficulty, image_path,
    gold_label_path, issues, field_difficulty, and expected_escalations."""
    required = {"document_id", "document_type", "difficulty", "image_path",
                "gold_label_path", "issues", "field_difficulty", "expected_escalations"}
    for s in samples:
        missing = required - set(s.keys())
        assert not missing, f"Sample {s['document_id']} missing keys: {missing}"


def test_valid_difficulty_values(samples):
    """Every sample difficulty must be clean/medium/hard/extreme."""
    for s in samples:
        assert s["difficulty"] in VALID_DIFFICULTIES, \
            f"Invalid difficulty '{s['difficulty']}' in {s['document_id']}"


def test_valid_document_types(samples):
    """Every sample document_type must be field_inspection or customer_onboarding."""
    for s in samples:
        assert s["document_type"] in VALID_DOC_TYPES, \
            f"Invalid doc type '{s['document_type']}' in {s['document_id']}"


def test_field_difficulty_labels(samples):
    """Every sample must have field_difficulty with valid values for all fields."""
    for s in samples:
        fd = s.get("field_difficulty", {})
        doc_type = s["document_type"]
        expected_fields = FI_FIELD_NAMES if doc_type == "field_inspection" else CO_FIELD_NAMES
        assert set(fd.keys()) == expected_fields, \
            f"field_difficulty keys mismatch in {s['document_id']}: got {set(fd.keys())}, expected {expected_fields}"
        for fname, diff in fd.items():
            assert diff in VALID_FIELD_DIFFICULTIES, \
                f"Invalid field difficulty '{diff}' for {fname} in {s['document_id']}"


def test_expected_escalations_structure(samples):
    """Every expected_escalation entry must have field, expected_decision, reason."""
    for s in samples:
        for esc in s.get("expected_escalations", []):
            assert "field" in esc, f"Missing 'field' in escalation for {s['document_id']}"
            assert "expected_decision" in esc, f"Missing 'expected_decision' in escalation for {s['document_id']}"
            assert "reason" in esc, f"Missing 'reason' in escalation for {s['document_id']}"
            assert esc["expected_decision"] in VALID_ESCALATION_DECISIONS, \
                f"Invalid expected_decision '{esc['expected_decision']}' in {s['document_id']}"


# ─── Gold Label Content Tests ─────────────────────────────────


def test_gold_label_field_counts(samples):
    """Gold labels must have the correct number of fields per doc type."""
    for s in samples:
        with open(s["gold_label_path"], "r", encoding="utf-8") as f:
            gold = json.load(f)
        fields = gold["gold_fields"]
        doc_type = s["document_type"]
        expected = FI_FIELD_COUNT if doc_type == "field_inspection" else CO_FIELD_COUNT
        assert len(fields) == expected, \
            f"Gold label {s['document_id']} has {len(fields)} fields, expected {expected}"


def test_gold_label_field_names_match_spec(samples):
    """Gold label field names must exactly match the metadata dictionary."""
    for s in samples:
        with open(s["gold_label_path"], "r", encoding="utf-8") as f:
            gold = json.load(f)
        field_names = set(gold["gold_fields"].keys())
        doc_type = s["document_type"]
        expected = FI_FIELD_NAMES if doc_type == "field_inspection" else CO_FIELD_NAMES
        assert field_names == expected, \
            f"Gold label {s['document_id']} field names {field_names} != spec {expected}"


def test_gold_label_required_fields_present(samples):
    """Required fields must not be null/empty unless documented as missing."""
    documented_missing = {
        "FI-006": {"inspector_name"},  # Documented missing mandatory field
    }
    for s in samples:
        with open(s["gold_label_path"], "r", encoding="utf-8") as f:
            gold = json.load(f)
        doc_type = DocumentType(s["document_type"])
        meta = get_metadata_for_family(doc_type)
        allowed_missing = documented_missing.get(s["document_id"], set())
        for fname, fmeta in meta.items():
            if fmeta.required and fname not in allowed_missing:
                val = gold["gold_fields"].get(fname)
                assert val is not None and str(val).strip() != "", \
                    f"Required field '{fname}' is null/empty in {s['document_id']}"


def test_gold_label_date_fields_valid(samples):
    """Date fields must be valid ISO-8601 strings."""
    date_fields = {
        "field_inspection": ["inspection_date", "followup_date"],
        "customer_onboarding": ["application_date"],
    }
    for s in samples:
        with open(s["gold_label_path"], "r", encoding="utf-8") as f:
            gold = json.load(f)
        for date_field in date_fields.get(s["document_type"], []):
            val = gold["gold_fields"].get(date_field)
            if val is not None:
                try:
                    datetime.strptime(val, "%Y-%m-%d")
                except ValueError:
                    pytest.fail(f"Invalid date '{val}' in {s['document_id']}.{date_field}")


def test_gold_label_enum_fields_valid(samples):
    """Enum fields must contain values from the controlled vocabulary."""
    for s in samples:
        with open(s["gold_label_path"], "r", encoding="utf-8") as f:
            gold = json.load(f)
        doc_type = DocumentType(s["document_type"])
        meta = get_metadata_for_family(doc_type)
        for fname, fmeta in meta.items():
            if fmeta.allowed_values:
                val = gold["gold_fields"].get(fname)
                if val is not None:
                    assert val in fmeta.allowed_values, \
                        f"Invalid enum '{val}' for {fname} in {s['document_id']}. Allowed: {fmeta.allowed_values}"


def test_gold_label_pattern_fields_valid(samples):
    """Pattern fields must match their regex."""
    for s in samples:
        with open(s["gold_label_path"], "r", encoding="utf-8") as f:
            gold = json.load(f)
        doc_type = DocumentType(s["document_type"])
        meta = get_metadata_for_family(doc_type)
        for fname, fmeta in meta.items():
            if fmeta.pattern:
                val = gold["gold_fields"].get(fname)
                if val is not None:
                    assert re.match(fmeta.pattern, val), \
                        f"Pattern mismatch for {fname}='{val}' in {s['document_id']}. Pattern: {fmeta.pattern}"


def test_no_forward_slash_in_paths(samples):
    """Image and gold label paths must use forward slashes for cross-platform compatibility."""
    for s in samples:
        assert "\\" not in s["image_path"], \
            f"Backslash in image_path for {s['document_id']}: {s['image_path']}"
        assert "\\" not in s["gold_label_path"], \
            f"Backslash in gold_label_path for {s['document_id']}: {s['gold_label_path']}"
