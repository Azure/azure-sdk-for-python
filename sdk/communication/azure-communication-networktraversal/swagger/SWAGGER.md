
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
tag: package-2021-10-08-preview
require: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/f2e08ab373eb0e96b54920e89f9fc96d683355ca/specification/communication/data-plane/NetworkTraversal/readme.md
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