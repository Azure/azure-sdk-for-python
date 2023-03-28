# Azure Communication Configuration for Python

> see https://aka.ms/autorest

### Setup
```ps
npm install -g autorest
```

### Generation
```ps
cd <swagger-folder>
autorest README.md
```

### Settings

```yaml
require:
    - https://raw.githubusercontent.com/Azure/azure-rest-api-specs/49ef4666b13e2e5675dfb92dab3b3d13aa8b3596/specification/communication/data-plane/Rooms/readme.md
output-folder: ../azure/communication/rooms/_generated
payload-flattening-threshold: 3
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

### Rename Role to ParticipantRole
```yaml
directive:
  from: swagger-document
  where: $.definitions.Role
  transform: >
    $["x-ms-enum"].name = "ParticipantRole";
```
