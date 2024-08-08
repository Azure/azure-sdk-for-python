# Azure Maps Weather for Python

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
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/b9765efcc5ea795d69aeb8826f78101b3a35c615/specification/maps/data-plane/Weather/stable/1.1/weather.json
output-folder: ../azure/maps/weather
namespace: azure.maps.weather
package-name: azure-maps-weather
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
credential-scopes: https://atlas.microsoft.com/.default
clear-output-folder: true
python: true
no-async: false
add-credential: false
title: MapsWeatherClient
disable-async-iterators: true
python-sdks-folder: $(python-sdks-folder)

directive:
- from: swagger-document
  where: $.securityDefinitions
  transform: |
    $["SharedKey"]["in"] = "header";
```
