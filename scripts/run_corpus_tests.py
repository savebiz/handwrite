"""
scripts/run_corpus_tests.py — Standalone Corpus Validation Runner

Validates the synthetic evaluation corpus manifest and gold labels
without requiring pytest. Mirrors scripts/run_schema_tests.py pattern.
"""
import sys
import os
import json
import re
from datetime import datetime

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("./vendor"))
sys.path.insert(0, os.path.abspath("./.venv/Lib/site-packages"))
user_site = os.path.expanduser(r"~\AppData\Roaming\Python\Python313\site-packages")
if os.path.exists(user_site):
    sys.path.insert(0, user_site)

from app.shared.metadata import (
    get_metadata_for_family,
    FIELD_INSPECTION_METADATA,
    CUSTOMER_ONBOARDING_METADATA,
)
from app.shared.schemas import DocumentType


MANIFEST_PATH = os.path.join("data", "manifests", "manifest.json")
FI_FIELD_NAMES = set(FIELD_INSPECTION_METADATA.keys())
CO_FIELD_NAMES = set(CUSTOMER_ONBOARDING_METADATA.keys())
VALID_DIFFICULTIES = {"clean", "medium", "hard", "extreme"}
VALID_FIELD_DIFFICULTIES = {"easy", "medium", "hard"}
VALID_ESCALATION_DECISIONS = {"human_review", "rescan_required"}
DOCUMENTED_MISSING = {"FI-006": {"inspector_name"}}


