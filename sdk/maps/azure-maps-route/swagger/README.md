# Azure Maps Timezone for Python

> see https://aka.ms/autorest

## Setup

Install Autorest v3

```ps
npm install -g autorest
```

## Generation

```ps
cd <swagger-folder>
autorest --v3 --python
```

## Settings

``` yaml
input-file:
- https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/maps/data-plane/Timezone/preview/1.0/timezone.json
output-folder: ../azure/maps/timezone/_generated
namespace: azure.maps.timezone
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
enable-xml: true
vanilla: true
clear-output-folder: true
python: true
version-tolerant: false
```
