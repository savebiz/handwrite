"""
scripts/run_test_run_suite.py — Unified Test Run Suite Harness

Executes baseline extraction, advanced pipeline execution, comparative evaluation,
and reviewer workflow walkthrough in a single unified command.

Outputs logs to data/<test_run_id>/logs/suite.log.
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("./vendor"))
sys.path.insert(0, os.path.abspath("./.venv/Lib/site-packages"))
user_site = os.path.expanduser(r"~\AppData\Roaming\Python\Python313\site-packages")
if os.path.exists(user_site):
    sys.path.insert(0, user_site)

from scripts.run_test_run_baseline import run_baseline
from scripts.run_test_run_advanced import run_advanced
from scripts.run_test_run_comparison import run_comparison
from scripts.run_reviewer_walkthrough import run_walkthrough


def run_suite(test_run_id: str = "test-run-01"):
    print("==========================================================================")
    print(f"HANDWRITE VERIFY — UNIFIED TEST RUN SUITE HARNESS ({test_run_id})")
    print("==========================================================================")
    
    suite_start = time.time()

    # Step 1: Baseline Execution
    print("\n>>> STEP 1: Executing Single-Pass Baseline Workflow...")
    run_baseline()

    # Step 2: Advanced Pipeline Execution
    print("\n>>> STEP 2: Executing Multi-Stage Advanced Agentic Pipeline...")
    run_advanced()

    # Step 3: Comparative Evaluation
    print("\n>>> STEP 3: Executing Baseline vs. Advanced Comparative Evaluation...")
    run_comparison()

    # Step 4: Reviewer Workflow Walkthrough
    print("\n>>> STEP 4: Executing End-to-End Reviewer Workflow Walkthrough...")
    run_walkthrough()

    suite_duration = time.time() - suite_start

    print("==========================================================================")
    print(f"UNIFIED TEST SUITE HARNESS COMPLETED SUCCESSFULLY ({test_run_id})")
    print("==========================================================================")
    print(f"Total Suite Execution Time: {suite_duration:.4f} seconds")
    print("Log & Summary Directory:    data/test-run-01/outputs/")
    print("==========================================================================\n")


if __name__ == "__main__":
    test_run_arg = sys.argv[1] if len(sys.argv) > 1 else "test-run-01"
    run_suite(test_run_arg)
