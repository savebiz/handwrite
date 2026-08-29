# HandWrite Verify — Quality & Review Checklist

All code changes and ticket completions must pass this 12-point review matrix before sign-off:

1. **Functional Correctness**: Does the code execute without runtime exceptions across clean, medium, and hard document inputs?
2. **Schema & API Contract Compliance**: Do all data structures strictly conform to `shared-data-contract.md` and Pydantic schemas?
3. **Validation Accuracy**: Are deterministic checks (dates, regexes, required fields) catching known edge cases and malformed values?
4. **Human-in-the-Loop Safety**: Are fields marked `personal` or `sensitive` strictly prohibited from auto-accepting without human reviewer sign-off?
5. **Evidence-Link Integrity**: Does every extracted field carry a valid page index, non-null bounding box `[ymin, xmin, ymax, xmax]`, and crop snippet?
6. **Privacy & Credentials**: Are environment variables loaded from `.env`, `.env.example` committed cleanly, and zero real PII or secrets present?
7. **UI Clarity & Usability**: Does the reviewer workspace display side-by-side evidence crops and clear action buttons (`Approve`, `Correct`, `Reject`, `Rescan`)?
8. **Error Handling & Graceful Recovery**: Are unreadable or corrupt files routed to `rescan_required` without throwing unhandled backend tracebacks?
9. **Reproducibility**: Can an independent developer run the setup commands and achieve identical evaluation results?
10. **Scope Discipline**: Does the pull request stay strictly within the single assigned workflow ticket without scope creep?
11. **Evidence-Based Claims**: Is every accuracy or performance claim backed by output logs from the automated evaluation harness?
12. **Audit Logging**: Is every automated triage decision and reviewer action logged to `logs/audit.jsonl` with ISO-8601 timestamps and actor IDs?
