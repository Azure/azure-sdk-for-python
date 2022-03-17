
# Azure Communication Network Traversal for Python

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
tag: package-2022-02-01
require: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/1824478ffd262205f5e7ea8218b1d667fe091d9d/specification/communication/data-plane/NetworkTraversal/readme.md
output-folder: ../azure/communication/networktraversal/_generated/
namespace: azure.communication.networktraversal
license-header: MICROSOFT_MIT_NO_VERSION
payload-flattening-threshold: 3
no-namespace-folders: true
clear-output-folder: true
v3: true
python: true
title: Communication Network Traversal Client
```