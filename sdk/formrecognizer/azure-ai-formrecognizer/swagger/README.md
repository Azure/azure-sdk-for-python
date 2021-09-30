## Python Form Recognizer

To generate this file, simply type

```
autorest swagger/README.md --python-sdks-folder=<path to the root directory of your azure-sdk-for-python clone>
```

We automatically hardcode in that this is `python` and `multiapi`.

## Basic

``` yaml
license-header: MICROSOFT_MIT_NO_VERSION
add-credential: true
namespace: azure.ai.formrecognizer
package-name: azure-ai-formrecognizer
credential-scopes: https://cognitiveservices.azure.com/.default
clear-output-folder: true
no-namespace-folders: true
python: true
multiapi: true
```

## Multiapi Batch Execution

```yaml $(multiapi)
batch:
  - tag: release_2_0
  - tag: release_2_1
  - tag: release_2021_09_30_preview
  - multiapiscript: true
```

## Multiapiscript

```yaml $(multiapiscript)
output-folder: $(python-sdks-folder)/formrecognizer/azure-ai-formrecognizer/azure/ai/formrecognizer/_generated/
default-api: 2021-09-30-preview
clear-output-folder: true
perform-load: false
```

## Release 2.0

These settings apply only when `--tag=release_2_0` is specified on the command line.


``` yaml $(tag) == 'release_2_0'
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/cognitiveservices/data-plane/FormRecognizer/stable/v2.0/FormRecognizer.json
namespace: azure.ai.formrecognizer.v2_0
output-folder: $(python-sdks-folder)/formrecognizer/azure-ai-formrecognizer/azure/ai/formrecognizer/_generated/v2_0
```

## Release 2.1

These settings apply only when `--tag=release_2_1` is specified on the command line.

``` yaml $(tag) == 'release_2_1'
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/cognitiveservices/data-plane/FormRecognizer/stable/v2.1/FormRecognizer.json
namespace: azure.ai.formrecognizer.v2_1
output-folder: $(python-sdks-folder)/formrecognizer/azure-ai-formrecognizer/azure/ai/formrecognizer/_generated/v2_1
```

## Release 3.1-preview

These settings apply only when `--tag=release_2021_09_30_preview` is specified on the command line.

``` yaml $(tag) == 'release_2021_09_30_preview'
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs-pr/8881ef0f39b9c002c9fd84fa355421e3e3cc385d/specification/cognitiveservices/data-plane/FormRecognizer/preview/2021-09-30-preview/FormRecognizer.json?token=AHUEAM5YOKH3SWW7BUF7EUDBK6KHS
namespace: azure.ai.formrecognizer.v2021_09_30_preview
output-folder: $(python-sdks-folder)/formrecognizer/azure-ai-formrecognizer/azure/ai/formrecognizer/_generated/v2021_09_30_preview
```


### Override with DocumentModelAdministrationLROPoller

``` yaml
directive:
    -   from: swagger-document
        where: '$.paths["/documentModels:build"].post'
        transform: >
            $["x-python-custom-poller-sync"] = "...._polling.DocumentModelAdministrationLROPoller";
            $["x-python-custom-poller-async"] = ".....aio._async_polling.AsyncDocumentModelAdministrationLROPoller";
```

``` yaml
directive:
    -   from: swagger-document
        where: '$.paths["/documentModels:compose"].post'
        transform: >
            $["x-python-custom-poller-sync"] = "...._polling.DocumentModelAdministrationLROPoller";
            $["x-python-custom-poller-async"] = ".....aio._async_polling.AsyncDocumentModelAdministrationLROPoller";
```

``` yaml
directive:
    -   from: swagger-document
        where: '$.paths["/documentModels/{modelId}:copyTo"].post'
        transform: >
            $["x-python-custom-poller-sync"] = "...._polling.DocumentModelAdministrationLROPoller";
            $["x-python-custom-poller-async"] = ".....aio._async_polling.AsyncDocumentModelAdministrationLROPoller";
```