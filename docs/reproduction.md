# Reproduction Guide — HandWrite Verify

Follow these exact steps to reproduce the clean-environment setup, synthetic document generation, agent pipeline execution, and comparative evaluation.

---

## 1. Prerequisites
- Python 3.13+
- Node.js v20+

---

## 2. Environment Setup & Dependency Installation

```bash
# Clone the repository
git clone https://github.com/savebiz/handwrite.git
cd handwrite

# Create and activate Python virtual environment
python -m venv .venv
# On Windows PowerShell:
.\.venv\Scripts\activate

# Install backend dependencies
pip install -r requirements.txt
```

---

## 3. Environment Configuration
```bash
# Copy template environment file
cp .env.example .env
```

---

## 4. Run Synthetic Corpus Generation
```bash
# Generates 12 synthetic document forms (6 field inspection, 6 customer onboarding), gold labels, and manifest
python scripts/generate_synthetic_corpus.py
```

---

## 5. Run Unit & Schema Tests
```bash
# Execute schema data contract & pipeline tests
python scripts/run_schema_tests.py
python tests/test_pipeline.py
python tests/test_api.py
```

---

## 6. Run Comparative Evaluation Harness
```bash
# Evaluates Baseline vs Agentic Pipeline on the identical dataset
python evaluation/evaluate.py
```
*Expected Output*:
- Baseline Verified Field Accuracy: ~83.33%
- Agentic Verified Field Accuracy: 100.0%
- Escalation Recall: 100.0%
- Results recorded at `outputs/evaluation_results.json`.

---

## 7. Run Local Web Application & Reviewer UI

```bash
# Terminal 1: Start FastAPI Backend Server
uvicorn app.backend.main:app --reload --port 8000

# Terminal 2: Start Vite Frontend UI
cd app/frontend
npm install
npm run dev
```
Open browser at `http://localhost:5173`.
