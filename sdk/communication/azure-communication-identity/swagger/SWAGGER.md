# Azure Communication Identity for Python

> see https://aka.ms/autorest

### Setup
```ps
npm install -g autorest
```

### Generation
```ps
cd <swagger-folder>
autorest ./SWAGGER.md
```

### Settings
``` yaml
tag: package-2022-10
require:
    -  https://raw.githubusercontent.com/Azure/azure-rest-api-specs/a8c4340400f1ab1ae6a43b10e8d635ecb9c49a2a/specification/communication/data-plane/Identity/readme.md
output-folder: ../azure/communication/identity/_generated/
namespace: azure.communication.identity
title: Communication Identity Client
license-header: MICROSOFT_MIT_NO_VERSION
payload-flattening-threshold: 3
no-namespace-folders: true
clear-output-folder: true
v3: true
python: true
models-mode: msrest
```

### Rename CommunicationIdentityTokenScope to CommunicationTokenScope
```yaml
directive:
  - from: swagger-document
    where: $.definitions.CommunicationIdentityTokenScope
    transform: >
      $["x-ms-enum"].name = "CommunicationTokenScope";