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
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/specification/purview/data-plane/Azure.Analytics.Purview.Scanning/preview/2018-12-01-preview/scanningService.json
output-folder: ../azure/purview/scanning
namespace: azure.purview.scanning
package-name: azure-purview-scanning
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
no-namespace-folders: true
python: true
title: PurviewScanningClient
version-tolerant: true
package-version: 1.0.0b2
add-credential: true
credential-scopes: https://purview.azure.net/.default
```

``` yaml
modelerfour:
  lenient-model-deduplication: true
```