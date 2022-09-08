# Azure Device Update autorest configuration for Python

### Settings

```yaml
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/d7c9be23749467be1aea18f02ba2f4948a39db6a/specification/deviceupdate/data-plane/Microsoft.DeviceUpdate/stable/2022-10-01/deviceupdate.json
output-folder: ../azure/iot/deviceupdate
namespace: azure.iot.deviceupdate
package-name: azure-iot-deviceupdate
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
no-namespace-folders: true
python: true
title: DeviceUpdateClient
version-tolerant: true
package-version: 1.0.0
add-credential: true
credential-scopes: https://api.adu.microsoft.com/.default
```
