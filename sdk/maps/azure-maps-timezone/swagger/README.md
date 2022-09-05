# Azure Maps Timezone for Python

> see <https://aka.ms/autorest>

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
require: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/maps/data-plane/Timezone/readme.md
output-folder: ../azure/maps/timezone/_generated
use-extension:
  "@autorest/modelerfour": "4.22.3"
namespace: azure.maps.timezone
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
enable-xml: true
vanilla: true
clear-output-folder: true
python: true
version-tolerant: false
```
