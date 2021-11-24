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
require: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/c2e5ae3e6d0bb5ea80493740de9d35c0ab1fe763/specification/communication/data-plane/CallingServer/readme.md
output-folder: ../azure/communication/callingserver/_generated
namespace: azure.communication.callingserver
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
enable-xml: true
clear-output-folder: true
python: true
v3: true
no-async: false
add-credential: false
title: Azure Communication CallingServer Service
```