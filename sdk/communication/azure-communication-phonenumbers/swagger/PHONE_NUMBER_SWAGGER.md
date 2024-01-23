# Azure Communication Phone Numbers for Python

> see https://aka.ms/autorest

### Generation
```ps
cd <swagger-folder>
autorest ./PHONE_NUMBER_SWAGGER.md
```

### Settings
``` yaml
tag: package-phonenumber-2024-03-01
require: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/e91cb6ec619e2a4744f59c5391e906cfe608e569/specification/communication/data-plane/PhoneNumbers/readme.md
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

``` yaml
directive:
  from: swagger-document
  where: $.definitions.PhoneNumberSearchResult.properties.error.x-ms-enum
  transform: >
    $["name"] = "PhoneNumberSearchResultError";
```

``` yaml
directive:
  from: swagger-document
  where: $.parameters.Endpoint
  transform: >
    $["format"] = "";
```