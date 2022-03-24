# Azure Digitaltwins for Python

> see https://aka.ms/autorest

### Settings
``` yaml
use-extension:
    "@autorest/python": "5.1.0-preview.4"
input-file: https://github.com/Azure/azure-rest-api-specs/blob/main/specification/digitaltwins/data-plane/Microsoft.DigitalTwins/preview/2021-06-30-preview/digitaltwins.json
output-folder: ../azure/digitaltwins/core/_generated
namespace: azure.digitaltwins.core
no-namespace-folders: true
add-credentials: true
credential-scopes: "https://digitaltwins.azure.net/.default"
license-header: MICROSOFT_MIT_NO_VERSION
enable-xml: true
vanilla: true
clear-output-folder: true
python: true
```

### Replace dtTimestamp with timestamp

```yaml
directive:
  - from: swagger-document
    where: $.paths..parameters[*]
    transform: >
      if ($.name === "dt-timestamp") {
        $["x-ms-client-name"] = "timestamp";
      }
```

### Expose If-None_match header

```yaml
directive:
  - from: swagger-document
    where: $..[?(@.name=='If-None-Match')]
    transform: delete $.enum;
```

### Rename EventRoute

```yaml
directive:
  - from: swagger-document
    where: $.definitions.EventRoute
    transform: >
      $["x-ms-client-name"] = "DigitalTwinsEventRoute"
```

### Rename models parameter to dtdl_models

```yaml
directive:
  - from: swagger-document
    where: $.paths["/models"]..parameters[?(@.name === "models")] 
    transform: >
        $["x-ms-client-name"] = "dtdl_models"
```

