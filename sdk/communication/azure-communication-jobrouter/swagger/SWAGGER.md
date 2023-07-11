# Azure Communication Configuration for Python

> see https://aka.ms/autorest

### Setup
```ps
npm install -g autorest
```

### Generation
```ps
cd <swagger-folder>
autorest SWAGGER.md
```

### Settings

``` yaml
tag: package-jobrouter-2022-07-18-preview
require: https://raw.githubusercontent.com/williamzhao87/azure-rest-api-specs/c6b35542072b325bfc07c32f5fc05fb5da6891bd/specification/communication/data-plane/JobRouter/readme.md
output-folder: ../azure/communication/jobrouter/_generated
namespace: azure.communication.jobrouter
package-name: azure-communication-jobrouter
license-header: MICROSOFT_MIT_NO_VERSION
enable-xml: true
clear-output-folder: true
no-namespace-folders: true
python: true
v3: true
no-async: false
add-credential: false
title: Azure Communication Job Router Service
```
