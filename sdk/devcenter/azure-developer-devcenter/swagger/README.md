### Settings

```yaml
input-file:
  - C:\Users\chrismiller\source\repos\azure-devtest-center\src\sdk\specification\devcenter\data-plane\Microsoft.DevCenter\preview\2022-03-01-preview\devcenter.json
  - C:\Users\chrismiller\source\repos\azure-devtest-center\src\sdk\specification\devcenter\data-plane\Microsoft.DevCenter\preview\2022-03-01-preview\devbox.json
  - C:\Users\chrismiller\source\repos\azure-devtest-center\src\sdk\specification\devcenter\data-plane\Microsoft.DevCenter\preview\2022-03-01-preview\environments.json
output-folder: ../
namespace: azure.developer.devcenter
package-name: azure-developer-devcenter
license-header: MICROSOFT_MIT_NO_VERSION
title: DevCenterClient
package-version: 1.0.0b1
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