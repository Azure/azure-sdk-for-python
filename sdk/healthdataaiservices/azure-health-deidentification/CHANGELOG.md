# Release History

## 1.0.0 (2025-05-19)

### Features Added

- Introduced `DeidentificationCustomizationOptions` and `DeidentificationJobCustomizationOptions` models.
    - Added `surrogate_locale` field in these models.
    - Moved `redaction_format` field into these models.
- Introduced `overwrite` property in `TargetStorageLocation` model, which allows a job to overwrite existing documents in the storage location. 

### Breaking Changes

- Changed method names in `DeidentificationClient` to match functionality:
    - Changed the `deidentify` method name to `deidentify_text`.
    - Changed the `begin_create_job` method name to `begin_deidentify_documents`.
- Renamed the property `DeidentificationContent.operation` to `operation_type`.
- Deprecated `DocumentDataType`.
- Changed the model `DeidentificationDocumentDetails`:
    - Renamed `input` to `input_location`.
    - Renamed `output` to `output_location`.
- Changed the model `DeidentificationJob`
    - Renamed `name` to `job_name`.
    - Renamed `operation` to `operation_type`.
- Renamed the model `OperationState` to `OperationStatus`.
- Changed `path` field to `location` in `SourceStorageLocation` and `TargetStorageLocation`.
- Changed `outputPrefix` behavior to no longer include `job_name` by default.
- Deprecated `path` and `location` from `TaggerResult` model.

## 1.0.0b1 (2024-08-15)

- Azure Health Deidentification client library

### Features Added

- Azure Health Deidentification client library
