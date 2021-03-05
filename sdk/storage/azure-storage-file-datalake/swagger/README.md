# Azure DataLake for Python

> see https://aka.ms/autorest

### Setup
Install Autorest v3
```ps
npm install -g autorest
```

### Generation
```ps
cd <swagger-folder>
autorest --v3 --python
```

### Settings
``` yaml
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/storage-dataplane-preview/specification/storage/data-plane/Microsoft.StorageDataLake/stable/2020-02-10/DataLakeStorage.json
output-folder: ../azure/storage/filedatalake/_generated
namespace: azure.storage.filedatalake
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
enable-xml: true
vanilla: true
clear-output-folder: true
python: true
```