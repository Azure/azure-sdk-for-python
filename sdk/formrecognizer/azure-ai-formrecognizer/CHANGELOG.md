# Release History

## 3.1.0b4 (Unreleased)

**New features**

- New methods `begin_recognize_id_documents` and `begin_recognize_id_documents_from_url` introduced to the SDK. Use these methods to recognize data from identity documents.
- Content-type `image/bmp` now supported by custom forms and training methods.
- Added keyword argument `pages` for business cards, receipts, custom forms, and invoices 
to specify which page to process of the document.

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
- Removed `USReceipt`. To see how to deal with the return value of `begin_recognize_receipts`, see the recognize receipt samples in the [samples directory](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/formrecognizer/azure-ai-formrecognizer/samples) for details.
- Removed `USReceiptItem`. To see how to access the individual items on a receipt, see the recognize receipt samples in the [samples directory](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/formrecognizer/azure-ai-formrecognizer/samples) for details.
- Removed `USReceiptType` and the `receipt_type` property from `RecognizedReceipt`. See the recognize receipt samples in the [samples directory](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/formrecognizer/azure-ai-formrecognizer/samples) for details.

**New features**

- Support to copy a custom model from one Form Recognizer resource to another
- Authentication using `azure-identity` credentials now supported
  - see the [Azure Identity documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity/README.md) for more information
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
