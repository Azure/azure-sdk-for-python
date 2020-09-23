# Azure Communication Administration for Python

> see https://aka.ms/autorest

### Setup
```ps
npm install -g autorest
```

### Generation
```ps
cd <swagger-folder>
autorest ./COMMUNICATION_IDENTITY.md
```

### Settings
``` yaml
input-file: ./CommunicationIdentity.json
output-folder: ../azure/communication/administration/_identity/_generated/
namespace: azure.communication.administration
license-header: MICROSOFT_MIT_NO_VERSION
payload-flattening-threshold: 3
no-namespace-folders: true
clear-output-folder: true
v3: true
python: true
```