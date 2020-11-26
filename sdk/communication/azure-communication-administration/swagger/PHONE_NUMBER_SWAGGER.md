# Azure Communication Phone Number Administration for Python

> see https://aka.ms/autorest

### Generation
```ps
cd <swagger-folder>
autorest ./PHONE_NUMBER_SWAGGER.md
```

### Settings
``` yaml
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/ca264fa5c7c47c556f5e1ea75df04fd2c2e9b89d/specification/communication/data-plane/Microsoft.CommunicationServicesAdministration/preview/2020-11-01-preview3/phonenumbers.json
output-folder: ../azure/communication/administration/_phonenumber/_generated
namespace: azure.communication.administration
license-header: MICROSOFT_MIT_NO_VERSION
payload-flattening-threshold: 3
no-namespace-folders: true
clear-output-folder: true
v3: true
python: true
```