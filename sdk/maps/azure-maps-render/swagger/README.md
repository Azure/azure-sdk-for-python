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
tag: '2022-08-01'
require: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/48bb51ee0753ed56a88b3e7f989a70bf19ba96bb/specification/maps/data-plane/Render/readme.md
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
python3-only: true
version-tolerant: true
models-mode: msrest
```
