# Azure Blob Storage for Python

> see https://aka.ms/autorest

### Setup
```ps
cd C:\work
git clone --recursive https://github.com/Azure/autorest.python.git
cd autorest.python
git checkout azure-core
npm install
```

### Generation
```ps
cd <swagger-folder>
autorest --use=C:/work/autorest.python --version=2.0.4280
```

### Settings
``` yaml
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/storage-dataplane-preview/specification/storage/data-plane/Microsoft.BlobStorage/preview/2019-02-02/blob.json
output-folder: ../azure/storage/blob/_generated
namespace: azure.storage.blob
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
enable-xml: true
vanilla: true
clear-output-folder: true
python: true
```

### Remove x-ms-pageable
Currently breaking the latest version of autorest.python
``` yaml
directive:
- from: swagger-document
  where: $["x-ms-paths"]..get
  transform: >
    if ($["x-ms-pageable"]) { delete $["x-ms-pageable"]; }
```

### Use strings for dates when python doesn't have enough precision
``` yaml
directive:
- from: swagger-document
  where: $.definitions.AccessPolicy.properties
  transform: >
    $.Start.format = "str";
    $.Expiry.format = "str";
```

### BlobTagFilter
``` yaml
directive:
- from: swagger-document
  where: $.parameters.BlobTagFilter
  transform: >
    $["x-ms-parameter-location"] = "method";
```

### PathRenameMode
``` yaml
directive:
- from: swagger-document
  where: $.parameters.PathRenameMode
  transform: >
    $["x-ms-parameter-location"] = "method";
```

### BlobHierarchyListSegment
``` yaml
directive:
- from: swagger-document
  where: $.definitions.BlobHierarchyListSegment
  transform: >
    $.properties.BlobPrefixes.xml = { "name": "BlobPrefix" };
    $.properties.BlobItems.xml = { "name": "Blob" };
```

### SignedIdentifier shouldn't require an AccessPolicy, only ID
``` yaml
directive:
- from: swagger-document
  where: $.definitions.SignedIdentifier
  transform: >
    $.required = [ "Id" ];
```

### Make AccessTier Unique
autorest.python complains that the same enum has different values
``` yaml
directive:
- from: swagger-document
  where: $.parameters.AccessTierRequired
  transform: >
    $["x-ms-enum"].name = "AccessTierRequired";
- from: swagger-document
  where: $.parameters.AccessTierOptional
  transform: >
    $["x-ms-enum"].name = "AccessTierOptional";
```
