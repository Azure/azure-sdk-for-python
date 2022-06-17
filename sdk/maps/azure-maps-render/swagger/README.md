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
autorest --v3 --python
```

## Settings

```yaml
input: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/maps/data-plane/Render/preview/2.1/render.json
output-folder: ../azure/maps/render/_generated
namespace: azure.maps.render
package-name: azure-maps-render
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
credential-scopes: https://atlas.microsoft.com/.default
clear-output-folder: true
python: true
no-async: false
add-credential: false
title: MapsRenderClient
disable-async-iterators: true
python-sdks-folder: $(python-sdks-folder)
```
