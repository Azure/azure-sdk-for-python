# Azure Mixed Reality Authentication Service client library for Python

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
input-file: 
  - https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/specification/attestation/data-plane/Microsoft.Attestation/stable/2020-10-01/attestation.json
output-folder: azure/security/attestation/_generated
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
package-name: azure-attestation
credential-scopes: 'https://attest.azure.net/.default'

```
