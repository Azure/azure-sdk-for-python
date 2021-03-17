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
tag: package-sms-2021-03-07
require: https://github.com/Azure/azure-rest-api-specs/blob/e5a57e87f16c7fd9a6eaeb3c6049293d1334f6c6/specification/communication/data-plane/Microsoft.CommunicationServicesSms/readme.md
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