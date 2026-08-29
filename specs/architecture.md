# Specs: Architecture Overview

```
 [Uploaded Image] ──> [Intake & Quality Agent] ──> [Classification Agent]
                                                             │
                                                             ▼
                                                [Field Extraction Agent]
                                                             │
                                                             ▼
                                            [Deterministic Verification Agent]
                                                             │
                                                             ▼
                                                    [Triage Agent]
                                                             │
                                   ┌─────────────────────────┴─────────────────────────┐
                                   ▼                                                   ▼
                         (auto_accept / clean)                              (human_review / rescan)
                                   │                                                   │
                                   └─────────────────────────┬─────────────────────────┘
                                                             ▼
                                                 [Reviewer UI Workspace]
                                                             │
                                                             ▼
                                             [Approved Record Exporter]
                                                             │
                                             ┌───────────────┴───────────────┐
                                             ▼                               ▼
                                     [JSON / CSV Record]            [Audit Log JSONL]
```
