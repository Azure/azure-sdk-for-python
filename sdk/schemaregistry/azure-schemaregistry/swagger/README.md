# Azure Schema Registry for Python

> see https://aka.ms/autorest

### Generation
```ps
cd C:\Work\SchemaRegistry\
autorest --reset
autorest README.md
```
### Settings
``` yaml
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/schemaregistry/data-plane/Microsoft.EventHub/stable/2023-07-01/schemaregistry.json
output-folder: ../azure/schemaregistry/_generated
namespace: azure.schemaregistry._generated
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
python: true
add-credential: true
credential-scopes: "https://eventhubs.azure.net/.default"
package-version: "1.3.0b3"
trace: false
```

### Delete list operations

```yaml
directive:
  - from: swagger-document
    where: $["paths"]
    transform: >
      delete $["/$schemaGroups"]["get"];
      delete $["/$schemaGroups/{groupName}/schemas/{schemaName}/versions"]["get"];

  - from: swagger-document
    where: $["definitions"]
    transform: >
      delete $["SchemaGroups"];
      delete $["SchemaVersions"];
```
