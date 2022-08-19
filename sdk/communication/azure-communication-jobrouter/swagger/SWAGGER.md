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
tag: package-jobrouter-2022-07-18-preview
require: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/c350a26aa5bd64ccc7a768f2cb5464a1cbe825e5/specification/communication/data-plane/JobRouter/readme.md
output-folder: ../azure/communication/jobrouter/_generated
models-mode: msrest
namespace: azure.communication.jobrouter
package-name: azure-communication-jobrouter
license-header: MICROSOFT_MIT_NO_VERSION
enable-xml: true
clear-output-folder: true
no-namespace-folders: true
python: true
v3: true
no-async: false
add-credential: false
title: Azure Communication Job Router Service
```

### Rename JobQueue to JobQueueInternal
```yaml
directive:
  from: swagger-document
  where: '$.definitions.JobQueue'
  transform: >
    $["x-ms-client-name"] = "JobQueueInternal";
```

### Rename JobQueueItem to JobQueueItemInternal
```yaml
directive:
  from: swagger-document
  where: '$.definitions.JobQueueItem'
  transform: >
    $["x-ms-client-name"] = "JobQueueItemInternal";
```

### Rename RouterWorker to RouterWorkerInternal
```yaml
directive:
  from: swagger-document
  where: '$.definitions.RouterWorker'
  transform: >
    $["x-ms-client-name"] = "RouterWorkerInternal";
```

### Rename RouterWorkerItem to RouterWorkerItemInternal
```yaml
directive:
  from: swagger-document
  where: '$.definitions.RouterWorkerItem'
  transform: >
    $["x-ms-client-name"] = "RouterWorkerItemInternal";
```


### Rename RouterJob to RouterJobInternal
```yaml
directive:
  from: swagger-document
  where: '$.definitions.RouterJob'
  transform: >
    $["x-ms-client-name"] = "RouterJobInternal";
```

### Rename RouterJobItem to RouterJobItemInternal
```yaml
directive:
  from: swagger-document
  where: '$.definitions.RouterJobItem'
  transform: >
    $["x-ms-client-name"] = "RouterJobItemInternal";
```