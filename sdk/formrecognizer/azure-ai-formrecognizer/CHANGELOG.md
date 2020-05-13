# Change Log azure-ai-formrecognizer

## 1.0.0b3 (Unreleased)

**Breaking Changes**

- `training_files` parameter of `begin_train_model` is renamed to `training_files_url`
- `use_labels` parameter of `begin_train_model` is renamed to `use_training_labels`
- `list_model_infos` method has been renamed to `list_custom_models`
- Removed `get_form_training_client` from `FormRecognizerClient`
- Added `get_form_recognizer_client` to `FormTrainingClient`

**New features**

- Authentication using `azure-identity` credentials now supported
  - see the [Azure Identity documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity/README.md) for more information


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
