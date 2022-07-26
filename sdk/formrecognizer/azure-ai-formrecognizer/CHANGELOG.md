# Release History

## 3.2.0b6 (Unreleased)

### Features Added
- Added `TargetAuthorization` of type `dict[str, str]`.

### Breaking Changes
- Renamed `begin_create_composed_model()` on `DocumentModelAdministrationClient` to `begin_compose_model()`.
- Renamed `get_account_info()` on `DocumentModelAdministrationClient` to `get_resource_details()`.
- Renamed `AccountInfo` model to `ResourceDetails`.
- Renamed `DocumentModelInfo` model to `DocumentModelSummary`.
- Renamed `DocumentModel` to `DocumentModelDetails`.
- Renamed `ModelOperation` to `ModelOperationDetails`.
- Renamed `ModelOperationInfo` to `ModelOperationSummary`.
- Renamed `model` parameter to `model_id` on `begin_analyze_document()` and `begin_analyze_document_from_url()`.
- Removed `continuation_token` keyword from `begin_analyze_document()` and `begin_analyze_document_from_url()` on `DocumentAnalysisClient` and from `begin_build_model()`, `begin_compose_model()` and `begin_copy_model_to()` on `DocumentModelAdministrationClient`.
- Changed return type of `get_copy_authorization()` from `dict[str, str]` to `TargetAuthorization`.
- Changed expected `target` parameter in `begin_copy_to()` from `dict[str, str]` to `TargetAuthorization`.
- Long-running operation metadata is now accessible through the `details` property on the returned `DocumentModelAdministrationLROPoller` and `AsyncDocumentModelAdministrationLROPoller` instances.

### Bugs Fixed

### Other Changes
- Python 3.6 is no longer supported in this release. Please use Python 3.7 or later.

## 3.2.0b5 (2022-06-07)

### Features Added
- Added `paragraphs` property on `AnalyzeResult`.
- Added new `DocumentParagraph` model to represent document paragraphs.
- Added new `AddressValue` model to represent address fields found in documents.
- Added `kind` property on `DocumentPage`.

### Breaking Changes
- Renamed `bounding_box` to `polygon` on `BoundingRegion`, `DocumentContentElement`, `DocumentLine`, `DocumentSelectionMark`, `DocumentWord`.
- Renamed `language_code` to `locale` on `DocumentLanguage`.
- Some models that previously returned string for address related fields may now return `AddressValue`. TIP: Use `get_model()` on `DocumentModelAdministrationClient` to see updated prebuilt model schemas.
- Removed `entities` property on `AnalyzeResult`.
- Removed `DocumentEntity` model.

## 3.2.0b4 (2022-04-05)

### Breaking Changes
- Renamed `begin_copy_model()` to `begin_copy_model_to()`.
- In `begin_create_composed_model()`, renamed required parameter `model_ids` to `component_model_ids`.
- Renamed `model_count` and `model_limit` on `AccountInfo` to `document_model_count` and `document_model_limit`.

### Bugs Fixed
- Fixed `to_dict()` and `from_dict()` methods on `DocumentField` to support converting lists, dictionaries, and CurrenyValue field types to and from a dictionary.

### Other Changes
- Renamed `sample_copy_model.py` and `sample_copy_model_async.py` to `sample_copy_model_to.py` and `sample_copy_model_to_async.py` under the `3.2-beta` samples folder. Updated the samples to use renamed copy model method.

## 3.2.0b3 (2022-02-10)

### Features Added
- Added new `CurrencyValue` model to represent the amount and currency symbol values found in documents.
- Added `DocumentBuildMode` enum with values `template` and `neural`. These enum values can be passed in for the `build_mode` parameter in `begin_build_model()`.
- Added `api_version` and `tags` properties on `ModelOperation`, `ModelOperationInfo`, `DocumentModel`, `DocumentModelInfo`.
- Added `build_mode` property on `DocTypeInfo`.
- Added a `tags` keyword argument to `begin_build_model()`, `begin_create_composed_model()`, and `get_copy_authorization()`.
- Added `languages` property on `AnalyzeResult`.
- Added model `DocumentLanguage` that includes information about the detected languages found in a document.
- Added `sample_analyze_read.py` and `sample_analyze_read_async.py` under the `v3.2-beta` samples directory. These samples use the new `prebuilt-read` model added by the service.
- Added `sample_analyze_tax_us_w2.py` and `sample_analyze_tax_us_w2_async.py` under the `v3.2-beta` samples directory. These samples use the new `prebuilt-tax.us.w2` model added by the service.

### Breaking Changes
- Added new required parameter `build_mode` to `begin_build_model()`.
- Some models that previously returned float for currency related fields may now return a `CurrencyValue`. TIP: Use `get_model()` on `DocumentModelAdministrationClient` to see updated prebuilt model schemas.

