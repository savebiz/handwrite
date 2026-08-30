"""
scripts/run_baseline_scoring.py — Dedicated Baseline Scoring CLI

Executes baseline extraction across the evaluation dataset manifest (v2.0.0)
and writes outputs/baseline_results.json.
"""
import sys
import os

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("./vendor"))
sys.path.insert(0, os.path.abspath("./.venv/Lib/site-packages"))
user_site = os.path.expanduser(r"~\AppData\Roaming\Python\Python313\site-packages")
if os.path.exists(user_site):
    sys.path.insert(0, user_site)

from evaluation.baseline import run_baseline_evaluation


def main():
    manifest_path = "data/manifests/manifest.json"
    output_path = "outputs/baseline_results.json"
    
    if len(sys.argv) > 1:
        manifest_path = sys.argv[1]
    if len(sys.argv) > 2:
        output_path = sys.argv[2]

    print(f"Running baseline extraction scoring against: {manifest_path}")
    results = run_baseline_evaluation(manifest_path=manifest_path, output_path=output_path)
    print(f"Scoring complete. Verified Field Accuracy: {results['run_metadata']['verified_field_accuracy_percent']}%")


if __name__ == "__main__":
    main()
