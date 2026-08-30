"""
scripts/run_baseline_tests.py — Standalone Baseline Test Runner

Executes unit tests for the baseline extraction workflow without pytest dependency.
"""
import sys
import os
import json

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("./vendor"))
sys.path.insert(0, os.path.abspath("./.venv/Lib/site-packages"))
user_site = os.path.expanduser(r"~\AppData\Roaming\Python\Python313\site-packages")
if os.path.exists(user_site):
    sys.path.insert(0, user_site)

from evaluation.baseline import run_baseline_extraction, run_baseline_evaluation
from app.shared.schemas import DocumentRecord, RecordStatusEnum


MANIFEST_PATH = "data/manifests/manifest.json"


def run_tests():
    print("--- Running Baseline Extraction Unit Tests ---")
    passed = 0
    total = 0

    assert os.path.exists(MANIFEST_PATH), f"Manifest not found: {MANIFEST_PATH}"
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    samples = manifest["samples"]

    # Test 1: Baseline output schema compliance
    total += 1
    sample_fi = next(s for s in samples if s["document_id"] == "FI-001")
    rec = run_baseline_extraction(sample_fi)
    assert isinstance(rec, DocumentRecord)
    assert rec.document_id == "FI-001"
    assert len(rec.field_results) == 10
    print("[PASS] Test 1: Baseline returns valid DocumentRecord schema")
    passed += 1

    # Test 2: Unverified values marking
    total += 1
    for field in rec.field_results:
        assert field.verification_checks == [], f"Field {field.field_name} has verification checks"
    print("[PASS] Test 2: Baseline marks all values unverified (verification_checks = [])")
    passed += 1

    # Test 3: Never claims approval
    total += 1
    for s in samples:
        r = run_baseline_extraction(s)
        assert r.record_status == RecordStatusEnum.AWAITING_REVIEW, \
            f"{s['document_id']} claimed status {r.record_status}"
    print("[PASS] Test 3: Baseline NEVER claims approval (record_status = AWAITING_REVIEW)")
    passed += 1

    # Test 4: Zero fabrication on null values
    total += 1
    sample_fi_extreme = next(s for s in samples if s["document_id"] == "FI-006")
    rec_extreme = run_baseline_extraction(sample_fi_extreme)
    inspector = next(f for f in rec_extreme.field_results if f.field_name == "inspector_name")
    assert inspector.proposed_value is None, f"Fabricated '{inspector.proposed_value}' for missing inspector"
    
    sample_co_missing = next(s for s in samples if s["document_id"] == "CO-006")
    rec_co = run_baseline_extraction(sample_co_missing)
    email = next(f for f in rec_co.field_results if f.field_name == "email_address")
    assert email.proposed_value is None, f"Fabricated '{email.proposed_value}' for missing email"
    print("[PASS] Test 4: Zero fabrication policy (null values remain None)")
    passed += 1

    # Test 5: Machine-readable output & metadata generation
    total += 1
    out_file = "outputs/baseline_results.json"
    results = run_baseline_evaluation(manifest_path=MANIFEST_PATH, output_path=out_file)
    assert os.path.exists(out_file)
    assert "run_metadata" in results
    assert "records" in results
    assert len(results["records"]) == 12
    meta = results["run_metadata"]
    assert meta["dataset_version"] == "2.0.0"
    assert meta["total_samples"] == 12
    assert meta["total_fields"] == 126
    assert "verified_field_accuracy_percent" in meta
    print(f"[PASS] Test 5: Machine-readable output generated with dataset v{meta['dataset_version']} metadata")
    passed += 1

    print(f"\n[SUCCESS] ALL BASELINE TESTS PASSED CLEANLY ({passed}/{total}).")


if __name__ == "__main__":
    run_tests()
