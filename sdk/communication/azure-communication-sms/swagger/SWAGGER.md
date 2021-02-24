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
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/83d782b99cb85a9b2f5ef22774584541dd0ff997/specification/communication/data-plane/Microsoft.CommunicationServicesSms/stable/2021-03-07/communicationservicessms.json
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