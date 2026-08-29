# Specs: Error Taxonomy

1. `EXTRACTION_ERROR`: Model mistranscribed handwriting characters.
2. `NORMALIZATION_ERROR`: Value correctly read but failed standard format conversion (e.g. date formatting).
3. `VALIDATION_ERROR`: Value failed deterministic regex or vocabulary constraint.
4. `FALSE_AUTO_ACCEPT`: Low quality or incorrect value was erroneously auto-accepted.
5. `MISSED_ESCALATION`: Problematic field bypassed reviewer queue.
6. `UNNECESSARY_ESCALATION`: High-confidence clean non-sensitive field sent to review.
7. `QUALITY_ROUTING_ERROR`: Bad scan misclassified as readable or vice-versa.
8. `CLASSIFICATION_ERROR`: Form family assigned incorrectly.
