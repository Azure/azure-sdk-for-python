## Python Form Recognizer

To generate this file, simply type:

```
autorest --use=@autorest/python@5.16.0 swagger/README.md --python-sdks-folder=<path to the root directory of your azure-sdk-for-python clone>
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
version-tolerant: false
python3-only: true
```

## Multiapi Batch Execution

```yaml $(multiapi)
batch:
  - tag: release_2_0
  - tag: release_2_1
  - tag: release_2022_08_31
  - tag: release_2023_07_31
  - multiapiscript: true
```

## Multiapiscript

```yaml $(multiapiscript)
output-folder: $(python-sdks-folder)/formrecognizer/azure-ai-formrecognizer/azure/ai/formrecognizer/_generated/
default-api: v2_1
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

## Release 3.1

These settings apply only when `--tag=release_2022_08_31` is specified on the command line.

``` yaml $(tag) == 'release_2022_08_31'
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/64484dc8760571a2de7f5cfbc96861e4a0985a54/specification/cognitiveservices/data-plane/FormRecognizer/stable/2022-08-31/FormRecognizer.json
namespace: azure.ai.formrecognizer.v2022_08_31
output-folder: $(python-sdks-folder)/formrecognizer/azure-ai-formrecognizer/azure/ai/formrecognizer/_generated/v2022_08_31
```

## Release 3.2

These settings apply only when `--tag=release_2023_07_31` is specified on the command line.

``` yaml $(tag) == 'release_2023_07_31'
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/83eb6fffa205037f1c9675ff0c098656db6fc6dd/specification/cognitiveservices/data-plane/FormRecognizer/stable/2023-07-31/FormRecognizer.json
namespace: azure.ai.formrecognizer.v2023_07_31
output-folder: $(python-sdks-folder)/formrecognizer/azure-ai-formrecognizer/azure/ai/formrecognizer/_generated/v2023_07_31
```


### Override with DocumentModelAdministrationClientLROPoller

``` yaml
directive:
    -   from: swagger-document
        where: '$.paths["/documentModels:build"].post'
        transform: >
            $["x-python-custom-poller-sync"] = "...._polling.DocumentModelAdministrationClientLROPoller";
            $["x-python-custom-poller-async"] = ".....aio._async_polling.AsyncDocumentModelAdministrationClientLROPoller";
```

``` yaml
directive:
    -   from: swagger-document
        where: '$.paths["/documentModels:compose"].post'
        transform: >
            $["x-python-custom-poller-sync"] = "...._polling.DocumentModelAdministrationClientLROPoller";
            $["x-python-custom-poller-async"] = ".....aio._async_polling.AsyncDocumentModelAdministrationClientLROPoller";
```

``` yaml
directive:
    -   from: swagger-document
        where: '$.paths["/documentModels/{modelId}:copyTo"].post'
        transform: >
            $["x-python-custom-poller-sync"] = "...._polling.DocumentModelAdministrationClientLROPoller";
            $["x-python-custom-poller-async"] = ".....aio._async_polling.AsyncDocumentModelAdministrationClientLROPoller";
```

``` yaml
directive:
    -   from: swagger-document
        where: '$.paths["/documentClassifiers:build"].post'
        transform: >
            $["x-python-custom-poller-sync"] = "...._polling.DocumentModelAdministrationClientLROPoller";
            $["x-python-custom-poller-async"] = ".....aio._async_polling.AsyncDocumentModelAdministrationClientLROPoller";
```

### Override unique items in composed models due to msrest validation issue

``` yaml
directive:
    -   from: swagger-document
        where: '$.definitions["ComposeDocumentModelRequest"].properties'
        transform: >
            $["componentModels"].uniqueItems = false
```
