# Skill: Handwriting Extraction

- **Owner Roles**: `vision-extraction-specialist`
- **Purpose**: Extract handwritten form fields into structured text with bounding box evidence coordinates `[ymin, xmin, ymax, xmax]` and confidence scores.
- **Non-Goals**: Making autonomous verification decisions or outputting hallucinated values.
- **Inputs**: Form image file, document family schema.
- **Method**:
  1. Identify candidate field bounding boxes based on template coordinates or visual layout.
  2. Perform line/box level transcription.
  3. Attach bounding box coordinates and calculated confidence (0.0 to 1.0).
  4. Output structured field candidates according to `shared-data-contract.md`.
- **Quality Checks**: Bounding box normalized `[0..1000]`, non-null page index, confidence score present.
