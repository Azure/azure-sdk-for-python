## Azure Container Registry for Python

### Settings
``` yaml
title: Container Registry
input-file: https://github.com/Azure/azure-rest-api-specs/blob/c8d9a26a2857828e095903efa72512cf3a76c15d/specification/containerregistry/data-plane/Azure.ContainerRegistry/stable/2021-07-01/containerregistry.json
output-folder: "../azure/containerregistry/_generated"
no-namespace-folders: true
python: true
clear-output-folder: true
add-credentials: true
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

## Customizations for Track 2 Generator

See the [AutoRest samples](https://github.com/Azure/autorest/tree/master/Samples/3b-custom-transformations)
for more about how we're customizing things.

### Rename the enum "TagOrderBy" to "ArtifactTagOrder"
``` yaml
directive:
  from: swagger-document
  where: $.definitions.TagOrderBy
  transform: >
    $['x-ms-enum']["name"] = "ArtifactTagOrder"
```

### Rename the enum "ManifestOrderBy" to "ArtifactManifestOrder"
``` yaml
directive:
  from: swagger-document
  where: $.definitions.ManifestOrderBy
  transform: >
    $['x-ms-enum']["name"] = "ArtifactManifestOrder"
```

### Remove response for "ContainerRegistry_DeleteRepository" operation

so that the generate code doesn't return a response for the delete repository operation.

```yaml
directive:
  - from: swagger-document
    where: $["paths"]["/acr/v1/{name}"]
    transform: >
      delete $.delete["responses"]["202"].schema
```

### Remove "Authentication_GetAcrAccessTokenFromLogin" operation

as the service team discourage using username/password to authenticate.

```yaml
directive:
  - from: swagger-document
    where: $["paths"]["/oauth2/token"]
    transform: >
      delete $.get
```

### Remove "definitions.TagAttributesBase.properties.signed"

as we don't have a SDK client customer scenario using it.

```yaml
directive:
  - from: swagger-document
    where: $.definitions.TagAttributesBase
    transform: >
      delete $.properties.signed
```

### Remove "definitions.ManifestAttributesBase.properties.configMediaType"

as we don't have a SDK client customer scenario using it.

```yaml
directive:
  - from: swagger-document
    where: $.definitions.ManifestAttributesBase
    transform: >
      delete $.properties.configMediaType
```

### Change "parameters.ApiVersionParameter.required" to true

so that the generated client/clientcontext constructors take api_version as a parameter.

```yaml
directive:
  - from: swagger-document
    where: $.parameters.ApiVersionParameter
    transform: >
      $.required = true
```

### Change NextLink client name to nextLink
``` yaml
directive:
  from: swagger-document
  where: $.parameters.NextLink
  transform: >
    $["x-ms-client-name"] = "nextLink"
```

### Take stream as manifest body
``` yaml
directive:
  from: swagger-document
  where: $.parameters.ManifestBody
  transform: >
    $.schema = {
        "type": "string",
        "format": "binary"
      }
```

### Replace ManifestWrapper with stream response to calculate SHA256
``` yaml
directive:
  from: swagger-document
  where: $.paths["/v2/{name}/manifests/{reference}"].get.responses["200"]
  transform: >
      $.schema = {
          "type": "string",
          "format": "binary"
      };
```

### Rename parameter "Range" to "RangeHeader"
``` yaml
directive:
  from: swagger-document
  where: $.parameters.Range
  transform: >
    $["x-ms-client-name"] = "RangeHeader"
```

### Remove security definitions

as it is incorrect in swagger

```yaml
directive:
  - from: swagger-document
    where: $.
    transform: >
      delete $["securityDefinitions"];
      delete $["security"];
```

### Remove stream response from `deleteBlob`

as we don't care about the stream that is returned and we don't want to clean it up

```yaml
directive:
  - from: swagger-document
    where: $.paths["/v2/{name}/blobs/{digest}"]["delete"]
    transform: >
      delete $.responses["202"].schema;
```
