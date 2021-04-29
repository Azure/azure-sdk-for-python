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

```yaml
tag: package-chat-2021-03-07
require: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/bf081421869ccd31d9fd87084b07a1e246aee310/specification/communication/data-plane/Microsoft.CommunicationServicesChat/readme.md
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
```

### Rename CommunicationError to ChatError
```yaml
directive:
  from: swagger-document
  where: '$.definitions.CommunicationError'
  transform: >
    $["x-ms-client-name"] = "ChatError";
```