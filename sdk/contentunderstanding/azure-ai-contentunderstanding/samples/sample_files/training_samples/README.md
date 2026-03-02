# Training Samples for Custom Model Building

This directory contains labeled training files for the `sample_create_analyzer_with_labels.py` sample.

## File Requirements

For each training document, you need **three files**:

1. **Source document**: The actual document (image, PDF, etc.) (e.g., `receipt1.jpg`)
2. **Labels file**: Field labels and bounding box annotations (e.g., `receipt1.jpg.labels.json`)
3. **Result file**: Pre-computed OCR results (e.g., `receipt1.jpg.result.json`, optional, speeds up training)

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
        "MerchantName": {
            "type": "string",
            "valueString": "Contoso",
            ...
        }
    }
}
```

## Current Training Set

This directory contains 2 labeled receipt images with 3 fields:
- `MerchantName` (string) — Name of the merchant
- `Items` (array of objects) — Each item has `Quantity`, `Name`, and `Price`
- `TotalPrice` (string) — Total amount

### Files

| Document | Labels | OCR Result |
|---|---|---|
| `receipt1.jpg` | `receipt1.jpg.labels.json` | `receipt1.jpg.result.json` |
| `receipt2.jpg` | `receipt2.jpg.labels.json` | `receipt2.jpg.result.json` |

## Usage

1. Upload all files to Azure Blob Storage
2. Set environment variables (choose one option):
   - **Option A**: Set `CONTENTUNDERSTANDING_TRAINING_DATA_SAS_URL` to a SAS URL with Read + List permissions
   - **Option B**: Set `CONTENTUNDERSTANDING_TRAINING_DATA_STORAGE_ACCOUNT` and `CONTENTUNDERSTANDING_TRAINING_DATA_CONTAINER` to auto-upload
3. Optionally set `CONTENTUNDERSTANDING_TRAINING_DATA_PREFIX` if files are in a subfolder
4. Run `python sample_create_analyzer_with_labels.py`

See `sample_create_analyzer_with_labels.py` and `../../env.sample` for configuration details.


