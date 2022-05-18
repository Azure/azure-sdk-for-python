# Azure Search

> see https://aka.ms/autorest

This is the AutoRest configuration file for Search Client

---

## Getting Started

To build the SDK for Search, simply [Install AutoRest](https://aka.ms/autorest/install) and in this folder, run:

> `autorest`

To see additional help and options, run:

> `autorest --help`

---

## Configuration

### Basic Information

These are the global settings for Search Client.

``` yaml
title: SearchClient
openapi-type: data-plane
tag: 1.0-preview
license-header: MICROSOFT_MIT_NO_VERSION
add-credential: true
namespace: azure.maps.search
package-name: azure-maps-search
package-version: 1.0-preview
credential-default-policy-type: BearerTokenCredentialPolicy
credential-scopes: https://atlas.microsoft.com/.default
clear-output-folder: true
no-namespace-folders: true
python: true
multiapi: true
```

``` yaml $(tag) == '1.0-preview'
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/maps/data-plane/Search/preview/1.0/search.json
no-namespace-folders: true
output-folder: ../azure/maps/search/_generated
```