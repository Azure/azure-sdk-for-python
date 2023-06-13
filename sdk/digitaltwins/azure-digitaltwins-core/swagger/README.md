# Azure Digitaltwins for Python

> see https://aka.ms/autorest

### Settings
``` yaml
input-file: https://github.com/Azure/azure-rest-api-specs/blob/2c0f2c7d585b99af7428435aa065d5ea4276119a/specification/digitaltwins/data-plane/Microsoft.DigitalTwins/stable/2023-06-30/digitaltwins.json
output-folder: ../azure/digitaltwins/core/_generated
use-extension: 
  "@autorest/python": "5.16.0"
namespace: azure.digitaltwins.core
no-namespace-folders: true
add-credentials: true
credential-scopes: "https://digitaltwins.azure.net/.default"
license-header: MICROSOFT_MIT_NO_VERSION
enable-xml: true
vanilla: true
combine-operation-files: false
clear-output-folder: true
models-mode: msrest
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

