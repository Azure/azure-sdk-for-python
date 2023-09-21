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

```yaml $(python)
python:
  azure-arm: true
  license-header: MICROSOFT_MIT_NO_VERSION
  payload-flattening-threshold: 2
  clear-output-folder: true
```

```yaml
title: Azure Communication Rooms Service
require:
    - https://raw.githubusercontent.com/Azure/azure-rest-api-specs/c01954913cf229486cb3091072e807c277ebc322/specification/communication/data-plane/Rooms/readme.md
output-folder: ../azure/communication/rooms/_generated
namespace: azure.communication.rooms
package-name: azure-communication-rooms
no-namespace-folders: true
python: true
add-credential: false
v3: true
no-async: false
security: Anonymous
```

### Rename Role to ParticipantRole
```yaml
directive:
  from: swagger-document
  where: $.definitions.Role
  transform: >
    $["x-ms-enum"].name = "ParticipantRole";
```

### Rename RoomModel to CommunicationRoom
```yaml
directive:
  from: swagger-document
  where: $.definitions.RoomModel
  transform: >
    $["x-ms-client-name"] = "CommunicationRoom";
```