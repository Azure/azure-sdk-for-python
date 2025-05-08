# Azure Communication Configuration for Python

> see https://aka.ms/autorest

### Setup
```ps
npm install -g autorest
```

### Generation
```ps
cd <swagger-folder>
autorest ./SIP_ROUTING_SWAGGER.md
```

### Settings
``` yaml
require: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/9191854514911a10bfd71636fd2903e6be2d7edf/specification/communication/data-plane/SipRouting/readme.md
tag: package-2024-11-15-preview
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

### Directive renaming "TrunkRoute" model to "SipTrunkRouteInternal"
``` yaml
directive:
  from: swagger-document
  where: "$.definitions.TrunkRoute"
  transform: >
    $["x-ms-client-name"] = "SipTrunkRouteInternal";
```

### Directive renaming "Domain" model to "SipDomainInternal"
``` yaml
directive:
  from: swagger-document
  where: "$.definitions.Domain"
  transform: >
    $["x-ms-client-name"] = "SipDomainInternal";
```

### Directive renaming "Health" model to "TrunkHealth"
``` yaml
directive:
  from: swagger-document
  where: "$.definitions.Health"
  transform: >
    $["x-ms-client-name"] = "TrunkHealth";
```

### Directive renaming "Tls" model to "TlsHealth"
``` yaml
directive:
  from: swagger-document
  where: "$.definitions.Tls"
  transform: >
    $["x-ms-client-name"] = "TlsHealth";
```

### Directive renaming "Ping" model to "PingHealth"
``` yaml
directive:
  from: swagger-document
  where: "$.definitions.Ping"
  transform: >
    $["x-ms-client-name"] = "PingHealth";
```

### Directive renaming "InactiveStatusReason" enum to "HealthStatusReason"
``` yaml
directive:
  from: swagger-document
  where: "$.definitions.OverallHealth"
  transform: >
    $.properties.reason["x-ms-enum"].name = "HealthStatusReason";
```
