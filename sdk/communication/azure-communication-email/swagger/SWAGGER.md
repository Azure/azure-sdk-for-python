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
package-version: 1.0.0
tag: package-2024-07-01-preview
require: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/e64ad693df24b47d4009eece6663c8d95cf94be6/specification/communication/data-plane/Email/readme.md
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

### Ensure contentInBase64 is a string

```yaml
directive:
  - from: swagger-document
    where: $.definitions.EmailAttachment.properties.contentInBase64
    transform: >
      $["type"] = "string";
      if ($["format"]) {
        delete $["format"];
      }
```
