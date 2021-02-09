# Azure Remote Rendering Service client library for Python

## Setup

```ps
npm install -g autorest
```

## Generation

```ps
cd <swagger-folder>
autorest AUTOREST.md
```

### Code generation settings

```yaml
title: RemoteRenderingRestClient
input-file: https://raw.githubusercontent.com/rikogeln/azure-rest-api-specs/c90870a194ab90b29760ab06ea7d18c4573a7d93/specification/mixedreality/data-plane/Microsoft.MixedReality/stable/2021-01-01/mr-arr.json
output-folder: ../azure/mixedreality/remoterendering/_generated
namespace: azure.mixedreality.remoterendering._generated
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
enable-xml: false
clear-output-folder: true
vanilla: true
python: true
v3: true
no-async: false
```

### Directive renaming conversion "creationTime" property to "createdOn"

``` yaml
directive:
    from: swagger-document
    where: '$.definitions.conversion.properties.creationTime'
    transform: >
        $["x-ms-client-name"] = "createdOn";
```

### Directive renaming conversion to asset_conversion

``` yaml
directive:
    from: swagger-document
    where: '$.definitions.conversion'
    transform: >
        $["x-ms-client-name"] = "asset_conversion";
```

### Directive renaming create_conversion_settings to create_asset_conversion_settings

``` yaml
directive:
    from: swagger-document
    where: '$.definitions.create_conversion_settings'
    transform: >
        $["x-ms-client-name"] = "create_asset_conversion_settings";
```

### Directive renaming conversion output outputAssetUri property to assetUri

``` yaml
directive:
    from: swagger-document
    where: '$.definitions.conversion.properties.output.properties.outputAssetUri'
    transform: >
        $["x-ms-client-name"] = "assetUri";
```

### Directive renaming conversion_input_settings to asset_conversion_input_settings

``` yaml
directive:
    from: swagger-document
    where: '$.definitions.conversion_input_settings'
    transform: >
        $["x-ms-client-name"] = "asset_conversion_input_settings";
```

### Directive renaming conversion_output to asset_conversion_output

``` yaml
directive:
  - from: swagger-document
    where: $.definitions
    transform: >
      $["AssetConversionOutput"] = $.conversion.properties.output;
      $.conversion.properties["output"] = {"$ref": "#/definitions/AssetConversionOutput"};
```

### Directive renaming conversion_output_settings to asset_conversion_output_settings

``` yaml
directive:
    from: swagger-document
    where: '$.definitions.conversion_output_settings'
    transform: >
        $["x-ms-client-name"] = "asset_conversion_output_settings";
```

### Directive renaming conversion_settings to asset_conversion_settings

``` yaml
directive:
    from: swagger-document
    where: '$.definitions.conversion_settings'
    transform: >
        $["x-ms-client-name"] = "asset_conversion_settings";
```

### Directive renaming conversion_status to asset_conversion_status

``` yaml
directive:
    from: swagger-document
    where: '$.definitions.conversion_status'
    transform: >
        $["x-ms-enum"].name = "asset_conversion_status";
```

### Directive renaming session creationTime property to createdOn

``` yaml
directive:
    from: swagger-document
    where: '$.definitions.session_properties.properties.creationTime'
    transform: >
        $["x-ms-client-name"] = "createdOn";
```

### Directive renaming session maxLeaseTimeMinutes property to leaseTimeMinutes

``` yaml
directive:
    from: swagger-document
    where: '$.definitions.session_properties.properties.maxLeaseTimeMinutes'
    transform: >
        $["x-ms-client-name"] = "leaseTimeMinutes";
```

### Directive renaming create_session_settings maxLeaseTimeMinutes property to leaseTimeMinutes

``` yaml
directive:
    from: swagger-document
    where: '$.definitions.create_session_settings.properties.maxLeaseTimeMinutes'
    transform: >
        $["x-ms-client-name"] = "leaseTimeMinutes";
```

### Directive renaming update_session_settings maxLeaseTimeMinutes property to leaseTimeMinutes

``` yaml
directive:
    from: swagger-document
    where: '$.definitions.update_session_settings.properties.maxLeaseTimeMinutes'
    transform: >
        $["x-ms-client-name"] = "leaseTimeMinutes";
```


### Directive renaming conversion settings inputLocation property to inputSettings

``` yaml
directive:
    from: swagger-document
    where: '$.definitions.conversion_settings.properties.inputLocation'
    transform: >
        $["x-ms-client-name"] = "inputSettings";
```

### Directive renaming conversion settings outputLocation property to outputSettings

``` yaml
directive:
    from: swagger-document
    where: '$.definitions.conversion_settings.properties.outputLocation'
    transform: >
        $["x-ms-client-name"] = "outputSettings";
```

### Directive renaming session_properties to rendering_session

``` yaml
directive:
    from: swagger-document
    where: '$.definitions.session_properties'
    transform: >
        $["x-ms-client-name"] = "rendering_session";
```

### Directive renaming create_session_settings to create_rendering_session_settings

``` yaml
directive:
    from: swagger-document
    where: '$.definitions.create_session_settings'
    transform: >
        $["x-ms-client-name"] = "create_rendering_session_settings";
```

### Directive renaming session_status to rendering_session_status

``` yaml
directive:
    from: swagger-document
    where: '$.definitions.session_status'
    transform: >
        $["x-ms-enum"].name = "rendering_session_status";
```

### Directive renaming session_size to rendering_session_size

``` yaml
directive:
    from: swagger-document
    where: '$.definitions.session_size'
    transform: >
        $["x-ms-enum"].name = "rendering_session_size";
```

### Directive renaming error to remote_rendering_error

``` yaml
directive:
    from: swagger-document
    where: '$.definitions.error'
    transform: >
        $["x-ms-client-name"] = "remote_rendering_error";
```