### Bugs Fixed
- Default the `percent_completed` property to 0 when not returned with model operation information.

### Other Changes
- Python 2.7 is no longer supported in this release. Please use Python 3.6 or later.
- Bumped `azure-core` minimum dependency version from `1.13.0` to `1.20.1`.
- Updated samples that call `begin_build_model()` to send the `build_mode` parameter.

## 3.2.0b2 (2021-11-09)

### Features Added
- Added `get_words()` on `DocumentLine`.
- Added samples showing how to use `get_words()` on a `DocumentLine` under `/samples/v3.2-beta`: `sample_get_words_on_document_line.py` and `sample_get_words_on_document_line_async.py`.

### Breaking Changes
- Renamed `DocumentElement` to `DocumentContentElement`.

## 3.2.0b1 (2021-10-07)

This version of the SDK defaults to the latest supported API version, which is currently 2021-09-30-preview.

> Note: Starting with version 2021-09-30-preview, a new set of clients were introduced to leverage the newest features of the Form Recognizer service. Please see the [Migration Guide](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/MIGRATION_GUIDE.md) for detailed instructions on how to update application code from client library version 3.1.X or lower to the latest version. Also, please refer to the [README](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/README.md) for more information about the library. 

### Features Added
- Added new `DocumentAnalysisClient` with  `begin_analyze_document` and `begin_analyze_document_from_url` methods. Use these methods with the latest Form Recognizer 
API version to analyze documents, with prebuilt and custom models.
- Added new models to use with the new `DocumentAnalysisClient`: `AnalyzeResult`, `AnalyzedDocument`, `BoundingRegion`, `DocumentElement`, `DocumentEntity`, `DocumentField`, `DocumentKeyValuePair`, `DocumentKeyValueElement`, `DocumentLine`, `DocumentPage`, `DocumentSelectionMark`, `DocumentSpan`, `DocumentStyle`, `DocumentTable`, `DocumentTableCell`, `DocumentWord`.
- Added new `DocumentModelAdministrationClient` with methods: `begin_build_model`, `begin_create_composed_model`, `begin_copy_model`, `get_copy_authorization`, `get_model`, `delete_model`, `list_models`, `get_operation`, `list_operations`, `get_account_info`, `get_document_analysis_client`.
- Added new models to use with the new `DocumentModelAdministrationClient`: `DocumentModel`, `DocumentModelInfo`, `DocTypeInfo`, `ModelOperation`, `ModelOperationInfo`, `AccountInfo`, `DocumentAnalysisError`, `DocumentAnalysisInnerError`.
- Added samples using the `DocumentAnalysisClient` and `DocumentModelAdministrationClient` under `/samples/v3.2-beta`.
- Added `DocumentAnalysisApiVersion` to be used with `DocumentAnalysisClient` and `DocumentModelAdministrationClient`.

### Other Changes
- Python 3.5 is no longer supported in this release.

## 3.1.2 (2021-08-10)

### Bugs Fixed
- A `HttpResponseError` will be immediately raised when the call quota volume is exceeded in a `F0` tier Form Recognizer
resource.

### Other Changes
- Bumped `azure-core` minimum dependency version from `1.8.2` to `1.13.0`

## 3.1.1 (2021-06-08)

**Bug Fixes**

- Handles invoices that do not have sub-line item fields detected.

## 3.1.0 (2021-05-26)

This version of the SDK defaults to the latest supported API version, which currently is v2.1

Note: this version will be the last to officially support Python 3.5, future versions will require Python 2.7 or Python 3.6+

**Breaking Changes**

- `begin_recognize_id_documents` renamed to `begin_recognize_identity_documents`.
- `begin_recognize_id_documents_from_url` renamed to `begin_recognize_identity_documents_from_url`.
- The model `TextAppearance` now includes the properties `style_name` and `style_confidence` that were part of the `TextStyle` object.
- Removed the model `TextStyle`.
- Removed field value types "gender" and "country" from the `FieldValueType` enum.
- Added field value type "countryRegion" to the `FieldValueType` enum.
- Renamed field name for identity documents from "Country" to "CountryRegion".

**New features**

- Added `to_dict` and `from_dict` methods to all of the models

## 3.1.0b4 (2021-04-06)

**New features**

- New methods `begin_recognize_id_documents` and `begin_recognize_id_documents_from_url` introduced to the SDK. Use these methods to recognize data from identity documents.
- New field value types "gender" and "country" described in the `FieldValueType` enum.
- Content-type `image/bmp` now supported by custom forms and training methods.
- Added keyword argument `pages` for business cards, receipts, custom forms, and invoices
to specify which page to process of the document.
- Added keyword argument `reading_order` to `begin_recognize_content` and `begin_recognize_content_from_url`.

**Dependency Updates**

