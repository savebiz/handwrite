# Specs: Product Brief — HandWrite Verify

## Executive Summary
HandWrite Verify is an agentic, human-in-the-loop records digitization system designed for processing handwritten paper business forms. It guarantees zero silent hallucination by linking every extracted value to visual evidence crops and routing unreadable, uncertain, or sensitive data to human review.

## Key Principles
1. **Evidence-Linked Extraction**: Every field links to bounding box visual crops on the original form.
2. **Deterministic-First Validation**: Rules run before model guesswork.
3. **Risk-Aware Triage**: Sensitive fields (PII, consent, identity) and low-confidence fields require human sign-off.
4. **Auditability**: Every decision and edit is preserved in an append-only JSONL audit log.
