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
  - tag: release_3_1
  - tag: release_3_2_preview.1
  - multiapiscript: true
```

## Multiapiscript

```yaml $(multiapiscript)
output-folder: ../azure/ai/textanalytics/_generated/
default-api: v3_2_preview_1
clear-output-folder: true
perform-load: false
```

## Release 3.0

These settings apply only when `--tag=release_3_0` is specified on the command line.

```yaml $(tag) == 'release_3_0'
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/specification/cognitiveservices/data-plane/TextAnalytics/stable/v3.0/TextAnalytics.json
namespace: azure.ai.textanalytics.v3_0
output-folder: ../azure/ai/textanalytics/_generated/v3_0
```

## Release 3.1

These settings apply only when `--tag=release_3_1` is specified on the command line.

```yaml $(tag) == 'release_3_1'
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/specification/cognitiveservices/data-plane/TextAnalytics/stable/v3.1/TextAnalytics.json
namespace: azure.ai.textanalytics.v3_1
output-folder: ../azure/ai/textanalytics/_generated/v3_1
```

## Release 3.2-preview.1

These settings apply only when `--tag=release_3_2_preview.1` is specified on the command line.

```yaml $(tag) == 'release_3_2_preview.1'
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/143ac79e3cfa029217315bd96c3cd58f35bf35f9/specification/cognitiveservices/data-plane/TextAnalytics/preview/v3.2-preview.1/TextAnalytics.json
namespace: azure.ai.textanalytics.v3_2_preview_1
output-folder: ../azure/ai/textanalytics/_generated/v3_2_preview_1
```

### Override Analyze's pager poller

```yaml
directive:
  - from: swagger-document
    where: '$.paths["/analyze"].post'
    transform: >
      $["responses"]["200"] = {"description": "dummy schema", "schema": {"$ref": "#/definitions/AnalyzeJobState"}};
      $["x-python-custom-poller-sync"] = "...._lro.AnalyzeActionsLROPoller";
      $["x-python-custom-poller-async"] = ".....aio._lro_async.AsyncAnalyzeActionsLROPoller";
      $["x-python-custom-default-polling-method-sync"] = "...._lro.AnalyzeActionsLROPollingMethod";
      $["x-python-custom-default-polling-method-async"] = ".....aio._lro_async.AsyncAnalyzeActionsLROPollingMethod";
```

### Override Healthcare's poller

```yaml
directive:
  - from: swagger-document
    where: '$.paths["/entities/health/jobs"].post'
    transform: >
      $["responses"]["200"] = {"description": "dummy schema", "schema": {"$ref": "#/definitions/HealthcareJobState"}};
      $["x-python-custom-poller-sync"] = "...._lro.AnalyzeHealthcareEntitiesLROPoller";
      $["x-python-custom-poller-async"] = ".....aio._lro_async.AsyncAnalyzeHealthcareEntitiesLROPoller";
      $["x-python-custom-default-polling-method-sync"] = "...._lro.AnalyzeHealthcareEntitiesLROPollingMethod";
      $["x-python-custom-default-polling-method-async"] = ".....aio._lro_async.AsyncAnalyzeHealthcareEntitiesLROPollingMethod";
```

### Override parameterizing the ApiVersion v3.1

```yaml $(tag) == 'release_3_1'
directive:
  - from: swagger-document
    where: '$["x-ms-parameterized-host"]'
    transform: >
      $["hostTemplate"] = "{Endpoint}/text/analytics/v3.1";
      $["parameters"] = [{"$ref": "#/parameters/Endpoint"}];
```

### Override parameterizing the ApiVersion v3.2-preview.1

```yaml $(tag) == 'release_3_2_preview.1'
directive:
  - from: swagger-document
    where: '$["x-ms-parameterized-host"]'
    transform: >
      $["hostTemplate"] = "{Endpoint}/text/analytics/v3.2-preview.1";
      $["parameters"] = [{"$ref": "#/parameters/Endpoint"}];
```