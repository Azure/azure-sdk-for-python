# Azure Communication Phone Numbers for Python

> see https://aka.ms/autorest

### Generation
```ps
cd <swagger-folder>
autorest ./PHONE_NUMBER_SWAGGER.md
```

### Settings
``` yaml
tag: package-phonenumber-2021-03-07
require: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/bf081421869ccd31d9fd87084b07a1e246aee310/specification/communication/data-plane/Microsoft.CommunicationServicesPhoneNumbers/readme.md
output-folder: ../azure/communication/phonenumbers/_generated
namespace: azure.communication.phonenumbers
license-header: MICROSOFT_MIT_NO_VERSION
payload-flattening-threshold: 3
no-namespace-folders: true
clear-output-folder: true
v3: true
python: true
title: Phone Numbers Client
```
