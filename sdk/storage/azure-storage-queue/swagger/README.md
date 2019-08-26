# Azure Queue Storage for Python

> see https://aka.ms/autorest

### Setup
```ps
cd C:\work
git clone --recursive https://github.com/Azure/autorest.python.git
cd autorest.python
git checkout azure-core
npm install
```

### Generation
```ps
cd <swagger-folder>
autorest --use=C:/work/autorest.python --version=2.0.4280
```

### Settings
``` yaml
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/storage-dataplane-preview/specification/storage/data-plane/Microsoft.QueueStorage/preview/2018-03-28/queue.json
output-folder: ../azure/storage/queue/_generated
namespace: azure.storage.queue
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
enable-xml: true
vanilla: true
clear-output-folder: true
python: true
```

### Remove x-ms-pageable
Currently breaking the latest version of autorest.python
``` yaml
directive:
- from: swagger-document
  where: $["x-ms-paths"]..get
  transform: >
    if ($["x-ms-pageable"]) { delete $["x-ms-pageable"]; }
```

### Use strings for dates when python doesn't have enough precision
``` yaml
directive:
- from: swagger-document
  where: $.definitions.AccessPolicy.properties
  transform: >
    $.Start.format = "str";
    $.Expiry.format = "str";
```

### SignedIdentifier shouldn't require an AccessPolicy, only ID
``` yaml
directive:
- from: swagger-document
  where: $.definitions.SignedIdentifier
  transform: >
    $.required = [ "Id" ];
```

### QueueMessage is required for enqueue, but not for update
``` yaml
directive:
- from: swagger-document
  where: $.parameters.QueueMessage
  transform: >
    $.required = false;
```
