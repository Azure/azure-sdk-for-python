# Azure DataLake for Python

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
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/storage-dataplane-preview/specification/storage/data-plane/Microsoft.StorageDataLake/stable/2018-11-09/DataLakeStorage.json
output-folder: ../azure/storage/filedatalake/_generated
namespace: azure.storage.filedatalake
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
enable-xml: true
vanilla: true
clear-output-folder: true
python: true
```