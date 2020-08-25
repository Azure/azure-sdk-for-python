# Azure Schema Registry for Python

> see https://aka.ms/autorest

### Generation
```ps
cd C:\Work\SchemaRegistry\
autorest --v3 --python --use=@autorest/python@5.0.0-preview.6
```
### Settings
``` yaml
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/arerlend.sr.init/specification/schemaregistry/data-plane/Microsoft.EventHub/preview/2018-01-01-preview/schemaregistry.json
output-folder: ../azure/schemaregistry/_generated
namespace: azure.schemaregistry._generated
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
python: true
package-version: "1.0.0b1"
```
