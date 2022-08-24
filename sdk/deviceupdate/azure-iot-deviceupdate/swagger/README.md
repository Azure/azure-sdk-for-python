# Azure Device Update autorest configuration for Python

### Settings

```yaml
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/d01a6a71b73e6b3cac477eae7e78454c3f6d4340/specification/deviceupdate/data-plane/Microsoft.DeviceUpdate/stable/2022-10-01/deviceupdate.json
output-folder: ../azure/iot/deviceupdate
namespace: azure.iot.deviceupdate
package-name: azure-iot-deviceupdate
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
no-namespace-folders: true
python: true
title: DeviceUpdateClient
version-tolerant: true
package-version: 1.0.0b4
add-credential: true
credential-scopes: https://api.adu.microsoft.com/.default
```
