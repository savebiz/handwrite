# Video Shot List & Production Plan — HandWrite Verify

**Target Length**: 4 minutes 45 seconds (Max 5:00)
**Resolution**: 1920x1080 (1080p, 60 FPS)
**Format**: MP4 (H.264 / AAC)

---

## 🎬 Second-by-Second Shot List

| Time Range | Shot # | Visual Screen Layout | On-Screen Action / Focus | Audio / Narration Cue |
|---|---|---|---|---|
| **00:00 - 00:15** | `SHOT-01` | Title Slide & Architecture Diagram | Display "HandWrite Verify", Victor Sabo, Challenge Name | "In safety-critical industries like field inspection..." |
| **00:15 - 00:30** | `SHOT-02` | Split View: Scanned Form `FI-004` | Zoom into blurry text and cut-off form border | "...traditional single-pass OCR systems hallucinate text..." |
| **00:30 - 01:00** | `SHOT-03` | VS Code Terminal (`run_baseline_scoring.py`) | Execute baseline scoring script; view raw OCR JSON output | "Here is our unassisted baseline... outputting raw text without checks." |
| **01:00 - 01:25** | `SHOT-04` | Terminal (`run_test_run_suite.py`) | Launch agentic pipeline; highlight Stage 1 Intake Quality | "First, Document Quality pre-screens images for blur and skew..." |
| **01:25 - 01:45** | `SHOT-05` | File Explorer (`outputs/crops/`) | Show generated crop PNG files (`FI-001_inspection_ref.png`) | "...Extraction transcribes text and slices physical PNG crops..." |
| **01:45 - 02:00** | `SHOT-06` | VS Code (`verification_agent.py`) | Highlight `RULE-EVID-010` and `RULE-COMP-011` rules | "...Verification runs 10 deterministic validation rules..." |
| **02:00 - 02:25** | `SHOT-07` | Chrome Browser (`/static/reviewer.html`) | Display Reviewer Dashboard UI; select `AXA-ATT-001` | "Now let's open the Reviewer Dashboard..." |
| **02:25 - 02:40** | `SHOT-08` | Reviewer Dashboard (Export Attempt) | Click "Export Record" button; show red HTTP 400 error banner | "...if a reviewer attempts to export a pending record, backend blocks export..." |
| **02:40 - 03:00** | `SHOT-09` | Reviewer Dashboard (Submit Action) | Enter reviewer correction + reason; click Submit & Export | "Once reviewer submits correction, record transitions to APPROVED..." |
| **03:00 - 03:45** | `SHOT-10` | Evaluation Report (`comparison-results.json`) | Display baseline (85.71%) vs advanced (100.00%) metrics table | "Across 12 benchmark forms, advanced pipeline achieved 100% final accuracy..." |
| **03:45 - 04:15** | `SHOT-11` | Code Diff (`CHANGELOG.md`) | Show `RULE-EVID-010` evidence rule vs failed bounding box experiment | "Our most useful improvement was evidence crop verification..." |
| **04:15 - 04:45** | `SHOT-12` | Closing Slide & Repository URL | Show `github.com/savebiz/handwrite` & "110/110 PASSED" badge | "Single-pass OCR without quality checks is a production liability. Thank you!" |
