# Azure Communication Services Email REST API Client

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
package-version: 1.0.0b2
tag: package-2023-01-15-preview
require: https://raw.githubusercontent.com/apattath/azure-rest-api-specs-apattath/2beb92d3d6c70d683183192bab3beac8bef09322/specification/communication/data-plane/Email/readme.md
output-folder: ../azure/communication/email/_generated
namespace: azure.communication.email
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
enable-xml: true
clear-output-folder: true
python: true
v3: true
no-async: false
add-credential: false
security: Anonymous
title: Azure Communication Email Service
use-extension:
  "@autorest/python": "6.1.1"
```
