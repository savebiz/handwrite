# Specs: Customer Onboarding Form Family

## Description
Handwritten application forms for new customer onboarding services.

## Schema Fields
- `onboarding_ref` (Required, Pattern `ONB-YYYY-XXX`)
- `application_date` (Required, ISO Date)
- `applicant_name` (Required, Personal - Mandatory Review)
- `contact_number` (Required, Personal - Mandatory Review)
- `email_address` (Optional, Personal - Mandatory Review)
- `address_location` (Required, Personal - Mandatory Review)
- `product_requested` (Required, Enum: Standard / Premium / Enterprise)
- `id_ref_placeholder` (Required, Sensitive - Masked Placeholder, Mandatory Review)
- `consent_indicator` (Required, Personal - Enum: YES / NO)
- `reviewer_status` (Required, Enum: PENDING / VERIFIED / REJECTED)
- `form_completeness` (Required, Enum: COMPLETE / INCOMPLETE)
