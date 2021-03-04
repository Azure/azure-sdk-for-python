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
title: MixedRealityStsRestClient
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/aa19725fe79aea2a9dc580f3c66f77f89cc34563/specification/mixedreality/data-plane/Microsoft.MixedReality/preview/2019-02-28-preview/mr-sts.json
output-folder: ../azure/mixedreality/authentication/_generated
namespace: azure.mixedreality.authentication._generated
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
enable-xml: false
clear-output-folder: true
python: true
v3: true
add-credentials: false
```
