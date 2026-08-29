# Skill: Document Quality Assurance

- **Owner Roles**: `verification-qa-specialist`
- **Purpose**: Detect image flaws (blur, skew, cut-offs, duplicates) and flag documents for rescan before extraction.
- **Non-Goals**: Attempting OCR on unreadable images.
- **Inputs**: Image bytes/file.
- **Method**: Compute contrast variance, edge detection density, rotation angle; emit `QualityResult`.
- **Quality Checks**: `rescan_required = True` when blur or threshold falls below minimum spec.
