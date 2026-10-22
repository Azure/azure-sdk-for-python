# Release History

## 1.0.0b2 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes

## 1.0.0b1 (2022-11-07)

### Features Added
- New namespace/package name:
  - The namespace/package name for the Personalizer client library has changed from
    `azure.cognitiveservices.personalizer` to `azure.ai.personalizer`
- Asynchronous APIs added under `azure.ai.personalizer.aio` namespace
- Authentication with AAD supported
- Authentication with API key supported using `AzureKeyCredential("<api_key>")` from `azure.core.credentials`
- New underlying REST pipeline implementation based on the azure-core library
- New error hierarchy:
    - All service errors will now use the base type: `azure.core.exceptions.HttpResponseError`

### Breaking Changes
- Version (1.0.0b1) is the first preview of our efforts to create a user-friendly and Pythonic client library for Azure Personalizer.
- This library replaces the package found here: https://pypi.org/project/azure-cognitiveservices-personalizer/

For more information about this, and preview releases of other Azure SDK libraries, please visit
https://azure.github.io/azure-sdk/releases/latest/python.html.
