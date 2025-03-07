# Azure Maps Timezone for Python

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
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/maps/data-plane/Timezone/preview/1.0/timezone.json
output-folder: ../azure/maps/timezone/_generated
namespace: azure.maps.timezone
package-name: azure-maps-timezone
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
credential-scopes: https://atlas.microsoft.com/.default
clear-output-folder: true
python: true
no-async: false
add-credential: false
title: TimezoneClient
disable-async-iterators: true
python-sdks-folder: $(python-sdks-folder)

directive:
- from: swagger-document
  where: $.securityDefinitions
  transform: |
    $["SharedKey"]["in"] = "header";

- from: swagger-document
  where: $.parameters.TimezoneTransitionsYears
  transform: |
    $["x-ms-client-name"] = "dst_lating_years"

- from: swagger-document
  where: $.parameters.TimezoneTransitionsFrom
  transform: |
    $["x-ms-client-name"] = "dst_from"
```
