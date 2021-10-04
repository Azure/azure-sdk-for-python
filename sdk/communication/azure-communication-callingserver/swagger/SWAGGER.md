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
require: https://raw.githubusercontent.com/navali-msft/azure-rest-api-specs/c55dac6666919f6c7d6d2a280c6e002c647b15f6/specification/communication/data-plane/CallingServer/readme.md
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