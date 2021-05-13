# Azure AgriFood Farming FarmBeats for Python

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
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/specification/agfood/data-plane/Microsoft.AgFoodPlatform/preview/2021-03-31-preview/agfood.json
output-folder: ../azure/agrifood/farming
namespace: azure.agrifood.farming
package-name: azure-agrifood-farming
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
no-namespace-folders: true
python: true
title: FarmBeatsClient
package-version: 1.0.0b1
add-credential: true
credential-scopes: https://farmbeats.azure.net/.default
```
