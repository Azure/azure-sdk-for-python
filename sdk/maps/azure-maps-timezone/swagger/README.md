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
tag: 1.0-preview
require: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/maps/data-plane/Timezone/readme.md
output-folder: ../azure/maps/timezone/_generated
package-version: 1.0.0b1
use-extension:
  "@autorest/modelerfour": "4.22.3"
namespace: azure.maps.timezone
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
python: true
python3-enable: true
version-tolerant: true
models-mode: msrest
```
