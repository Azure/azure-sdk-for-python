# Azure Maps Route for Python

> see https://aka.ms/autorest

## Setup

```ps

npm install -g autorest
```

## Generation

```ps

cd <swagger-folder>
autorest SWAGGER.md
```

To generate this file, simply type

```ps

autorest swagger/README.md --python-sdks-folder=<location-of-your-sdk-dir>
```

We automatically hardcode in that this is `python`.

## Basic Information

```yaml
tag: 1.0-preview
require: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/maps/data-plane/Route/readme.md
output-folder: ../azure/maps/route/_generated
namespace: azure.maps.route
package-name: azure-maps-route
package-version: 1.0-preview
credential-default-policy-type: BearerTokenCredentialPolicy
credential-scopes: https://atlas.microsoft.com/.default
clear-output-folder: true
no-namespace-folders: true
python: true
no-async: false
add-credential: false
title: MapsRouteClient
disable-async-iterators: true
python-sdks-folder: $(python-sdks-folder)
```
