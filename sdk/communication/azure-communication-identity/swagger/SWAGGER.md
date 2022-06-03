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
tag: package-preview-2021-10
require:
    -  https://raw.githubusercontent.com/Azure/azure-rest-api-specs/6f40b65610a4fad7a03f3fe8c57e8c0a9c3b77d0/specification/communication/data-plane/Identity/readme.md
output-folder: ../azure/communication/identity/_generated/
namespace: azure.communication.identity
license-header: MICROSOFT_MIT_NO_VERSION
payload-flattening-threshold: 3
no-namespace-folders: true
clear-output-folder: true
v3: true
python: true
title: Communication Identity Client
```

### Rename CommunicationIdentityTokenScope to CommunicationTokenScope
```yaml
directive:
  - from: swagger-document
    where: $.definitions.CommunicationIdentityTokenScope
    transform: >
      $["x-ms-enum"].name = "CommunicationTokenScope";