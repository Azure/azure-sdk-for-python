# Generate SDK using Autorest

> see `https://aka.ms/autorest`

## Getting started
```ps
cd <swagger-folder>
autorest --v3 --python
```
## Settings

```yaml
input-file:
- C:\Azure-Media-LiveVideoAnalytics\src\Edge\Client\AzureVideoAnalyzer.Edge\preview\1.0\AzureVideoAnalyzer.json
- C:\Azure-Media-LiveVideoAnalytics\src\Edge\Client\AzureVideoAnalyzer.Edge\preview\1.0\AzureVideoAnalyzerSdkDefinitions.json
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
