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
input-file: storage.json
output-folder: ../azure/oep/storage
namespace: azure.oep.storage
package-name: azure-oep-storage
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
no-namespace-folders: true
python: true
title: OepStorageClient
package-version: 1.0.0b1
add-credential: true
credential-scopes: https://management.azure.com/.default
```
