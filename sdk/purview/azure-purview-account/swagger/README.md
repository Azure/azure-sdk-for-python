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
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/purview/data-plane/Azure.Analytics.Purview.Account/preview/2019-11-01-preview/account.json
output-folder: ../azure/purview/account
namespace: azure.purview.account
package-name: azure-purview-account
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
no-namespace-folders: true
python: true
title: PurviewAccountClient
version-tolerant: true
package-version: 1.0.0b1
add-credential: true
credential-scopes: https://purview.azure.net/.default
```
