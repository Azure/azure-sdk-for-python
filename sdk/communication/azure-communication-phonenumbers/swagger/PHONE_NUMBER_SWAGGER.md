# Azure Communication Phone Numbers for Python

> see https://aka.ms/autorest

### Generation
```ps
cd <swagger-folder>
autorest ./PHONE_NUMBER_SWAGGER.md
```

### Settings
``` yaml
tag: package-preview-2024-01
require: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/a443d2d3c562d91419d11bed6326b5907d38848c/specification/communication/data-plane/PhoneNumbers/readme.md
output-folder: ../azure/communication/phonenumbers/_generated
namespace: azure.communication.phonenumbers
license-header: MICROSOFT_MIT_NO_VERSION
payload-flattening-threshold: 3
no-namespace-folders: true
clear-output-folder: true
v3: true
python: true
title: Phone Numbers Client
models-mode: msrest
```