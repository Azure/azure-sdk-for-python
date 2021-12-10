# Azure ServiceBus for Python

> see https://aka.ms/autorest

### Generation
```ps
cd C:\Work\ServiceBus\
autorest --v3 --python --use=@autorest/python@5.0.0-preview.6
```
### Settings
``` yaml
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/sb_dataplane_namespace/specification/servicebus/data-plane/servicebus-swagger.json
output-folder: ../azure/servicebus/management/_generated
namespace: azure.servicebus.management._generated
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
python: true
package-version: "2021-05"
```
