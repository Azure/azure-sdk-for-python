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
tag: package-sms-2026-01-23
require: C:\azure-rest-api-specs\specification\communication\data-plane\Sms\readme.md
output-folder: ../azure/communication/sms/_generated
namespace: azure.communication.sms
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
enable-xml: true
clear-output-folder: true
python: true
v3: true
no-async: false
add-credential: false
title: Azure Communication SMS Service
use-extension:
  "@autorest/python": "6.1.1"
```