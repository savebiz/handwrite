# HandWrite Verify — Quality & Review Checklist

All code changes, ticket completions, and submission pull requests must pass this 14-point review matrix before sign-off:

1. **Individual Entry Certification**: Is the submission explicitly declared as an individual entry by Victor Sabo, with virtual agent roles clearly documented?
2. **Qualification Gate Compliance**: Does the submission satisfy all 11 qualification gate criteria in `docs/qualification-gate-checklist.md`?
3. **Tool & Agent Disclosure Audit**: Are all AI tools, subagents, and automated code generation mechanisms listed in `docs/agent-use-disclosure.md`?
4. **Functional Correctness**: Does the backend and frontend code execute without runtime exceptions across clean, medium, hard, and typewritten document inputs?
5. **Schema & API Contract Compliance**: Do all data structures strictly conform to `specs/shared-data-contract.md` and Pydantic schemas?
6. **Validation Accuracy**: Are deterministic checks (dates, regexes, required fields) catching known edge cases and malformed values before model judgment?
7. **Human-in-the-Loop Safety**: Are fields marked `personal` or `sensitive` strictly prohibited from auto-accepting without human reviewer sign-off?
8. **Evidence-Link Integrity**: Does every extracted field carry a valid page index, non-null bounding box `[ymin, xmin, ymax, xmax]`, and crop reference?
9. **Privacy & Credentials**: Are environment variables loaded from `.env`, `.env.example` committed cleanly, and zero real PII or secrets present?
10. **UI Clarity & Usability**: Does the reviewer workspace display side-by-side evidence crops, text style badges, and clear action controls?
11. **Error Handling & Graceful Recovery**: Are unreadable or corrupt files routed to `rescan_required` without throwing unhandled backend tracebacks?
12. **Reproducibility**: Can an independent developer run setup commands and reproduce evaluation metrics?
13. **Scope Discipline**: Does the pull request stay strictly within the designated workflow ticket without scope creep?
14. **Evidence-Based Claims**: Is every accuracy or performance claim backed by empirical output from `evaluation/evaluate.py`?
