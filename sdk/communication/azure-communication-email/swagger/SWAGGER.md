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
package-version: 1.0.0b1
tag: package-2021-10-01-preview
require: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/communication/data-plane/Email/readme.md
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
```

### Change the bCC property to bcc
```yaml
directive:
  - from: swagger-document
    where: $.definitions.EmailRecipients.properties.bCC
    transform: >
      $["x-ms-client-name"] = "bcc"
```
