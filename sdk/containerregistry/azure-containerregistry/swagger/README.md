## Azure Appconfiguration for Python

### Settings
``` yaml
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/7d61610b5b54f21de3c95b64c341c7bde385c994/specification/containerregistry/data-plane/Azure.ContainerRegistry/preview/2019-08-15-preview/containerregistry.json
output-folder: "../azure/containerregistry/_generated"
no-namespace-folders: true
python: true
clear-output-folder: true
```


### Correct Security to be separately defined

``` yaml
directive:
  from: swagger-document
  where: $
  transform: >
    $.security = [
      {
        "registry_oauth2": []
      },
      {
        "registry_auth": []
      }
    ]
```
