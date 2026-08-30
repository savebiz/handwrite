# Specs: Metadata Dictionary

## 1. Field Inspection Form Fields
| Field Name | Display Name | Type | Required | Sensitivity | Validations / Rules |
|------------|--------------|------|----------|-------------|---------------------|
| `inspection_ref` | Inspection Reference | String | Yes | Public | Pattern `INSP-[0-9]{4}-[0-9]{3}` |
| `inspection_date` | Inspection Date | Date | Yes | Public | Valid ISO-8601 date, not in future |
| `site_location` | Site / Location | String | Yes | Internal | Non-empty text |
| `inspector_name` | Inspector Name | String | Yes | Personal | Non-empty text |
| `asset_ref` | Asset Reference | String | Yes | Internal | Pattern `AST-[0-9]{5}` |
| `inspection_status` | Inspection Status | Enum | Yes | Public | `PASS`, `FAIL`, `NEEDS_ATTENTION` |
| `observation_finding` | Finding / Observation | String | No | Public | Free text |
| `action_required` | Action Required | String | No | Public | Free text |
| `followup_date` | Follow-up Date | Date | No | Public | Date >= inspection_date |
| `form_completeness` | Completeness Status | Enum | Yes | Internal | `COMPLETE`, `INCOMPLETE` |

---

## 2. Customer Onboarding Form Fields
| Field Name | Display Name | Type | Required | Sensitivity | Validations / Rules |
|------------|--------------|------|----------|-------------|---------------------|
| `onboarding_ref` | Onboarding Reference | String | Yes | Public | Pattern `ONB-[0-9]{4}-[0-9]{3}` |
| `application_date` | Application Date | Date | Yes | Public | Valid ISO-8601 date, not in future |
| `applicant_name` | Applicant Name | String | Yes | Personal | Non-empty text, human review mandatory |
| `contact_number` | Contact Number | String | Yes | Personal | Phone regex `^\+?[0-9]{10,14}$`, human review mandatory |
| `email_address` | Email Address | String | No | Personal | Standard email regex, human review mandatory |
| `address_location` | Address / Location | String | Yes | Personal | Non-empty text, human review mandatory |
| `product_requested` | Product / Service | String | Yes | Internal | Controlled list (`Standard`, `Premium`, `Enterprise`) |
| `id_ref_placeholder` | Identity Reference | String | Yes | Sensitive | Masked placeholder `ID-*****`, human review mandatory |
| `consent_indicator` | Consent Indicator | Enum | Yes | Personal | `YES`, `NO` |
| `reviewer_status` | Reviewer Status | Enum | Yes | Internal | `PENDING`, `VERIFIED`, `REJECTED` |
| `form_completeness` | Completeness Status | Enum | Yes | Internal | `COMPLETE`, `INCOMPLETE` |

> **Privacy Rule**: All fields classified as `personal` or `sensitive` (including applicant name, phone, email, address, and ID placeholder) are strictly flagged as `human_review` and CANNOT be auto-accepted.
