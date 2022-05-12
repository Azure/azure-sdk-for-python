# Azure Communication Configuration for Python

> see https://aka.ms/autorest

### Setup
```ps
npm install -g autorest
```

### Generation
```ps
cd <swagger-folder>
autorest SWAGGER.md
```

### Settings

``` yaml
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/communication/data-plane/JobRouter/preview/2021-10-20-preview2/communicationservicejobrouter.json
output-folder: ../azure/communication/jobrouter/_generated
namespace: azure.communication.jobrouter
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
enable-xml: true
clear-output-folder: true
python: true
v3: true
no-async: false
add-credential: false
title: Azure Communication Job Router Service
disable-async-iterators: true
```

### Set reference to WorkerSelectorAttachment in ClassificationPolicy
```yaml
directive:
  - from: swagger-document
    where: "$.definitions.ClassificationPolicy.properties.workerSelectors.items"
    transform: >
      $["$ref"] = "#/definitions/WorkerSelectorAttachment";
```

### Set reference to QueueSelectorAttachment in ClassificationPolicy
```yaml
directive:
  - from: swagger-document
    where: "$.definitions.ClassificationPolicy.properties.queueSelectors.items"
    transform: >
      $["$ref"] = "#/definitions/QueueSelectorAttachment";
```

### Set reference to WorkerSelectorAttachment in PagedClassificationPolicy
```yaml
directive:
  - from: swagger-document
    where: "$.definitions.PagedClassificationPolicy.properties.workerSelectors.items"
    transform: >
      $["$ref"] = "#/definitions/WorkerSelectorAttachment";
```

### Set reference to QueueSelectorAttachment in PagedClassificationPolicy
```yaml
directive:
  - from: swagger-document
    where: "$.definitions.PagedClassificationPolicy.properties.queueSelectors.items"
    transform: >
      $["$ref"] = "#/definitions/QueueSelectorAttachment";
```

### Set reference to ExceptionAction in ExceptionRule
```yaml
directive:
  - from: swagger-document
    where: "$.definitions.ExceptionRule.properties.actions"
    transform: >
      $.type = "object";
      $.additionalProperties["$ref"] = "#/definitions/ExceptionAction";
```


### Rename CommunicationError to JobRouterError
```yaml
directive:
  from: swagger-document
  where: '$.definitions.CommunicationError'
  transform: >
    $["x-ms-client-name"] = "JobRouterError";
```

### Rename JobQueue to JobQueueInternal
```yaml
directive:
  from: swagger-document
  where: '$.definitions.JobQueue'
  transform: >
    $["x-ms-client-name"] = "JobQueueInternal";
```

### Rename RouterWorker to RouterWorkerInternal
```yaml
directive:
  from: swagger-document
  where: '$.definitions.RouterWorker'
  transform: >
    $["x-ms-client-name"] = "RouterWorkerInternal";
```