# Specs: Evaluation Plan & Corpus

## Corpus Design
- Total Documents: 12 synthetic forms
  - 6 Field-Inspection Forms
  - 6 Customer-Onboarding Forms
- Difficulty Mix:
  - 4 Clean documents (high contrast, clear print/handwriting)
  - 4 Medium documents (minor skew, mixed handwriting styles)
  - 4 Hard documents (1 extreme case with blur, skew, crossed-out text, missing mandatory field, ambiguous characters)

## Primary Metric
- **Verified Field Accuracy**: Exact normalized field matches / total applicable labelled fields.

## Secondary Metrics
- Median Reviewer Seconds per Document
- Escalation Recall (% of problematic fields correctly sent to human review)
- Unnecessary Review Rate (% of clean fields sent to review)
- Schema Validation Pass Rate
