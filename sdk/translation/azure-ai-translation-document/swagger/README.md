# Document Translation for Python

To generate this file, simply type

```
autorest swagger/README.md --python-sdks-folder=<location-of-your-sdk-dir>
```

We automatically hardcode in that this is `python`.

## Basic

```yaml
license-header: MICROSOFT_MIT_NO_VERSION
add-credentials: true
payload-flattening-threshold: 2
namespace: azure.ai.translation.document
package-name: azure-ai-translation-document
clear-output-folder: true
credential-scopes: https://cognitiveservices.azure.com/.default
no-namespace-folders: true
python: true
models-mode: msrest
```


## Release 1.0

These settings apply only when `--tag=release_1_0` is specified on the command line.

``` yaml $(tag) == 'release_1_0'
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/specification/cognitiveservices/data-plane/TranslatorText/stable/v1.0/TranslatorBatch.json
output-folder: ../azure/ai/translation/document/_generated/
```


### Override Document Translation poller

``` yaml
directive:
    -   from: swagger-document
        where: '$.paths["/batches"].post'
        transform: >
            $["x-python-custom-poller-sync"] = "..._polling.DocumentTranslationLROPoller";
            $["x-python-custom-poller-async"] = "....aio._async_polling.AsyncDocumentTranslationLROPoller";
            $["x-python-custom-default-polling-method-sync"] = "..._polling.DocumentTranslationLROPollingMethod";
            $["x-python-custom-default-polling-method-async"] = "....aio._async_polling.AsyncDocumentTranslationLROPollingMethod";
```
