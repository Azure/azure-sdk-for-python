## Azure Appconfiguration for Python

### Settings
``` yaml
input-file: https://github.com/Azure/azure-rest-api-specs/raw/40e8bf1504ed672e86027b240dddd9ca94a15d4c/specification/containerregistry/data-plane/Azure.ContainerRegistry/preview/2019-08-15-preview/containerregistry.json
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
