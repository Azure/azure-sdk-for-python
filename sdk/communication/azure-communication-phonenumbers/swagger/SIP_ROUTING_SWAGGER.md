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
require: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/communication/data-plane/SipRouting/readme.md
tag: package-2023-03
output-folder: ../azure/communication/phonenumbers/siprouting/_generated
namespace: azure.communication.phonenumbers.siprouting
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
python: true
v3: true
title: SIP Routing Service
model-namespace: false
models-mode: msrest
```

### Remove the -Update types and use simple types instead, to simplify user interface
``` yaml
directive:
  from: swagger-document
  where: $.paths.*[?(@.operationId == "SipRouting_Update")].parameters..[?(@.description == "Sip configuration update object.")]
  transform: >
    $.schema = {"$ref": "#/definitions/SipConfiguration"}
```

``` yaml
directive:
  from: swagger-document
  where: $.definitions
  transform: >
    delete $.TrunkUpdate
```

``` yaml
directive:
  from: swagger-document
  where: $.definitions
  transform: >
    delete $.SipConfigurationUpdate
```

### Directive renaming "Trunk" model to "SipTrunkInternal"
``` yaml
directive:
  from: swagger-document
  where: "$.definitions.Trunk"
  transform: >
    $["x-ms-client-name"] = "SipTrunkInternal";
```

### Directive renaming "TrunkRoute" model to "SipTrunkRoute"
``` yaml
directive:
  from: swagger-document
  where: "$.definitions.TrunkRoute"
  transform: >
    $["x-ms-client-name"] = "SipTrunkRoute";
```
