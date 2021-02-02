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
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/5b19c6e69cd2bb9dbe4e5c1237b2c5a175d90ca5/specification/communication/data-plane/Microsoft.CommunicationServicesIdentity/stable/2021-03-07/CommunicationIdentity.json
output-folder: ../azure/communication/identity/_generated/
namespace: azure.communication.identity
license-header: MICROSOFT_MIT_NO_VERSION
payload-flattening-threshold: 3
no-namespace-folders: true
clear-output-folder: true
v3: true
python: true
```

### Rename CommunicationIdentityTokenScope to CommunicationTokenScope
```yaml
directive:
  - from: swagger-document
    where: $.definitions.CommunicationIdentityTokenScope
    transform: >
      $["x-ms-enum"].name = "CommunicationTokenScope";