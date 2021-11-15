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
require: https://raw.githubusercontent.com/navali-msft/azure-rest-api-specs/f63c517df5083d1f3d044277bac15c6b1ed2b060/specification/communication/data-plane/CallingServer/readme.md
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