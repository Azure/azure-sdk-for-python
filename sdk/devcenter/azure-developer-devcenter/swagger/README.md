### Settings

```yaml
input-file:
  - https://github.com/Azure/azure-rest-api-specs/blob/af3f7994582c0cbd61a48b636907ad2ac95d332c/specification/devcenter/data-plane/Microsoft.DevCenter/preview/2022-11-11-preview/devcenter.json
  - https://github.com/Azure/azure-rest-api-specs/blob/af3f7994582c0cbd61a48b636907ad2ac95d332c/specification/devcenter/data-plane/Microsoft.DevCenter/preview/2022-11-11-preview/devbox.json
  - https://github.com/Azure/azure-rest-api-specs/blob/af3f7994582c0cbd61a48b636907ad2ac95d332c/specification/devcenter/data-plane/Microsoft.DevCenter/preview/2022-11-11-preview/environments.json
output-folder: ../
namespace: azure.developer.devcenter
package-name: azure-developer-devcenter
license-header: MICROSOFT_MIT_NO_VERSION
title: DevCenterClient
package-version: 1.0.0b3
package-mode: dataplane
package-pprint-name: Azure Developer DevCenter Service
security: AADToken
security-scopes: https://devcenter.azure.com/.default
```

### Put project as a method param, since Python will generate only one client
``` yaml
directive:
- from: swagger-document
  where: $.parameters["ProjectNameParameter"]
  transform: $["x-ms-parameter-location"] = "method"
```