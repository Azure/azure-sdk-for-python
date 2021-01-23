# Azure Mixed Reality Authentication Service client library for Python

## Setup

```ps
npm install -g autorest
```

## Generation

```ps
cd <swagger-folder>
autorest README.md
```

### Code generation settings

```yaml
title: MixedRealityStsRestClient
input-file: https://raw.githubusercontent.com/craigktreasure/azure-rest-api-specs/6938d23da2be2a20b9998e002ef8b79e8d83e509/specification/mixedreality/data-plane/Microsoft.MixedReality/preview/2019-02-28-preview/mr-sts.json
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
