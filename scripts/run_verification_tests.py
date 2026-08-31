"""
scripts/run_verification_tests.py — Standalone Runner for Deterministic Verification Agent Tests
"""

import sys
import os

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("./vendor"))
sys.path.insert(0, os.path.abspath("./.venv/Lib/site-packages"))
user_site = os.path.expanduser(r"~\AppData\Roaming\Python\Python313\site-packages")
if os.path.exists(user_site):
    sys.path.insert(0, user_site)

from tests.test_verification import run_all_verification_tests

if __name__ == "__main__":
    run_all_verification_tests()
