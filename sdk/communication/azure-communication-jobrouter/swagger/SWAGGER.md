# Azure Communication Configuration for Python

> see https://aka.ms/autorest

### Setup
```ps
npm install -g autorest
```

### Generation
```ps
cd <swagger-folder>
autorest SWAGGER.md
```

### Settings
``` yaml
input-file: ./swagger.json
output-folder: ../azure/communication/jobrouter/_generated
namespace: azure.communication.jobrouter
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
enable-xml: true
clear-output-folder: true
python: true
v3: true
no-async: false
add-credential: false
title: Azure Communication Job Router Service
disable-async-iterators: true
```

### Set reference to LabelSelectorAttachment and ExceptionAction
```yaml
directive:
  - from: swagger-document
    where: "$.definitions"
    transform: >
      $.UpsertClassificationPolicyRequest.properties.workerSelectors.items["$ref"] = "#/definitions/LabelSelectorAttachment";

      $.UpsertClassificationPolicyResponse.properties.workerSelectors.items["$ref"] = "#/definitions/LabelSelectorAttachment";

      $.ClassificationPolicy.properties.workerSelectors.items["$ref"] = "#/definitions/LabelSelectorAttachment";;

      $.ExceptionRule.properties.actions.items["$ref"] = "#/definitions/ExceptionAction";
            
      $.QueueLabelSelector.properties.labelSelectors.items["$ref"] = "#/definitions/LabelSelectorAttachment";
```

### Rename CommunicationError to JobRouterError
```yaml
directive:
  from: swagger-document
  where: '$.definitions.CommunicationError'
  transform: >
    $["x-ms-client-name"] = "JobRouterError";
```