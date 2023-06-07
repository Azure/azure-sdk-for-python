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
require: https://raw.githubusercontent.com/williamzhao87/azure-rest-api-specs/9d0184f60868f175aa515e34cffdc3bd6235768f/specification/communication/data-plane/JobRouter/readme.md
output-folder: ../azure/communication/jobrouter/_generated
models-mode: msrest
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
