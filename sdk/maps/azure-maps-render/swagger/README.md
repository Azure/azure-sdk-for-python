# Azure Maps Render for Python

> see <https://aka.ms/autorest>

## Setup

Install Autorest v3

```ps
npm install -g autorest
```

## Generation

```ps
cd <swagger-folder>
autorest .\README.md
```

## Settings

```yaml
tag: '2024-04-01'
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/maps/data-plane/Render/stable/2024-04-01/render.json
output-folder: ../azure/maps/render/_generated
namespace: azure.maps.render
package-name: azure-maps-render
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
credential-scopes: https://atlas.microsoft.com/.default
clear-output-folder: true
python: true
add-credential: true
title: MapsRenderClient
disable-async-iterators: true
python-sdks-folder: $(python-sdks-folder)
python3-only: true
```
