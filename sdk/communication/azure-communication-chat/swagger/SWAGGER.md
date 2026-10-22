# Azure Communication Configuration for Python

> see https://aka.ms/autorest

### Setup
```ps
npm install -g autorest
```

### Generation
```ps
cd <swagger-folder>
autorest SWAGGER.md --version-tolerant=false
```

### Settings

```yaml
tag: package-chat-2024-03-07
require: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/72d4c8cae964a12dc27ad4684b0bddf493225338/specification/communication/data-plane/Chat/readme.md
output-folder: ../azure/communication/chat/_generated
namespace: azure.communication.chat
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
enable-xml: true
clear-output-folder: true
python: true
v3: true
no-async: false
add-credential: false
title: Azure Communication Chat Service
disable-async-iterators: true
security: Anonymous
```

### Rename CommunicationError to ChatError
```yaml
directive:
  from: swagger-document
  where: '$.definitions.CommunicationError'
  transform: >
    $["x-ms-client-name"] = "ChatError";
```
