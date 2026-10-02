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

### Add Topic Filter Count Runtime Properties

Adds the read-only `SqlFilterCount` and `CorrelationFilterCount` runtime properties to `TopicDescription`. They report
the total number of SQL / correlation filters across all of a topic's subscriptions and are served by the `2024-05`
service API version. They are not present in the pinned `2021-05` input swagger, so they are injected here (mirroring the
sibling `subscriptionCount`) until the `input-file` is bumped to a spec revision that defines them. The two properties
are inserted immediately after `subscriptionCount` so the generated property and XML element order is retained.

```yaml
directive:
  - from: swagger-document
    where: $.definitions
    transform: >
      const filterCountProperties = {
        "sqlFilterCount": {
          "description": "The total number of SQL filters across all subscriptions of the topic.",
          "type": "integer",
          "format": "int32",
          "xml": {
            "name": "SqlFilterCount",
            "namespace": "http://schemas.microsoft.com/netservices/2010/10/servicebus/connect"
          }
        },
        "correlationFilterCount": {
          "description": "The total number of correlation filters across all subscriptions of the topic.",
          "type": "integer",
          "format": "int32",
          "xml": {
            "name": "CorrelationFilterCount",
            "namespace": "http://schemas.microsoft.com/netservices/2010/10/servicebus/connect"
          }
        }
      };

      const topicProperties = $.TopicDescription.properties;
      const newTopicProperties = {};
      Object.keys(topicProperties).forEach(key => {
        newTopicProperties[key] = topicProperties[key];
        if (key === "subscriptionCount") {
          newTopicProperties["sqlFilterCount"] = filterCountProperties["sqlFilterCount"];
          newTopicProperties["correlationFilterCount"] = filterCountProperties["correlationFilterCount"];
        }
      });
      $.TopicDescription.properties = newTopicProperties;
```
