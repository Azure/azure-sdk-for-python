# Generate SDK using Autorest

see `https://aka.ms/autorest`

## Getting started
```ps
cd <swagger-folder>
autorest --v3 --python
```
## Settings

```yaml
require: https://github.com/Azure/azure-rest-api-specs/blob/14732a2d9802c98cb8fea52800853874529c5f8e/specification/mediaservices/data-plane/readme.md
output-folder: ../azure/media/analyticsedge/_generated
namespace: azure.media.analyticsedge
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
