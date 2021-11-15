# Azure Communication Configuration for Python

> see https://aka.ms/autorest

### Setup
```ps
npm install -g autorest
```

### Generation
```ps
cd <swagger-folder>
autorest SWAGGER.md
```

### Basic Information

These are the global settings for Search Client.

``` yaml
title: SearchClient
openapi-type: data-plane
tag: 1.0-preview
# at some point those credentials will move away to Swagger according to [this](https://github.com/Azure/autorest/issues/3718)
add-credentials: true
credential-default-policy-type: BearerTokenCredentialPolicy
credential-scopes: https://atlas.microsoft.com/.default
```

### Tag: 1.0-preview

These settings apply only when `--tag=1.0-preview` is specified on the command line.

``` yaml $(tag) == '1.0-preview'
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/maps/data-plane/Search/preview/1.0/search.json
```

``` yaml $(python)
python-mode: create
license-header: MICROSOFT_MIT_NO_VERSION
namespace: azure.maps.search
package-name: azure-maps-search
package-version: 1.0-preview
clear-output-folder: true
```
``` yaml $(python) && $(tag) == '1.0-preview' && $(python-mode) == 'update'
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/maps/data-plane/Search/preview/1.0/search.json
no-namespace-folders: true
output-folder: $(python-sdks-folder)/maps/azure-maps-search/azure/maps/search/_generated
```
``` yaml $(python) && $(tag) == '1.0-preview' && $(python-mode) == 'create'
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/maps/data-plane/Search/preview/1.0/search.json
basic-setup-py: true
output-folder: $(python-sdks-folder)/maps/azure-maps-search/_generated
```
