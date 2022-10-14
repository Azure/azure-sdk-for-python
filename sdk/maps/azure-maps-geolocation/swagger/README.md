# Azure Maps Geolocation for Python

> see https://aka.ms/autorest

## Setup

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
tag: 1.0-preview
require: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/maps/data-plane/Geolocation/readme.md
output-folder: ../azure/maps/geolocation/_generated
namespace: azure.maps.geolocation
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
enable-xml: true
vanilla: true
clear-output-folder: true
python: true
python3-only: true
version-tolerant: true
models-mode: msrest
```

```yaml
directive:
- from: swagger-document
  where: $.securityDefinitions
  transform: |
    $["SharedKey"]["in"] = "header";
```
