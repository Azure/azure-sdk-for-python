# Azure Schema Registry for Python

> see https://aka.ms/autorest

### Generation
```ps
cd C:\Work\SchemaRegistry\
autorest --reset
autorest --use=D:\Projects\autorest.python --low-level-client --modelerfour.lenient-model-deduplication
```
### Settings
``` yaml
input-file: https://raw.githubusercontent.com/deyaaeldeen/azure-rest-api-specs/schemaregistry/sdk-swagger-edits/specification/schemaregistry/data-plane/Microsoft.EventHub/preview/2021-11-01-preview/schemaregistry.json
output-folder: ../azure/schemaregistry/_generated
namespace: azure.schemaregistry._generated
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
python: true
add-credential: true
credential-scopes: "https://eventhubs.azure.net/.default"
package-version: "1.0.0b4"
```
