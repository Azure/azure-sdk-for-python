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
input-file: https://github.com/Azure/azure-rest-api-specs/blob/e38daec67d57ef9c4804b1e3055753407e45fa71/specification/agrifood/data-plane/Microsoft.AgFoodPlatform/preview/2022-11-01-preview/agfood.json
output-folder: ../azure/agrifood/farming
namespace: azure.agrifood.farming
package-name: azure-agrifood-farming
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
no-namespace-folders: true
python: true
title: FarmBeatsClient
package-version: 1.0.0b2
security: AADToken
security-scopes: https://farmbeats.azure.net/.default
```
