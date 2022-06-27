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
output-folder: ../azure/communication/phonenumbers/siprouting/_generated
namespace: azure.communication.phonenumbers.siprouting
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
python: true
v3: true
title: SIP Routing Service
model-namespace: false
```

### Remove the -Patch types and use simple types instead, to simplify user interface
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

### Remove additional responses from Swagger, because they should be treated as errors and throw exception
``` yaml
directive:
  from: swagger-document
  where: $.paths.*[?(@.operationId == "PatchSipConfiguration")]
  transform: >
    delete $.responses["422"]
```

``` yaml
directive:
  from: swagger-document
  where: $.paths.*[?(@.operationId == "PatchSipConfiguration")]
  transform: >
    delete $.responses["415"]
```

``` yaml
directive:
  from: swagger-document
  where: $.paths.*[?(@.operationId == "PatchSipConfiguration")]
  transform: >
    delete $.responses["500"]
```