def run_tests():
    print("--- Running Corpus & Gold-Label Validation Tests ---")
    passed = 0
    total = 0

    # Test 1: Manifest exists and parses
    total += 1
    assert os.path.exists(MANIFEST_PATH), f"Manifest not found: {MANIFEST_PATH}"
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    samples = manifest["samples"]
    print("[PASS] Test 1: Manifest file exists and parses as valid JSON")
    passed += 1

    # Test 2: Dataset version present
    total += 1
    assert "dataset_version" in manifest and manifest["dataset_version"]
    print(f"[PASS] Test 2: Dataset version present: {manifest['dataset_version']}")
    passed += 1

    # Test 3: Data policy note present
    total += 1
    assert "data_policy" in manifest
    assert "synthetic" in manifest["data_policy"].lower()
    print("[PASS] Test 3: Synthetic data policy note present")
    passed += 1

    # Test 4: Sample count
    total += 1
    assert manifest["total_samples"] == len(samples) == 12
    print(f"[PASS] Test 4: Sample count matches (12/12)")
    passed += 1

    # Test 5: Document type distribution
    total += 1
    fi_count = sum(1 for s in samples if s["document_type"] == "field_inspection")
    co_count = sum(1 for s in samples if s["document_type"] == "customer_onboarding")
    assert fi_count == 6 and co_count == 6
    print(f"[PASS] Test 5: Document type distribution (6 FI, 6 CO)")
    passed += 1

    # Test 6: Difficulty distribution
    total += 1
    clean = sum(1 for s in samples if s["difficulty"] == "clean")
    medium = sum(1 for s in samples if s["difficulty"] == "medium")
    hard_ext = sum(1 for s in samples if s["difficulty"] in ("hard", "extreme"))
    assert clean >= 4 and medium >= 4 and hard_ext >= 4
    print(f"[PASS] Test 6: Difficulty distribution ({clean} clean, {medium} medium, {hard_ext} hard/extreme)")
    passed += 1

    # Test 7: Extreme case exists
    total += 1
    extreme = [s for s in samples if s["difficulty"] == "extreme"]
    assert len(extreme) >= 1
    print(f"[PASS] Test 7: Extreme case present ({extreme[0]['document_id']})")
    passed += 1

    # Test 8: All image files exist
    total += 1
    for s in samples:
        assert os.path.exists(s["image_path"]), f"Missing image: {s['image_path']}"
    print("[PASS] Test 8: All 12 image files exist on disk")
    passed += 1

    # Test 9: All gold label files exist
    total += 1
    for s in samples:
        assert os.path.exists(s["gold_label_path"]), f"Missing gold label: {s['gold_label_path']}"
    print("[PASS] Test 9: All 12 gold label files exist on disk")
    passed += 1

    # Test 10: All samples have required keys
    total += 1
    required_keys = {"document_id", "document_type", "difficulty", "image_path",
                     "gold_label_path", "issues", "field_difficulty", "expected_escalations"}
    for s in samples:
        missing = required_keys - set(s.keys())
        assert not missing, f"{s['document_id']} missing: {missing}"
    print("[PASS] Test 10: All samples have required metadata keys")
    passed += 1

    # Test 11: Field difficulty labels valid
    total += 1
    for s in samples:
        expected_fields = FI_FIELD_NAMES if s["document_type"] == "field_inspection" else CO_FIELD_NAMES
        fd = s["field_difficulty"]
        assert set(fd.keys()) == expected_fields, f"{s['document_id']} field_difficulty keys mismatch"
        for fname, diff in fd.items():
            assert diff in VALID_FIELD_DIFFICULTIES, f"Invalid: {fname}={diff} in {s['document_id']}"
    print("[PASS] Test 11: All field-level difficulty labels valid")
    passed += 1

    # Test 12: Expected escalations structure
    total += 1
    for s in samples:
        for esc in s["expected_escalations"]:
            assert "field" in esc and "expected_decision" in esc and "reason" in esc
            assert esc["expected_decision"] in VALID_ESCALATION_DECISIONS
    print("[PASS] Test 12: All expected escalation entries well-formed")
    passed += 1

    # Test 13: Gold label field counts match metadata dictionary
    total += 1
    for s in samples:
        with open(s["gold_label_path"], "r", encoding="utf-8") as f:
            gold = json.load(f)
        fields = gold["gold_fields"]
        expected_count = len(FIELD_INSPECTION_METADATA) if s["document_type"] == "field_inspection" else len(CUSTOMER_ONBOARDING_METADATA)
        assert len(fields) == expected_count, f"{s['document_id']}: {len(fields)} != {expected_count}"
    print("[PASS] Test 13: All gold label field counts match spec")
    passed += 1

    # Test 14: Gold label field names match spec
    total += 1
    for s in samples:
        with open(s["gold_label_path"], "r", encoding="utf-8") as f:
            gold = json.load(f)
        field_names = set(gold["gold_fields"].keys())
        expected = FI_FIELD_NAMES if s["document_type"] == "field_inspection" else CO_FIELD_NAMES
        assert field_names == expected, f"{s['document_id']}: {field_names} != {expected}"
    print("[PASS] Test 14: All gold label field names match metadata dictionary")
    passed += 1

    # Test 15: Required fields not null (except documented missing)
    total += 1
    for s in samples:
        with open(s["gold_label_path"], "r", encoding="utf-8") as f:
            gold = json.load(f)
        doc_type = DocumentType(s["document_type"])
        meta = get_metadata_for_family(doc_type)
        allowed = DOCUMENTED_MISSING.get(s["document_id"], set())
        for fname, fmeta in meta.items():
            if fmeta.required and fname not in allowed:
                val = gold["gold_fields"].get(fname)
                assert val is not None and str(val).strip() != "", \
                    f"Required field '{fname}' null/empty in {s['document_id']}"
    print("[PASS] Test 15: Required fields present (documented exceptions honored)")
    passed += 1

    # Test 16: Date fields valid ISO-8601
    total += 1
    date_fields_map = {
        "field_inspection": ["inspection_date", "followup_date"],
        "customer_onboarding": ["application_date"],
    }
    for s in samples:
        with open(s["gold_label_path"], "r", encoding="utf-8") as f:
            gold = json.load(f)
        for df in date_fields_map.get(s["document_type"], []):
            val = gold["gold_fields"].get(df)
            if val is not None:
                datetime.strptime(val, "%Y-%m-%d")  # Raises on invalid
    print("[PASS] Test 16: All date fields are valid ISO-8601")
    passed += 1

    # Test 17: Enum fields in controlled vocabulary
    total += 1
    for s in samples:
        with open(s["gold_label_path"], "r", encoding="utf-8") as f:
            gold = json.load(f)
        doc_type = DocumentType(s["document_type"])
        meta = get_metadata_for_family(doc_type)
        for fname, fmeta in meta.items():
            if fmeta.allowed_values:
                val = gold["gold_fields"].get(fname)
                if val is not None:
                    assert val in fmeta.allowed_values, f"Invalid enum: {fname}='{val}' in {s['document_id']}"
    print("[PASS] Test 17: All enum fields match controlled vocabulary")
    passed += 1

    # Test 18: Pattern fields match regex
    total += 1
    for s in samples:
        with open(s["gold_label_path"], "r", encoding="utf-8") as f:
            gold = json.load(f)
        doc_type = DocumentType(s["document_type"])
        meta = get_metadata_for_family(doc_type)
        for fname, fmeta in meta.items():
            if fmeta.pattern:
                val = gold["gold_fields"].get(fname)
                if val is not None:
                    assert re.match(fmeta.pattern, val), f"Pattern fail: {fname}='{val}' in {s['document_id']}"
    print("[PASS] Test 18: All pattern fields match their regex")
    passed += 1

    # Test 19: Paths use forward slashes
    total += 1
    for s in samples:
        assert "\\" not in s["image_path"], f"Backslash in {s['document_id']} image_path"
        assert "\\" not in s["gold_label_path"], f"Backslash in {s['document_id']} gold_label_path"
    print("[PASS] Test 19: All paths use forward slashes")
    passed += 1

    print(f"\n[SUCCESS] ALL CORPUS VALIDATION TESTS PASSED CLEANLY ({passed}/{total}).")


if __name__ == "__main__":
    run_tests()
