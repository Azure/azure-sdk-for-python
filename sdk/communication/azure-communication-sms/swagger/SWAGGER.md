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

### Rename SmsSendResponseItem to SmsSendResult
``` yaml
directive:
    - rename-model:
        from: SmsSendResponseItem
        to: SmsSendResult
```

### Settings
``` yaml
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/dc652c9308ddcb19a73dbbb37498e63081dfde6e/specification/communication/data-plane/Microsoft.CommunicationServicesSms/stable/2021-03-07/communicationservicessms.json
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