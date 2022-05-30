# Azure Blob Storage for Python

> see https://aka.ms/autorest

### Setup
Install Autorest v3
```ps
npm install -g autorest
```

### Generation
```ps
cd <swagger-folder>
autorest --v3 --python
```

### Settings
``` yaml
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/storage/data-plane/Microsoft.BlobStorage/preview/2021-04-10/blob.json
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

### EncryptionAlgorithm workaround until Modeler is fixed
``` yaml
directive:
- from: swagger-document
  where: $.parameters
  transform: >
    delete $.EncryptionAlgorithm.enum;
    $.EncryptionAlgorithm.enum = [
      "None",
      "AES256"
    ];
```

### Remove ContainerName and BlobName from parameter list since they are not needed
``` yaml
directive:
- from: swagger-document
  where: $["x-ms-paths"]
  transform: >
    for (const property in $)
    {
        if (property.includes('/{containerName}/{blob}'))
        {
            $[property]["parameters"] = $[property]["parameters"].filter(function(param) { return (typeof param['$ref'] === "undefined") || (false == param['$ref'].endsWith("#/parameters/ContainerName") && false == param['$ref'].endsWith("#/parameters/Blob"))});
        }
        else if (property.includes('/{containerName}'))
        {
            $[property]["parameters"] = $[property]["parameters"].filter(function(param) { return (typeof param['$ref'] === "undefined") || (false == param['$ref'].endsWith("#/parameters/ContainerName"))});
        }
    }
```

### Change to OrMetadata
``` yaml
directive:
- from: swagger-document
  where: $.definitions.BlobItemInternal
  transform: |
    $.properties.OrMetadata = $.properties.ObjectReplicationMetadata;
    $.properties.OrMetadata["x-ms-client-name"] = "ObjectReplicationMetadata";
    delete $.properties.ObjectReplicationMetadata;
```

### Remove x-ms-parameterized-host
``` yaml
directive:
- from: swagger-document
  where: $
  transform: >
    $["x-ms-parameterized-host"] = undefined;
```

### Add url parameter to each operation and add url to the path
``` yaml
directive:
- from: swagger-document
  where: $["x-ms-paths"]
  transform: >
    for (const property in $)
    {
        $[property]["parameters"].push({"$ref": "#/parameters/Url"});

        var oldName = property;
        // For service operations (where the path is just '/') we need to
        // remove the '/' at the begining to avoid having an extra '/' in
        // the final URL.
        if (property === '/' || property.startsWith('/?'))
        {
            var newName = '{url}' + property.substring(1);
        }
        else
        {
            var newName = '{url}' + property;
        }
        $[newName] = $[oldName];
        delete $[oldName];
    }
```
