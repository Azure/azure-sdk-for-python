# Azure Blob Storage for Python

> see https://aka.ms/autorest

### Setup

Install Autorest v3

```ps
npm install -g autorest
```

### Generation

```ps
cd <swagger-folder>
autorest --v3 --python
```

### Settings

```yaml
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/dev-agfood-Microsoft.AgFoodPlatform-2021-03-31-preview/specification/agfood/data-plane/Microsoft.AgFoodPlatform/preview/2021-03-31-preview/agfood.json
output-folder: ../azure/farmbeats
namespace: azure.farmbeats
package-name: azure-farmbeats
license-header: MICROSOFT_MIT_NO_VERSION
vanilla: true
clear-output-folder: true
no-namespace-folders: true
python: true
title: FarmBeatsClient
rest-layer: true
no-models: true
vendor: true
package-version: 1.0.0b1
add-credential: true
credential-scopes: https://farmbeats-dogfood.azure.net/.default
only-path-params-positional: true
```
