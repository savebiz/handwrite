import os
import json
from PIL import Image, ImageDraw, ImageFont, ImageFilter


def ensure_dirs():
    os.makedirs("data/synthetic/field-inspection", exist_ok=True)
    os.makedirs("data/synthetic/customer-onboarding", exist_ok=True)
    os.makedirs("data/gold-labels", exist_ok=True)
    os.makedirs("data/manifests", exist_ok=True)


CORPUS_SPECS = [
    # --- Field Inspection Forms ---
    {
        "id": "FI-001",
        "family": "field_inspection",
        "difficulty": "clean",
        "filename": "field_insp_001.png",
        "fields": {
            "inspection_ref": "INSP-2026-001",
            "inspection_date": "2026-08-15",
            "site_location": "Building A, North Wing",
            "inspector_name": "John Doe",
            "asset_ref": "AST-10293",
            "inspection_status": "PASS",
            "observation_finding": "All pressure valves optimal.",
            "action_required": "None",
            "followup_date": "2026-11-15",
            "form_completeness": "COMPLETE",
        },
        "issues": [],
    },
    {
        "id": "FI-002",
        "family": "field_inspection",
        "difficulty": "clean",
        "filename": "field_insp_002.png",
        "fields": {
            "inspection_ref": "INSP-2026-002",
            "inspection_date": "2026-08-16",
            "site_location": "Substation 4B",
            "inspector_name": "Alice Smith",
            "asset_ref": "AST-44102",
            "inspection_status": "NEEDS_ATTENTION",
            "observation_finding": "Minor coolant leak on valve 3.",
            "action_required": "Replace gasket seals.",
            "followup_date": "2026-09-01",
            "form_completeness": "COMPLETE",
        },
        "issues": [],
    },
    {
        "id": "FI-003",
        "family": "field_inspection",
        "difficulty": "medium",
        "filename": "field_insp_003.png",
        "fields": {
            "inspection_ref": "INSP-2026-003",
            "inspection_date": "2026-08-18",
            "site_location": "Warehouse Depot 12",
            "inspector_name": "Robert Vance",
            "asset_ref": "AST-88192",
            "inspection_status": "FAIL",
            "observation_finding": "Heavy corrosion on structural beam.",
            "action_required": "Immediate safety audit & beam replacement.",
            "followup_date": "2026-08-25",
            "form_completeness": "COMPLETE",
        },
        "issues": ["minor_skew"],
    },
    {
        "id": "FI-004",
        "family": "field_inspection",
        "difficulty": "medium",
        "filename": "field_insp_004.png",
        "fields": {
            "inspection_ref": "INSP-2026-004",
            "inspection_date": "2026-08-20",
            "site_location": "Solar Array Field 7",
            "inspector_name": "Maria Garcia",
            "asset_ref": "AST-33019",
            "inspection_status": "PASS",
            "observation_finding": "Dust buildup on panel surface.",
            "action_required": "Schedule monthly cleaning.",
            "followup_date": "2026-09-20",
            "form_completeness": "COMPLETE",
        },
        "issues": ["slight_contrast_variation"],
    },
    {
        "id": "FI-005",
        "family": "field_inspection",
        "difficulty": "hard",
        "filename": "field_insp_005.png",
        "fields": {
            "inspection_ref": "INSP-2026-005",
            "inspection_date": "2026-08-22",
            "site_location": "Refinery Zone C",
            "inspector_name": "David K.",
            "asset_ref": "AST-99001",
            "inspection_status": "NEEDS_ATTENTION",
            "observation_finding": "Vibration noise in pump motor.",
            "action_required": "Lubricate bearings.",
            "followup_date": "2026-09-05",
            "form_completeness": "COMPLETE",
        },
        "issues": ["handwriting_overlap", "noise"],
    },
    {
        "id": "FI-006",
        "family": "field_inspection",
        "difficulty": "hard",
        "filename": "field_insp_006_extreme.png",
        "fields": {
            "inspection_ref": "INSP-2026-006",
            "inspection_date": "2026-08-25",
            "site_location": "Offshore Platform Delta",
            "inspector_name": None,  # Missing mandatory inspector name
            "asset_ref": "AST-11002",
            "inspection_status": "FAIL",
            "observation_finding": "Pressure drop cross-out (120psi -> 80psi)",
            "action_required": "Emergency shutdown valve check",
            "followup_date": "2026-08-26",
            "form_completeness": "INCOMPLETE",
        },
        "issues": [
            "extreme_blur",
            "skew",
            "crossed_out_text",
            "missing_mandatory_field",
            "multiple_handwriting_styles",
        ],
    },
    # --- Customer Onboarding Forms ---
    {
        "id": "CO-001",
        "family": "customer_onboarding",
        "difficulty": "clean",
        "filename": "cust_onb_001.png",
        "fields": {
            "onboarding_ref": "ONB-2026-101",
            "application_date": "2026-08-10",
            "applicant_name": "Sarah Jenkins",
            "contact_number": "+14155550192",
            "email_address": "sarah.j@example.com",
            "address_location": "742 Evergreen Terrace, Springfield",
            "product_requested": "Standard",
            "id_ref_placeholder": "ID-984712",
            "consent_indicator": "YES",
            "reviewer_status": "PENDING",
            "form_completeness": "COMPLETE",
        },
        "issues": [],
    },
    {
        "id": "CO-002",
        "family": "customer_onboarding",
        "difficulty": "clean",
        "filename": "cust_onb_002.png",
        "fields": {
            "onboarding_ref": "ONB-2026-102",
            "application_date": "2026-08-11",
            "applicant_name": "Michael Brown",
            "contact_number": "+12125550144",
            "email_address": "m.brown@domain.com",
            "address_location": "100 Broadway Ave, New York, NY",
            "product_requested": "Premium",
            "id_ref_placeholder": "ID-551029",
            "consent_indicator": "YES",
            "reviewer_status": "PENDING",
            "form_completeness": "COMPLETE",
        },
        "issues": [],
    },
    {
        "id": "CO-003",
        "family": "customer_onboarding",
        "difficulty": "medium",
        "filename": "cust_onb_003.png",
        "fields": {
            "onboarding_ref": "ONB-2026-103",
            "application_date": "2026-08-14",
            "applicant_name": "Elena Rostova",
            "contact_number": "+442079460912",
            "email_address": "elena.r@net.co.uk",
            "address_location": "12 Baker Street, London",
            "product_requested": "Enterprise",
            "id_ref_placeholder": "ID-334910",
            "consent_indicator": "YES",
            "reviewer_status": "PENDING",
            "form_completeness": "COMPLETE",
        },
        "issues": ["slight_skew"],
    },
    {
        "id": "CO-004",
        "family": "customer_onboarding",
        "difficulty": "medium",
        "filename": "cust_onb_004.png",
        "fields": {
            "onboarding_ref": "ONB-2026-104",
            "application_date": "2026-08-15",
            "applicant_name": "David Wu",
            "contact_number": "+14085550188",
            "email_address": "dwu@techcorp.io",
            "address_location": "500 Market St, San Francisco, CA",
            "product_requested": "Standard",
            "id_ref_placeholder": "ID-771823",
            "consent_indicator": "NO",
            "reviewer_status": "PENDING",
            "form_completeness": "COMPLETE",
        },
        "issues": ["faded_ink"],
    },
    {
        "id": "CO-005",
        "family": "customer_onboarding",
        "difficulty": "hard",
        "filename": "cust_onb_005.png",
        "fields": {
            "onboarding_ref": "ONB-2026-105",
            "application_date": "2026-08-19",
            "applicant_name": "Carlos Gomez",
            "contact_number": "+34911234567",
            "email_address": "carlos.g@madrid.es",
            "address_location": "Calle Mayor 4, Madrid",
            "product_requested": "Premium",
            "id_ref_placeholder": "ID-110293",
            "consent_indicator": "YES",
            "reviewer_status": "PENDING",
            "form_completeness": "COMPLETE",
        },
        "issues": ["cursive_handwriting", "low_contrast"],
    },
    {
        "id": "CO-006",
        "family": "customer_onboarding",
        "difficulty": "hard",
        "filename": "cust_onb_006.png",
        "fields": {
            "onboarding_ref": "ONB-2026-106",
            "application_date": "2026-08-21",
            "applicant_name": "Anita Patel",
            "contact_number": "+919876543210",
            "email_address": None,
            "address_location": "MG Road 45, Bengaluru",
            "product_requested": "Enterprise",
            "id_ref_placeholder": "ID-882019",
            "consent_indicator": "YES",
            "reviewer_status": "PENDING",
            "form_completeness": "COMPLETE",
        },
        "issues": ["ambiguous_digits", "wrinkled_paper"],
    },
]


