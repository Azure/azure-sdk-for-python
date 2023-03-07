## Azure Appconfiguration for Python

### Settings
``` yaml
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/appconfiguration/data-plane/Microsoft.AppConfiguration/preview/2022-11-01-preview/appconfiguration.json
output-folder: "../azure/appconfiguration/_generated"
namespace: azure.appconfiguration
no-namespace-folders: true
python: true
python-mode: create
license-header: MICROSOFT_MIT_NO_VERSION
package-name: azure-appconfiguration
clear-output-folder: true
enable-xml: true
vanilla: true
version-tolerant: false
```

## Customizations for Track 2 Generator

See the [AutoRest samples](https://github.com/Azure/autorest/tree/master/Samples/3b-custom-transformations)
for more about how we're customizing things.

### Rename the enum "KeyValueFilter" to "ConfigurationSettingFilter"
``` yaml
directive:
  from: swagger-document
  where: $.definitions.KeyValueFilter
  transform: >
    $['x-ms-client-name'] = "ConfigurationSettingFilter"
```
