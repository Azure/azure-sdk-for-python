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
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/webpubsub/data-plane/WebPubSub/preview/2021-08-01-preview/webpubsub.json
output-folder: ../azure/messaging/webpubsubservice
namespace: azure.messaging.webpubsubservice
package-name: azure-messaging-webpubsubservice
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
no-namespace-folders: true
python: true
title: WebPubSubServiceClient
version-tolerant: true
package-version: 1.0.0b1
add-credential: true
credential-scopes: https://webpubsub.azure.com/.default
```
