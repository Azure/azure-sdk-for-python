# Text Analytics for Python

To generate this file, simply type

```
autorest swagger/README.md --python-sdks-folder=<path to the root directory of your azure-sdk-for-python clone>
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
python3-only: true
```

## Multiapi Batch Execution

```yaml $(multiapi)
batch:
  - tag: release_3_0
  - tag: release_3_1
  - tag: release_2022_05_01
  - multiapiscript: true
```

## Multiapiscript

```yaml $(multiapiscript)
output-folder: $(python-sdks-folder)/textanalytics/azure-ai-textanalytics/azure/ai/textanalytics/_generated/
default-api: v3.1
clear-output-folder: true
perform-load: false
```

## Release 3.0

These settings apply only when `--tag=release_3_0` is specified on the command line.

```yaml $(tag) == 'release_3_0'
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/cognitiveservices/data-plane/TextAnalytics/stable/v3.0/TextAnalytics.json
namespace: azure.ai.textanalytics.v3_0
output-folder: $(python-sdks-folder)/textanalytics/azure-ai-textanalytics/azure/ai/textanalytics/_generated/v3_0
```

## Release 3.1

These settings apply only when `--tag=release_3_1` is specified on the command line.

```yaml $(tag) == 'release_3_1'
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/cognitiveservices/data-plane/TextAnalytics/stable/v3.1/TextAnalytics.json
namespace: azure.ai.textanalytics.v3_1
output-folder: $(python-sdks-folder)/textanalytics/azure-ai-textanalytics/azure/ai/textanalytics/_generated/v3_1
```

## Release v2022_05_01

These settings apply only when `--tag=release_2022_05_01` is specified on the command line.

```yaml $(tag) == 'release_2022_05_01'
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/cognitiveservices/data-plane/Language/stable/2022-05-01/textanalytics.json
namespace: azure.ai.textanalytics.v2022_05_01
output-folder: $(python-sdks-folder)/textanalytics/azure-ai-textanalytics/azure/ai/textanalytics/_generated/v2022_05_01
```

### Override Analyze's pager poller for v3.1

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

### Override Healthcare's poller for v3.1

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

### Override Analyze's pager poller for 2022_05_01

```yaml
directive:
  - from: swagger-document
    where: '$.paths["/analyze-text/jobs"].post'
    transform: >
      $["responses"]["200"] = {"description": "dummy schema", "schema": {"$ref": "#/definitions/AnalyzeTextJobState"}};
      $["x-python-custom-poller-sync"] = "...._lro.AnalyzeActionsLROPoller";
      $["x-python-custom-poller-async"] = ".....aio._lro_async.AsyncAnalyzeActionsLROPoller";
      $["x-python-custom-default-polling-method-sync"] = "...._lro.AnalyzeActionsLROPollingMethod";
      $["x-python-custom-default-polling-method-async"] = ".....aio._lro_async.AsyncAnalyzeActionsLROPollingMethod";
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

### Fix naming clash with analyze_text method in ApiVersion v2022_05_01

```yaml $(tag) == 'release_2022_05_01'
directive:
  - from: swagger-document
    where: '$["paths"]["/analyze-text/jobs"]["post"]'
    transform: >
      $["operationId"] = "AnalyzeTextSubmitJob";
```

### Fix naming clash with analyze_text method in ApiVersion v2022_05_01

```yaml $(tag) == 'release_2022_05_01'
directive:
  - from: swagger-document
    where: '$["paths"]["/analyze-text/jobs/{jobId}"]["get"]'
    transform: >
      $["operationId"] = "AnalyzeTextJobStatus";
```

### Fix naming clash with analyze_text method in ApiVersion v2022_05_01

```yaml $(tag) == 'release_2022_05_01'
directive:
  - from: swagger-document
    where: '$["paths"]["/analyze-text/jobs/{jobId}:cancel"]["post"]'
    transform: >
      $["operationId"] = "AnalyzeTextCancelJob";
```

### Fix generation of operation class name with ApiVersion v2022_05_01

```yaml $(tag) == 'release_2022_05_01'
directive:
  - from: swagger-document
    where: '$["info"]'
    transform: >
      $["title"] = "Text Analytics Client";
```
