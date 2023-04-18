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

```yaml
tag: package-2023-01-15-preview
require: https://raw.githubusercontent.com/williamzhao87/azure-rest-api-specs/058df5df47d9c9410cbde774ed1c525ffa6326de/specification/communication/data-plane/CallAutomation/readme.md
output-folder: ../azure/communication/callautomation/_generated
models-mode: msrest
namespace: azure.communication.callautomation
package-name: azure-communication-callautomation
license-header: MICROSOFT_MIT_NO_VERSION
enable-xml: true
clear-output-folder: true
no-namespace-folders: true
python: true
v3: true
no-async: false
add-credential: false
title: Azure Communication Call Automation Service
```
