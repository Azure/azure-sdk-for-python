# Azure Communication Phone Numbers for Python

> see https://aka.ms/autorest

### Generation
```ps
cd <swagger-folder>
autorest ./PHONE_NUMBER_SWAGGER.md
```

### Settings
``` yaml
tag: package-phonenumber-2025-04-01
require: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/de9cb12d2840ca0915849ce6a3bf8c956a32c022/specification/communication/data-plane/PhoneNumbers/readme.md
input-file: 
  - https://raw.githubusercontent.com/Azure/azure-rest-api-specs/refs/heads/main/specification/common-types/data-plane/v1/types.json
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

### Set remove-empty-child-schemas
```yaml
modelerfour:
    remove-empty-child-schemas: true
```

### Rename AvailablePhoneNumberStatus to PhoneNumberAvailabilityStatus
```yaml
directive:
  from: swagger-document
  where: $.definitions.AvailablePhoneNumber.properties.status.x-ms-enum
  transform: >
    $["name"] = "PhoneNumberAvailabilityStatus";
```

### Replace type from AvailablePhoneNumberError to ResponseError
```yaml
directive:
  - from: swagger-document
    where: $.definitions.AvailablePhoneNumber.properties.error
    transform: >
      $.type = "object";
      $.$ref = "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/refs/heads/main/specification/common-types/data-plane/v1/types.json#/definitions/ErrorDetail";
```