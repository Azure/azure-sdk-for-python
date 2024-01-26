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
input-file: https://github.com/Azure/azure-rest-api-specs/blob/28c5aaa5810448fce57da7e47427259a0c8850bf/specification/purview/data-plane/Azure.Analytics.Purview.DataMap/stable/2023-09-01/purviewdatamap.json
output-folder: ../azure/purview/datamap
namespace: azure.purview.datamap
package-name: azure-purview-datamap
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
no-namespace-folders: true
python: true
title: PurviewDataMapClient
package-version: 1.0.0b1
add-credential: true
credential-scopes: https://purview.azure.net/.default
only-path-params-positional: true
version-tolerant: true
```
