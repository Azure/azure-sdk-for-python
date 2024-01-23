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
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/servicebus/data-plane/Microsoft.ServiceBus/stable/2021-05/servicebus.json
output-folder: ../azure/servicebus/management/_generated
namespace: azure.servicebus.management._generated
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
python: true
models-mode: msrest
```

### Python Customizations
```yaml
directive:
    - from: swagger-document
      where: $.definitions.NamespacePropertiesEntry.properties.title
      transform: >
        $["type"] = "string";
    - from: swagger-document
      where: $.definitions.QueueDescriptionEntry.properties.title
      transform: >
        $["type"] = "string";
    - from: swagger-document
      where: $.definitions.TopicDescriptionEntry.properties.title
      transform: >
        $["type"] = "string";
    - from: swagger-document
      where: $.definitions.SubscriptionDescriptionEntry.properties.title
      transform: >
        $["type"] = "string";
    - from: swagger-document
      where: $.definitions.RuleDescriptionEntry.properties.title
      transform: >
        $["type"] = "string";
```
