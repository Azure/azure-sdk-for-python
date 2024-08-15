## Azure Appconfiguration for Python

### Settings
``` yaml
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/c1af3ab8e803da2f40fc90217a6d023bc13b677f/specification/appconfiguration/data-plane/Microsoft.AppConfiguration/stable/2023-11-01/appconfiguration.json
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

### Rename the enum "KeyValueFields" to "ConfigurationSettingFields"
```yaml
directive:
  from: swagger-document
  where: $.parameters.KeyValueFields
  transform: >
    $.items["x-ms-enum"]["name"] = "ConfigurationSettingFields"
```

### Rename the enum "CompositionType" to "SnapshotComposition"
```yaml
directive:
  from: swagger-document
  where: $.definitions.Snapshot.properties
  transform: >
    $.composition_type["x-ms-enum"].name = "SnapshotComposition"
```
