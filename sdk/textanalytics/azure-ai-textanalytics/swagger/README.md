# Text Analytics for Python

To generate this file, simply type

```
autorest swagger/README.md
```

We automatically hardcode in that this is `python` and `multiapi`.

## Basic

```yaml
license-header: MICROSOFT_MIT_NO_VERSION
add-credential: true
payload-flattening-threshold: 2
package-name: azure-ai-textanalytics
clear-output-folder: true
credential-scopes: https://cognitiveservices.azure.com/.default
no-namespace-folders: true
python: true
multiapi: true
```

## Multiapi Batch Execution

```yaml $(multiapi)
batch:
 - tag: release_3_0
 - tag: release_3_1_preview.4
 - multiapiscript: true
```

## Multiapiscript

``` yaml $(multiapiscript)
output-folder: ../azure/ai/textanalytics/_generated/
default-api: v3_0
clear-output-folder: false
perform-load: false
```

## Release 3.0

These settings apply only when `--tag=release_3_0` is specified on the command line.

``` yaml $(tag) == 'release_3_0'
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/specification/cognitiveservices/data-plane/TextAnalytics/stable/v3.0/TextAnalytics.json
namespace: azure.ai.textanalytics.v3_0
output-folder: ../azure/ai/textanalytics/_generated/v3_0
```

## Release 3.1-Preview.4

These settings apply only when `--tag=release_3_1_preview.4` is specified on the command line.

```yaml $(tag) == 'release_3_1_preview.4'
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/specification/cognitiveservices/data-plane/TextAnalytics/preview/v3.1-preview.4/TextAnalytics.json
namespace: azure.ai.textanalytics.v3_1_preview_4
output-folder: ../azure/ai/textanalytics/_generated/v3_1_preview_4
```

### Override Analyze's pager and poller

``` yaml
directive:
    -   from: swagger-document
        where: '$.paths["/analyze"].post'
        transform: >
            $["responses"]["200"] = {"description": "dummy schema", "schema": {"$ref": "#/definitions/AnalyzeJobState"}};
            $["x-python-custom-poller-sync"] = "...._lro.AnalyzeBatchActionsLROPoller";
            $["x-python-custom-poller-async"] = "....._async_lro.AsyncAnalyzeBatchActionsLROPoller";
            $["x-python-custom-default-polling-method-sync"] = "...._lro.AnalyzeBatchActionsLROPollingMethod";
            $["x-python-custom-default-polling-method-async"] = "....._async_lro.AsyncAnalyzeBatchActionsLROPollingMethod";
```


### Override Healthcare's pager and poller

``` yaml
directive:
    -   from: swagger-document
        where: '$.paths["/entities/health/jobs"].post'
        transform: >
            $["responses"]["200"] = {"description": "dummy schema", "schema": {"$ref": "#/definitions/HealthcareJobState"}};
            $["x-python-custom-poller-sync"] = "...._lro.AnalyzeHealthcareEntitiesLROPoller";
            $["x-python-custom-poller-async"] = "....._async_lro.AnalyzeHealthcareEntitiesAsyncLROPoller";
            $["x-python-custom-default-polling-method-sync"] = "...._lro.AnalyzeHealthcareEntitiesLROPollingMethod";
            $["x-python-custom-default-polling-method-async"] = "....._async_lro.AnalyzeHealthcareEntitiesAsyncLROPollingMethod";
```
