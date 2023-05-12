# Azure Communication Identity for Python

> see https://aka.ms/autorest

### Setup
```ps
npm install -g autorest
```

### Generation
```ps
cd <swagger-folder>
autorest ./SWAGGER.md
```

### Settings
``` yaml
tag: package-2022-10
require:
    -  https://raw.githubusercontent.com/Azure/azure-rest-api-specs/a8c4340400f1ab1ae6a43b10e8d635ecb9c49a2a/specification/communication/data-plane/Identity/readme.md
output-folder: ../azure/communication/identity/_generated/
namespace: azure.communication.identity
title: Communication Identity Client
license-header: MICROSOFT_MIT_NO_VERSION
payload-flattening-threshold: 3
no-namespace-folders: true
clear-output-folder: true
v3: true
python: true
models-mode: msrest
```

### Rename CommunicationIdentityTokenScope to CommunicationTokenScope
```yaml
directive:
  - from: swagger-document
    where: $.definitions.CommunicationIdentityTokenScope
    transform: >
      $["x-ms-enum"].name = "CommunicationTokenScope";
```      

###### Regenerating the service layer with a new version of the autorest(DPG), introduced a breaking change by changing the format of property "expires_on" from string to datetime. In order to avoid this breaking change, we added this directive to remove the format datetime from the expires_on property.
### Removes the "format": "date-time" from property expiresOn
```yaml
directive:
  - from: swagger-document
    where: $["definitions"]
    transform: >
      delete $["CommunicationIdentityAccessToken"]["properties"]["expiresOn"]["format"];
```