# Azure Purview for Python

> see https://aka.ms/autorest

### Setup

Install Autorest v3

```ps
npm install -g autorest
```

### Generation

```ps
cd <swagger-folder>
autorest
```

### Settings

```yaml
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/webpubsub/data-plane/WebPubSub/stable/2021-10-01/webpubsub.json
output-folder: ../azure/messaging/webpubsubservice
namespace: azure.messaging.webpubsubservice
package-name: azure-messaging-webpubsubservice
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
no-namespace-folders: true
python: true
title: WebPubSubServiceClient
version-tolerant: true
package-version: 1.0.0b2
add-credential: true
credential-scopes: https://webpubsub.azure.com/.default
```


Here's the directive to delete the health api operation that we don't need / want
```yaml

directive:
  - from: swagger-document
    where: $["paths"]["/api/health"]
    transform: >
        delete $["head"];
```

Here's the directive to move the operations from the webpubsub operation group directly onto the client

```yaml

directive:
  - from: swagger-document
    where: $["paths"][*]
    transform: >
        for (var op of Object.values($)) {
          if (op["operationId"].includes("WebPubSub_")) {
            op["operationId"] = op["operationId"].replace("WebPubSub_", "");
          }
        }
```