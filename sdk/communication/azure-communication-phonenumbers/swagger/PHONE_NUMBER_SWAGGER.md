# Azure Communication Phone Numbers for Python

> see https://aka.ms/autorest

### Generation
```ps
cd <swagger-folder>
autorest ./PHONE_NUMBER_SWAGGER.md
```

### Settings
``` yaml
tag: package-phonenumber-2023-10-01-preview
require: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/bd44f2d98fdc14c674b542cc64ce7df33ddfaf76/specification/communication/data-plane/PhoneNumbers/readme.md
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

### Removed Property error from PhoneNumberSearchResult
``` yaml
directive:
  where-model: PhoneNumberSearchResult
  remove-property: error
```

### Removed Property errorCode from PhoneNumberSearchResult
``` yaml
directive:
  where-model: PhoneNumberSearchResult
  remove-property: errorCode
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
  - remove-model: Error
```