def render_synthetic_form(spec: dict) -> str:
    width, height = 800, 1000
    img = Image.new("RGB", (width, height), color=(250, 250, 248))
    draw = ImageDraw.Draw(img)

    # Title header
    title = (
        "FIELD INSPECTION FORM"
        if spec["family"] == "field_inspection"
        else "CUSTOMER ONBOARDING APPLICATION"
    )
    draw.rectangle([20, 20, width - 20, 70], fill=(230, 235, 245), outline=(100, 110, 130))
    draw.text((40, 35), title, fill=(20, 40, 80))

    # Grid bounding boxes and text labels
    y_offset = 100
    for field_key, val in spec["fields"].items():
        draw.rectangle([50, y_offset, 750, y_offset + 50], outline=(180, 180, 180), width=1)
        label_str = field_key.replace("_", " ").title()
        draw.text((60, y_offset + 5), f"{label_str}:", fill=(100, 100, 100))

        display_val = str(val) if val is not None else "[UNREADABLE / BLANK]"
        # Simulate handwriting text
        val_color = (20, 20, 150) if "extreme" not in spec["filename"] else (120, 120, 120)
        draw.text((300, y_offset + 20), display_val, fill=val_color)

        if "crossed_out" in str(spec.get("issues", [])) and field_key == "observation_finding":
            draw.line([300, y_offset + 25, 600, y_offset + 25], fill=(200, 0, 0), width=3)

        y_offset += 65

    # Apply image flaws based on difficulty/issues
    if "minor_skew" in spec["issues"] or "skew" in spec["issues"]:
        angle = 2 if "minor_skew" in spec["issues"] else 6
        img = img.rotate(angle, expand=False, fillcolor=(250, 250, 248))

    if "extreme_blur" in spec["issues"]:
        img = img.filter(ImageFilter.GaussianBlur(radius=3))

    sub_dir = spec["family"].replace("_", "-")
    output_path = os.path.join("data/synthetic", sub_dir, spec["filename"])
    img.save(output_path)
    return output_path


def main():
    ensure_dirs()
    manifest_records = []

    for spec in CORPUS_SPECS:
        img_path = render_synthetic_form(spec)

        # Write Gold Label JSON
        gold_payload = {
            "document_id": spec["id"],
            "document_type": spec["family"],
            "difficulty": spec["difficulty"],
            "issues": spec["issues"],
            "gold_fields": spec["fields"],
        }

        gold_path = os.path.join("data/gold-labels", f"{spec['id']}_gold.json")
        with open(gold_path, "w", encoding="utf-8") as f:
            json.dump(gold_payload, f, indent=2)

        manifest_records.append(
            {
                "document_id": spec["id"],
                "document_type": spec["family"],
                "difficulty": spec["difficulty"],
                "image_path": img_path,
                "gold_label_path": gold_path,
                "issues": spec["issues"],
            }
        )

    manifest_path = "data/manifests/manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump({"total_samples": len(manifest_records), "samples": manifest_records}, f, indent=2)

    print(f"Generated {len(manifest_records)} synthetic forms, gold labels, and manifest at {manifest_path}.")


if __name__ == "__main__":
    main()
