# Workflow Tickets 2 - 5 Overview

## Ticket 2: Synthetic Corpus and Baseline
- Create 12 synthetic document cases and gold labels.
- Build a data manifest.
- Implement baseline extraction adapter/runner.
- Implement scoring harness (`evaluation/evaluate.py`).

## Ticket 3: Agent Workflow Backend
- Build quality, classification, extraction, deterministic verification, and triage stages.
- Persist structured run records and audit events.
- Add unit tests for core routing rules.

## Ticket 4: Human Reviewer Interface
- Build upload, queue, reviewer detail, decisions, and approved-record screens.
- Enforce sensitive-field approval.

## Ticket 5: Evaluation, Reproducibility, and Demo
- Run baseline and final workflow on the identical dataset.
- Record results and error analysis.
- Update changelog.
- Create reproduction instructions and demo assets.
