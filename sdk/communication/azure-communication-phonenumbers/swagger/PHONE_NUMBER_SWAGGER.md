# Azure Communication Phone Numbers Administration for Python

> see https://aka.ms/autorest

### Generation
```ps
cd <swagger-folder>
autorest ./PHONE_NUMBER_SWAGGER.md
```

### Settings
``` yaml
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/1ef769ae890b5f5a952f9ba6e46e0ef6d38241da/specification/communication/data-plane/Microsoft.CommunicationServicesPhoneNumbers/stable/2021-03-07/phonenumbers.json
output-folder: ../azure/communication/phonenumbers/_generated
namespace: azure.communication.phonenumbers
license-header: MICROSOFT_MIT_NO_VERSION
payload-flattening-threshold: 3
no-namespace-folders: true
clear-output-folder: true
v3: true
python: true
```
