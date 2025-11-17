# Training Samples for Custom Model Building

This directory contains training files for the `build_custom_model_with_training.py` sample.

## File Requirements

For each training document, you need **three files**:

1. **PDF file**: The actual document (e.g., `IRS_1040_1_09.pdf`)
2. **Labels file**: Field annotations (e.g., `IRS_1040_1_09.pdf.labels.json`)
3. **Result file**: OCR output from prebuilt-documentSearch (e.g., `IRS_1040_1_09.pdf.result.json`)

## Labels File Format

The `.labels.json` files must:
- Use schema version `2025-11-01` (not the preview version)
- Contain only fields defined in your custom schema
- Match the field types defined in the schema

Example structure:
```json
{
    "$schema": "https://schema.ai.azure.com/mmi/2025-11-01/labels.json",
    "fileId": "",
    "fieldLabels": {
        "FieldYourFirstNameAndMiddleInitial": {
            "type": "string",
            "valueString": "Robert",
            ...
        }
    }
}
```

## Current Training Set

This directory contains 2 labeled IRS 1040 forms with 5 fields:
- `FieldYourFirstNameAndMiddleInitial`
- `FieldYourFirstNameAndMiddleInitialLastName`
- `CheckboxYouAsADependent`
- `TableDependents` (with nested properties)
- `FieldWagesSalariesTipsEtcAttachFormSW2`

## Usage

1. Upload all files to Azure Blob Storage
2. Set the `CONTENT_UNDERSTANDING_STORAGE_CONTAINER_SAS_URL` environment variable
3. Set the `CONTENT_UNDERSTANDING_STORAGE_PREFIX` to point to your training files
4. Run `python build_custom_model_with_training.py`

See `../../env.sample` for configuration details.


