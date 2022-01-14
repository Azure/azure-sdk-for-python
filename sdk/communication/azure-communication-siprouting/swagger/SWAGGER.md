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
require: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/15d66311cc2b64f04692fdf021d1b235b538e1bc/specification/communication/data-plane/SipRouting/readme.md
tag: package-2021-05-01-preview
output-folder: ../azure/communication/siprouting/_generated
namespace: azure.communication.siprouting
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
enable-xml: true
clear-output-folder: true
python: true
v3: true
no-async: false
add-credential: false
title: Azure Communication SIP Routing Service
disable-async-iterators: true
model-namespace: false
```

``` yaml
directive:
  from: swagger-document
  where: $.paths.*[?(@.operationId == "PatchSipConfiguration")].parameters..[?(@.description == "Configuration patch.")]
  transform: >
    $.schema = {"$ref": "#/definitions/SipConfiguration"}
```

``` yaml
directive:
  from: swagger-document
  where: $.definitions
  transform: >
    delete $.TrunkPatch
```

``` yaml
directive:
  from: swagger-document
  where: $.definitions
  transform: >
    delete $.SipConfigurationPatch
```

``` yaml
directive:
  from: swagger-document
  where: $.definitions.Trunk
  transform: >
    delete $.required;
```