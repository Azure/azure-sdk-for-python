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
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/purview/data-plane/Azure.Analytics.Purview.Catalog/preview/2021-05-01-preview/purviewcatalog.json
output-folder: ../azure/purview/catalog
namespace: azure.purview.catalog
package-name: azure-purview-catalog
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
no-namespace-folders: true
python: true
title: PurviewCatalogClient
package-version: 1.0.0b2
add-credential: true
credential-scopes: https://purview.azure.net/.default
only-path-params-positional: true
version-tolerant: true
```
