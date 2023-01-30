# Azure Maps Route for Python

> see https://aka.ms/autorest

### Setup
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
tag: '1.0'
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/2e88f0e0951d1cdbe59db4dafbc48c93a723bfa2/specification/maps/data-plane/Route/preview/1.0/route.json
output-folder: ../azure/maps/route/_generated
namespace: azure.maps.route
package-name: azure-maps-route
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
credential-scopes: https://atlas.microsoft.com/.default
clear-output-folder: true
python: true
no-async: false
add-credential: false
title: MapsRouteClient
disable-async-iterators: true
python-sdks-folder: $(python-sdks-folder)
python3-only: true
version-tolerant: true
models-mode: msrest
show-operations: true
only-path-and-body-parameters-positional: true
```

```yaml
directive:
- from: swagger-document
  where: $.securityDefinitions
  transform: |
    $["SharedKey"]["in"] = "header";
```
