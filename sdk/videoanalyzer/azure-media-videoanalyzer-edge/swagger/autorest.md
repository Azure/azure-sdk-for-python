# Generate SDK using Autorest

> see `https://aka.ms/autorest`

## Getting started
```ps
cd <swagger-folder>
autorest --v3 --python
```
## Settings

```yaml
require: https://github.com/Azure/azure-rest-api-specs/blob/694fe69245024447f8d3647be1da88e9ad942058/specification/videoanalyzer/data-plane/readme.md
output-folder: ../azure/media/videoanalyzeredge/_generated
namespace: azure.media.videoanalyzer.edge
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
enable-xml: false
vanilla: true
clear-output-folder: true
add-credentials: false
python: true
package-version: "1.0"
public-clients: false
```