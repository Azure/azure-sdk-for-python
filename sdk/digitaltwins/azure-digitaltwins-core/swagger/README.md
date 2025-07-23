# Azure Digitaltwins for Python

> see https://aka.ms/autorest

### Settings
``` yaml
input-file: https://github.com/Azure/azure-rest-api-specs/blob/cf0244c2ee8ea158fea446786347bf0263a4d5b3/specification/digitaltwins/data-plane/Microsoft.DigitalTwins/stable/2023-10-31/digitaltwins.json
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

