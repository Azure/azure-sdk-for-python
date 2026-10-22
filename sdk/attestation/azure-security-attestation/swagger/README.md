# Azure Attestation Service client library for Python

## Setup

```ps
npm install -g autorest
```

## Generation

```ps
cd <swagger-folder>
autorest SWAGGER.md
```

### Code generation settings

```yaml
title: AzureAttestationRestClient
require: 
  - https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/specification/attestation/data-plane/readme.md
output-folder: ../azure/security/attestation/_generated
namespace: azure.security.attestation._generated
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
tag: package-2020-10-01
package-version: 1.0.0b2
enable-xml: false
clear-output-folder: true
python: true
v3: true
add-credentials: true
azure-arm: false
payload-flattening-threshold: 2
package-name: azure-security-attestation
credential-scopes: 'https://attest.azure.net/.default'
```

```yaml
directive:
  from: swagger-document
  where: "$.x-ms-parameterized-host.parameters"
  transform: >
    $.name = "endpoint"
```

```yaml
directive:
  where: "$.x-ms-parameterized-host"
  transform: >
    $.hostTemplate = "endpoint"
```