- Bumped `msrest` requirement from `0.6.12` to `0.6.21`.

## 3.1.0b3 (2021-02-09)

**Breaking Changes**

- `Appearance` is renamed to `TextAppearance`
- `Style` is renamed to `TextStyle`
- Client property `api_version` is no longer exposed. Pass keyword argument `api_version` into the client to select the
API version

**Dependency Updates**

- Bumped `six` requirement from `1.6` to `1.11.0`.

## 3.1.0b2 (2021-01-12)

**Bug Fixes**

- Package requires [azure-core](https://pypi.org/project/azure-core/) version 1.8.2 or greater


## 3.1.0b1 (2020-11-23)

This version of the SDK defaults to the latest supported API version, which currently is v2.1-preview.

**New features**

- New methods `begin_recognize_business_cards` and `begin_recognize_business_cards_from_url` introduced to the SDK. Use these
methods to recognize data from business cards
- New methods `begin_recognize_invoices` and `begin_recognize_invoices_from_url` introduced to the SDK. Use these
methods to recognize data from invoices
- Recognize receipt methods now take keyword argument `locale` to optionally indicate the locale of the receipt for
improved results
- Added ability to create a composed model from the `FormTrainingClient` by calling method `begin_create_composed_model()`
- Added support to train and recognize custom forms with selection marks such as check boxes and radio buttons.
This functionality is only available for models trained with labels
- Added property `selection_marks` to `FormPage` which contains a list of `FormSelectionMark`
- When passing `include_field_elements=True`, the property `field_elements` on `FieldData` and `FormTableCell` will
also be populated with any selection marks found on the page
- Added the properties `model_name` and `properties` to types `CustomFormModel` and `CustomFormModelInfo`
- Added keyword argument `model_name` to `begin_training()` and `begin_create_composed_model()`
- Added model type `CustomFormModelProperties` that includes information like if a model is a composed model
- Added property `model_id` to `CustomFormSubmodel` and `TrainingDocumentInfo`
- Added properties `model_id` and `form_type_confidence` to `RecognizedForm`
- `appearance` property added to `FormLine` to indicate the style of extracted text - like "handwriting" or "other"
- Added keyword argument `pages` to `begin_recognize_content` and `begin_recognize_content_from_url` to specify the page
numbers to analyze
- Added property `bounding_box` to `FormTable`
- Content-type `image/bmp` now supported by recognize content and prebuilt models
- Added keyword argument `language` to `begin_recognize_content` and `begin_recognize_content_from_url` to specify
which language to process document in

**Dependency updates**

- Package now requires [azure-common](https://pypi.org/project/azure-common/) version 1.1

## 3.0.0 (2020-08-20)

First stable release of the azure-ai-formrecognizer client library.

**New features**

- Client-level, keyword argument `api_version` can be used to specify the service API version to use. Currently only v2.0
is supported. See the enum `FormRecognizerApiVersion` for supported API versions.
- `FormWord` and `FormLine` now have attribute `kind` which specifies the kind of element it is, e.g. "word" or "line"

## 3.0.0b1 (2020-08-11)

The version of this package now targets the service's v2.0 API.

**Breaking Changes**

- Client library version bumped to `3.0.0b1`
- Values are now capitalized for enums `FormContentType`, `LengthUnit`, `TrainingStatus`, and `CustomFormModelStatus`
- `document_name` renamed to `name` on `TrainingDocumentInfo`
- Keyword argument `include_sub_folders` renamed to `include_subfolders` on `begin_training` methods

**New features**

- `FormField` now has attribute `value_type` which contains the semantic data type of the field value. The options for
`value_type` are described in the enum `FieldValueType`

**Fixes and improvements**

- Fixes a bug where error code and message weren't being returned on `HttpResponseError` if operation failed during polling
- `FormField` property `value_data` is now set to `None` if no values are returned on its `FieldData`.
Previously `value_data` returned a `FieldData` with all its attributes set to `None` in the above case.


## 1.0.0b4 (2020-07-07)

**Breaking Changes**

- `RecognizedReceipts` class has been removed.
- `begin_recognize_receipts` and `begin_recognize_receipts_from_url` now return `RecognizedForm`.
- `requested_on` has been renamed to `training_started_on` and `completed_on` renamed to `training_completed_on` on `
CustomFormModel` and `CustomFormModelInfo`
- `FieldText` has been renamed to `FieldData`
- `FormContent` has been renamed to `FormElement`
- Parameter `include_text_content` has been renamed to `include_field_elements` for
`begin_recognize_receipts`, `begin_recognize_receipts_from_url`, `begin_recognize_custom_forms`, and `begin_recognize_custom_forms_from_url`
- `text_content` has been renamed to `field_elements` on `FieldData` and `FormTableCell`

**Fixes and improvements**

- Fixes a bug where `text_angle` was being returned out of the specified interval (-180, 180]

## 1.0.0b3 (2020-06-10)

**Breaking Changes**

- All asynchronous long running operation methods now return an instance of an `AsyncLROPoller` from `azure-core`
- All asynchronous long running operation methods are renamed with the `begin_` prefix to indicate that an `AsyncLROPoller` is returned:
    - `train_model` is renamed to `begin_training`
    - `recognize_receipts` is renamed to `begin_recognize_receipts`
    - `recognize_receipts_from_url` is renamed to `begin_recognize_receipts_from_url`
    - `recognize_content` is renamed to `begin_recognize_content`
    - `recognize_content_from_url` is renamed to `begin_recognize_content_from_url`
    - `recognize_custom_forms` is renamed to `begin_recognize_custom_forms`
    - `recognize_custom_forms_from_url` is renamed to `begin_recognize_custom_forms_from_url`
- Sync method `begin_train_model` renamed to `begin_training`
- `training_files` parameter of `begin_training` is renamed to `training_files_url`
- `use_labels` parameter of `begin_training` is renamed to `use_training_labels`
- `list_model_infos` method has been renamed to `list_custom_models`
- Removed `get_form_training_client` from `FormRecognizerClient`
- Added `get_form_recognizer_client` to `FormTrainingClient`
- A `HttpResponseError` is now raised if a model with `status=="invalid"` is returned from the `begin_training` methods
- `PageRange` is renamed to `FormPageRange`
- `first_page` and `last_page` renamed to `first_page_number` and `last_page_number`, respectively on `FormPageRange`
- `FormField` does not have a page_number
- `use_training_labels` is now a required positional param in the `begin_training` APIs
- `stream` and `url` parameters found on methods for `FormRecognizerClient` have been renamed to `form` and `form_url`, respectively
- For `begin_recognize_receipt` methods, parameters have been renamed to `receipt` and `receipt_url`
- `created_on` and `last_modified` are renamed to `requested_on` and `completed_on` in the
`CustomFormModel`  and `CustomFormModelInfo` models
- `models` property of `CustomFormModel` is renamed to `submodels`
- `CustomFormSubModel` is renamed to `CustomFormSubmodel`
- `begin_recognize_receipts` APIs now return a list of `RecognizedReceipt` instead of `USReceipt`
- Removed `USReceipt`. To see how to deal with the return value of `begin_recognize_receipts`, see the recognize receipt samples in the [samples directory](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples) for details.
- Removed `USReceiptItem`. To see how to access the individual items on a receipt, see the recognize receipt samples in the [samples directory](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples) for details.
- Removed `USReceiptType` and the `receipt_type` property from `RecognizedReceipt`. See the recognize receipt samples in the [samples directory](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples) for details.

**New features**

- Support to copy a custom model from one Form Recognizer resource to another
- Authentication using `azure-identity` credentials now supported
  - see the [Azure Identity documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md) for more information
- `page_number` attribute has been added to `FormTable`
- All long running operation methods now accept the keyword argument `continuation_token` to restart the poller from a saved state

**Dependency updates**

- Adopted [azure-core](https://pypi.org/project/azure-core/) version 1.6.0 or greater

## 1.0.0b2 (2020-05-06)

**Fixes and improvements**

- Bug fixed where `confidence` == `0.0` was erroneously getting set to `1.0`
- `__repr__` has been added to all of the models


## 1.0.0b1 (2020-04-23)

Version (1.0.0b1) is the first preview of our efforts to create a user-friendly and Pythonic client library for Azure Form Recognizer.
This library replaces the package found here: https://pypi.org/project/azure-cognitiveservices-formrecognizer/

For more information about this, and preview releases of other Azure SDK libraries, please visit
https://azure.github.io/azure-sdk/releases/latest/python.html.

**Breaking changes: New API design**

- New namespace/package name:
  - The namespace/package name for the Form Recognizer client library has changed from
    `azure.cognitiveservices.formrecognizer` to `azure.ai.formrecognizer`
- Two client design:
    - FormRecognizerClient to analyze fields/values on custom forms, receipts, and form content/layout
    - FormTrainingClient to train custom models (with/without labels), and manage the custom models on your account
- Different analyze methods based on input type: file stream or URL.
    - URL input should use the method with suffix `from_url`
    - Stream methods will automatically detect content-type of the input file
- Asynchronous APIs added under `azure.ai.formrecognizer.aio` namespace
- Authentication with API key supported using `AzureKeyCredential("<api_key>")` from `azure.core.credentials`
- New underlying REST pipeline implementation based on the azure-core library
- Client and pipeline configuration is now available via keyword arguments at both the client level, and per-operation.
    See README for a link to optional configuration arguments
- New error hierarchy:
    - All service errors will now use the base type: `azure.core.exceptions.HttpResponseError`
