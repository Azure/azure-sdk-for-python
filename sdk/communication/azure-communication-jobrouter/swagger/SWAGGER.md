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
input-file: ./swagger.json
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