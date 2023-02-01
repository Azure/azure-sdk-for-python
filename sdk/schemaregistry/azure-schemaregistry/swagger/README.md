# Azure Schema Registry for Python

> see https://aka.ms/autorest

### Generation
```ps
cd C:\Work\SchemaRegistry\
autorest --reset
autorest --low-level-client --modelerfour.lenient-model-deduplication --show-operations --trace=false README.md
```
### Settings
``` yaml
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/schemaregistry/data-plane/Microsoft.EventHub/stable/2022-10/schemaregistry.json
output-folder: ../azure/schemaregistry/_generated
namespace: azure.schemaregistry._generated
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
python: true
add-credential: true
credential-scopes: "https://eventhubs.azure.net/.default"
package-version: "1.3.0b1"
```
