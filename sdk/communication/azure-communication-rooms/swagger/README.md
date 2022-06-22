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
require:
    - https://raw.githubusercontent.com/Azure/azure-rest-api-specs/ea1a21b30050e1a4b992dcb9d33db1245fa30b89/specification/communication/data-plane/Rooms/readme.md
output-folder: ../azure/communication/rooms/_generated
models-mode: msrest
namespace: azure.communication.rooms
package-name: azure-communication-rooms
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
no-namespace-folders: true
python: true
title: Azure Communication Rooms Service
add-credential: false
v3: true
no-async: false
```
