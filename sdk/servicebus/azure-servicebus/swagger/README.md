# Azure ServiceBus for Python

> see https://aka.ms/autorest

### Generation
```ps
cd C:\Work\ServiceBus\
autorest --reset
autorest swagger/README.md
```
### Settings
``` yaml
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/swathipil/sb/add-swagger-back/specification/servicebus/data-plane/Microsoft.ServiceBus/stable/2021-05/servicebus.json
output-folder: ../azure/servicebus/management/_generated
namespace: azure.servicebus.management._generated
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
python: true
models-mode: msrest
```
