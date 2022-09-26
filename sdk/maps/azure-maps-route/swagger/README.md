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
``` yaml
input-file: https://github.com/Azure/azure-rest-api-specs/blob/f729f12bb95b4515b51ded20aab2f728551053b6/specification/maps/data-plane/Route/preview/1.0/route.json
output-folder: ../azure/maps/route/_generated
namespace: azure.maps.route
no-namespace-folders: true
use-extension:
  "@autorest/modelerfour": "4.22.3"

license-header: MICROSOFT_MIT_NO_VERSION
enable-xml: true
vanilla: true
clear-output-folder: true
python: true
python3-only: true
version-tolerant: true
models-mode: msrest
```
