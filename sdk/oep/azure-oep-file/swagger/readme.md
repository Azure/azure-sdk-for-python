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
input-file: file.json
output-folder: ../azure/oep/file
namespace: azure.oep.file
package-name: azure-oep-file
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
no-namespace-folders: true
python: true
title: OepFileClient
package-version: 1.0.0b1
add-credential: true
credential-scopes: https://management.azure.com/.default
```
