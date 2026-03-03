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
package-version: 1.1.0
tag: package-2025-09-01
require: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/83327afe471d7a2eb923de58b163658d45e0e5a7/specification/communication/data-plane/Email/readme.md
output-folder: ../azure/communication/email
namespace: azure.communication.email
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
enable-xml: true
clear-output-folder: false
python: true
v3: true
no-async: false
add-credential: false
security: Anonymous
title: Email Client
use-extension:
  "@autorest/python": "6.40.0"
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

### Flatten operations by removing operation group prefixes

```yaml
directive:
  - from: swagger-document
    where: $.paths.*.*
    transform: >
      if ($["operationId"] && $["operationId"].startsWith("Email_")) {
        $["operationId"] = $["operationId"].replace("Email_", "");
      }
  - remove-operation: GetSendResult
```
