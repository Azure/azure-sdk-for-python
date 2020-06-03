# Change Log azure-ai-formrecognizer

## 1.0.0b3 (Unreleased)

**Breaking Changes**

- `training_files` parameter of `begin_train_model` is renamed to `training_files_url`
- `use_labels` parameter of `begin_train_model` is renamed to `use_training_labels`
- `list_model_infos` method has been renamed to `list_custom_models`
- Removed `get_form_training_client` from `FormRecognizerClient`
- Added `get_form_recognizer_client` to `FormTrainingClient`
- A `HttpResponseError` is now raised if a model with `status=="invalid"` is returned from the `begin_train_model()` or `train_model()` methods
- `PageRange` is renamed to `FormPageRange`
- `first_page` and `last_page` renamed to `first_page_number` and `last_page_number`, respectively on `FormPageRange`
- `FormField` does not have a page_number.
- `begin_recognize_receipts` APIs now return `RecognizedReceipt` instead of `USReceipt`
- `USReceiptType` is renamed to `ReceiptType`
- `use_training_labels` is now a required positional param in the `begin_training` APIs.
- `stream` and `url` parameters found on methods for `FormRecognizerClient` have been renamed to `form` and `form_url`, respectively.
- For recognize receipt methods, parameters have been renamed to `receipt` and `receipt_url`.
- `created_on` and `last_modified` are renamed to `requested_on` and `completed_on` in the
`CustomFormModel`  and `CustomFormModelInfo` models.
- `models` property of `CustomFormModel` is renamed to `submodels`
- `CustomFormSubModel` is renamed to `CustomFormSubmodel`
- Removed `USReceipt`. To see how to deal with the return value of `begin_recognize_receipts`, see [sample_recognize_receipts.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_recognize_receipts.py) or [sample_recognize_receipts_from_url.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_recognize_receipts_from_url.py) for details.
- Removed `USReceiptItem`. To see how to access the individual items on a receipt, see [sample_recognize_receipts.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_recognize_receipts.py) or [sample_recognize_receipts_from_url.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_recognize_receipts_from_url.py) for details.
- Removed `ReceiptType` and the `receipt_type` property from `RecogniedReceipt`. See sample_recognize_receipts.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_recognize_receipts.py) or [sample_recognize_receipts_from_url.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_recognize_receipts_from_url.py) for details.

**New features**

- Support to copy a custom model from one Form Recognizer resource to another
- Authentication using `azure-identity` credentials now supported
  - see the [Azure Identity documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity/README.md) for more information
- `page_number` attribute has been added to `FormTable`

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
