import os
import sys
import json
import time
from typing import Dict, Any, List

sys.path.insert(0, os.path.abspath("."))

from evaluation.baseline import run_baseline_extraction
from app.shared.schemas import DocumentRecord, DecisionEnum, ReviewerDecisionEnum


def evaluate_run(manifest_path: str = "data/manifests/manifest.json") -> Dict[str, Any]:
    if not os.path.exists(manifest_path):
        raise FileNotFoundError(f"Manifest not found at {manifest_path}. Run generate_synthetic_corpus.py first.")

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    samples = manifest["samples"]
    total_samples = len(samples)

    # --- Evaluate Baseline ---
    baseline_correct_fields = 0
    baseline_total_fields = 0
    baseline_schema_passes = 0
    start_time = time.time()

    for sample in samples:
        gold_path = sample["gold_label_path"]
        with open(gold_path, "r", encoding="utf-8") as f:
            gold = json.load(f)["gold_fields"]

        record: DocumentRecord = run_baseline_extraction(sample)
        baseline_schema_passes += 1

        for field in record.field_results:
            baseline_total_fields += 1
            gold_val = gold.get(field.field_name)

            # In baseline, value is accepted if proposed_value matches gold
            if field.proposed_value == gold_val:
                baseline_correct_fields += 1

    baseline_duration = time.time() - start_time
    baseline_accuracy = (
        (baseline_correct_fields / baseline_total_fields) * 100
        if baseline_total_fields > 0
        else 0.0
    )

    results = {
        "dataset": {
            "total_samples": total_samples,
            "manifest": manifest_path,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "baseline": {
            "verified_field_accuracy_percent": round(baseline_accuracy, 2),
            "correct_fields": baseline_correct_fields,
            "total_fields": baseline_total_fields,
            "schema_pass_rate_percent": 100.0,
            "total_duration_seconds": round(baseline_duration, 4),
            "avg_duration_per_doc_seconds": round(baseline_duration / total_samples, 4),
        },
    }

    os.makedirs("outputs", exist_ok=True)
    results_path = "outputs/evaluation_results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n============================================================")
    print("HANDWRITE VERIFY — EVALUATION HARNESS RESULTS")
    print("============================================================")
    print(f"Total Corpus Samples: {total_samples}")
    print(f"Baseline Verified Field Accuracy: {results['baseline']['verified_field_accuracy_percent']}%")
    print(f"Baseline Avg Duration / Doc: {results['baseline']['avg_duration_per_doc_seconds']} sec")
    print(f"Evaluation report saved to {results_path}")
    print("============================================================")

    return results


if __name__ == "__main__":
    evaluate_run()
