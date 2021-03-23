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
input-file: https://int.chatgateway.trafficmanager.net/swagger/2021-03-07/swagger.json
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
```

### Rename CommunicationError to ChatError
```yaml
directive:
    from: swagger-document
    where: '$.definitions.CommunicationError'
    transform: >
        $["x-ms-client-name"] = "ChatError";
```