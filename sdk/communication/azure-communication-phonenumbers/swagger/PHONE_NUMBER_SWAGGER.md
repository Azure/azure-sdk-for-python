# Azure Communication Phone Numbers for Python

> see https://aka.ms/autorest

### Generation
```ps
cd <swagger-folder>
autorest ./PHONE_NUMBER_SWAGGER.md
```

### Settings
``` yaml
tag: package-phonenumber-2024-03-01-preview
require: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/44a81f85be1e4797fbf5e290fc6b41d48788a6ba/specification/communication/data-plane/PhoneNumbers/readme.md
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

# Removed Models
``` yaml
directive:
  - remove-operation-match: /.*Reservation.*/i
  - remove-operation: PhoneNumbers_BrowseAvailableNumbers
  - remove-model: PhoneNumbersReservation
  - remove-model: PhoneNumbersReservations
  - remove-model: PhoneNumbersBrowseRequest
  - remove-model: PhoneNumbersBrowseResult
  - remove-model: PhoneNumberBrowseCapabilitiesRequest
  - remove-model: PhoneNumbersReservationPurchaseRequest
  - remove-model: AvailablePhoneNumber
  - remove-model: AvailablePhoneNumberCost
```