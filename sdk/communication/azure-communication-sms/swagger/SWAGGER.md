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
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/8818a603b78a1355ba1647ab9cd4e3354cdc4b69/specification/communication/data-plane/Microsoft.CommunicationServicesSms/preview/2020-07-20-preview1/communicationservicessms.json
output-folder: ../azure/communication/sms/_generated
namespace: azure.communication.sms
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
enable-xml: true
clear-output-folder: true
python: true
v3: true
no-async: false
add-credential: false
```