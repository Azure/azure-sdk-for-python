# Azure Maps Search for Python

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
require: https://raw.githubusercontent.com/alextts627/azure-rest-api-specs/main/specification/maps/data-plane/Search/readme.md
output-folder: ../azure/maps/search/_generated
namespace: azure.maps.search
package-name: azure-maps-search
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
credential-scopes: https://cognitiveservices.azure.com/.default
clear-output-folder: true
python: true
no-async: false
add-credential: false
title: SearchClient
disable-async-iterators: true
python-sdks-folder: $(python-sdks-folder)
```
