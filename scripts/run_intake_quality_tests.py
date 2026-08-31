"""
scripts/run_intake_quality_tests.py — Standalone Runner for Enhanced Intake & Quality Stage Tests
"""

import sys
import os

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("./vendor"))
sys.path.insert(0, os.path.abspath("./.venv/Lib/site-packages"))
user_site = os.path.expanduser(r"~\AppData\Roaming\Python\Python313\site-packages")
if os.path.exists(user_site):
    sys.path.insert(0, user_site)

from tests.test_intake_quality import run_all_intake_quality_tests

if __name__ == "__main__":
    run_all_intake_quality_tests()
