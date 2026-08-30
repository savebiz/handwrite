# Workflow Ticket 2: Synthetic Corpus and Baseline Extractor

- **Objective**: Generate 12 synthetic document forms (6 field inspection, 6 customer onboarding) across clean, medium, hard, and extreme difficulty levels, programmatically generate ground-truth gold labels, build the master manifest, and implement the single-pass baseline extractor.
- **Assigned Virtual Roles**: `evaluation-benchmark-specialist`, `vision-extraction-specialist`
- **Tasks**:
  1. Build `scripts/generate_synthetic_corpus.py` using Pillow to render synthetic forms with drawn handwriting and printed text.
  2. Emit 12 gold-label JSON files in `data/gold-labels/` and `data/manifests/manifest.json`.
  3. Implement `evaluation/baseline.py` to run single-pass unverified extraction.
- **Definition of Done**:
  - Baseline runs locally against all 12 synthetic document cases.
  - Empirical baseline metrics recorded without fabricated data.
