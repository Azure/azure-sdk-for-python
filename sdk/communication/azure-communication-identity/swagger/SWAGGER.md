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
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/14bfbf5d0ff8f0dc1358e6e60362e99d0a649ba7/specification/communication/data-plane/Microsoft.CommunicationServicesIdentity/stable/2021-03-07/CommunicationIdentity.json
output-folder: ../azure/communication/identity/_generated/
namespace: azure.communication.identity
license-header: MICROSOFT_MIT_NO_VERSION
payload-flattening-threshold: 3
no-namespace-folders: true
clear-output-folder: true
v3: true
python: true
```

### Rename CommunicationIdentityAccessToken to CommunicationUserToken

``` yaml
directive:
    - rename-model:
        from: CommunicationIdentityAccessToken
        to: CommunicationUserToken
```

### Rename CommunicationIdentityTokenScope to CommunicationTokenScope
```yaml
directive:
  - from: swagger-document
    where: $.definitions.CommunicationIdentityTokenScope
    transform: >
      $["x-ms-enum"].name = "CommunicationTokenScope";