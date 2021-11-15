
# Azure Communication Media Composition for Python

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
tag: package-2021-12-31-preview
require: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/e00ba9e22c4d70d005625f6798807a3ecc5b59a9/specification/communication/data-plane/MediaComposition/readme.md
output-folder: ../azure/communication/mediacomposition/_generated/
namespace: azure.communication.mediacomposition
license-header: MICROSOFT_MIT_NO_VERSION
payload-flattening-threshold: 3
no-namespace-folders: true
clear-output-folder: true
v3: true
python: true
title: Communication Media Composition Client
```