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
tag: package-2024-01-14-preview
require: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/4ad21c4cd5f024b520b77907b8ac15fb84c8413a/specification/communication/data-plane/Sms/readme.md
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
  "@autorest/python": "5.9.3"
```

### Directive renaming "MmsSendRequestAttachment" property to "MmsAttachment" in MMS
``` yaml
directive:
    from: swagger-document
    where: '$.definitions.MmsSendRequestAttachment'
    transform: >
        $["x-ms-client-name"] = "MmsAttachment";
```