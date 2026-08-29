# HandWrite Verify

> **HandWrite Verify turns scanned handwritten business forms into structured, evidence-linked, review-ready records—without silently treating uncertain handwriting as fact.**

---

## 📌 Problem & Purpose
Digitization teams processing handwritten paper business forms spend massive manual effort reading handwriting, indexing metadata, and catching scan flaws. Existing OCR systems often hallucinate uncertain characters or output raw text without source evidence. HandWrite Verify introduces an agentic human-in-the-loop processing pipeline that enforces deterministic rule checks, provides visual crop evidence, and routes high-risk or low-confidence data to human reviewers.

---

## 🛠️ Tech Stack & Architecture
- **Backend**: Python 3.13 + FastAPI + Pydantic v2 + Pillow
- **Frontend**: Vite + React + Tailwind CSS
- **Data & Logs**: JSON File DB + Append-only Audit Log (`logs/audit.jsonl`)
- **Evaluation Engine**: Automated comparative scoring harness (`evaluation/evaluate.py`)

---

## 🚀 Quickstart & Setup

### Prerequisites
- Python 3.13+
- Node.js v20+

### Local Setup
```bash
# 1. Clone repository & install backend dependencies
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure Environment
cp .env.example .env

# 3. Run Backend API
uvicorn app.backend.main:app --reload --port 8000

# 4. Run Frontend UI (in separate terminal)
cd app/frontend
npm install
npm run dev
```

---

## 📊 Running Baseline & Agent Evaluation
```bash
# Generate synthetic dataset (12 sample forms)
python scripts/generate_synthetic_corpus.py

# Run baseline & agent evaluation pipeline
python evaluation/evaluate.py
```

---

## 🛡️ Core Safety Principles
1. Synthetic Data Only — No real customer documents or PII.
2. Evidence Transparency — Every field links to image coordinates `[ymin, xmin, ymax, xmax]`.
3. Human-in-the-Loop Safeguard — Personal & sensitive fields require explicit human sign-off.
