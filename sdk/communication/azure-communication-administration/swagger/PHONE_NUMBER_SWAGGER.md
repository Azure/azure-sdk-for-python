# Azure Communication Phone Number Administration for Python

> see https://aka.ms/autorest

### Generation
```ps
cd <swagger-folder>
autorest ./PHONE_NUMBER_SWAGGER.md
```

### Settings
``` yaml
input-file: https://raw.githubusercontent.com/DominikMe/azure-rest-api-specs/3e42c16fc1fbfaaa5b236c88371bfb53dd34175d/specification/communication/data-plane/Microsoft.CommunicationServicesAdministration/preview/2020-11-01-preview3/phonenumbers.json
output-folder: ../azure/communication/administration/_phonenumber/_generated
namespace: azure.communication.administration
license-header: MICROSOFT_MIT_NO_VERSION
payload-flattening-threshold: 3
no-namespace-folders: true
clear-output-folder: true
v3: true
python: true
```

### Rename searchId to reservationId
```yaml
directive:
  - from: swagger-document
    where: $.definitions.PhoneNumberSearch.properties.searchId
    transform: >
      $["x-ms-client-name"] = "reservationId";
```

### Rename PhoneNumberSearch to PhoneNumberReservation
```yaml
custom-types-subpackage: models
custom-types: PhoneNumberReservation
required-fields-as-ctor-args: true
directive:
  - rename-model:
      from: PhoneNumberSearch
      to: PhoneNumberReservation
```