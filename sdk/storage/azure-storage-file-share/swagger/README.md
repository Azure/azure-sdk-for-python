# Azure File Storage for Python

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
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/storage/data-plane/Microsoft.FileStorage/stable/2025-05-05/file.json
output-folder: ../azure/storage/fileshare/_generated
namespace: azure.storage.fileshare
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
enable-xml: true
vanilla: true
clear-output-folder: true
python: true
version-tolerant: false
modelerfour:
    seal-single-value-enum-by-default: true
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
- from: swagger-document
  where: $["x-ms-paths"]..responses..headers["x-ms-file-last-write-time"]
  transform: >
    $.format = "str";
- from: swagger-document
  where: $["x-ms-paths"]..responses..headers["x-ms-file-change-time"]
  transform: >
    $.format = "str";
- from: swagger-document
  where: $["x-ms-paths"]..responses..headers["x-ms-file-creation-time"]
  transform: >
    $.format = "str";
- from: swagger-document
  where: $.parameters.FileChangeTime
  transform: >
    $.format = "str";
```

### Change new SMB file parameters to use default values
TODO: Verify these default values are correct
``` yaml
directive:
- from: swagger-document
  where: $.parameters.FileCreationTime
  transform: >
    $.format = "str";
    $.default = "now";
- from: swagger-document
  where: $.parameters.FileLastWriteTime
  transform: >
    $.format = "str";
    $.default = "now";
- from: swagger-document
  where: $.parameters.FileAttributes
  transform: >
    $.default = "none";
- from: swagger-document
  where: $.parameters.FilePermission
  transform: >
    $.default = "inherit";
```

### Don't include share name, directory, or file name in path - we have direct URIs.
``` yaml
directive:
- from: swagger-document
  where: $["x-ms-paths"]
  transform: >
    for (const property in $)
    {
        if (property.includes('/{shareName}/{directory}/{fileName}'))
        {
            $[property]["parameters"] = $[property]["parameters"].filter(function(param) { return (typeof param['$ref'] === "undefined") || (false == param['$ref'].endsWith("#/parameters/ShareName") && false == param['$ref'].endsWith("#/parameters/DirectoryPath") && false == param['$ref'].endsWith("#/parameters/FilePath"))});
        }
        else if (property.includes('/{shareName}/{directory}'))
        {
            $[property]["parameters"] = $[property]["parameters"].filter(function(param) { return (typeof param['$ref'] === "undefined") || (false == param['$ref'].endsWith("#/parameters/ShareName") && false == param['$ref'].endsWith("#/parameters/DirectoryPath"))});
        }
        else if (property.includes('/{shareName}'))
        {
            $[property]["parameters"] = $[property]["parameters"].filter(function(param) { return (typeof param['$ref'] === "undefined") || (false == param['$ref'].endsWith("#/parameters/ShareName"))});
        }
    }
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

## Remove ShareName, Directory, and FileName - we have direct URIs

This directive is necessary for Python (also this directive is copied from .net) because we removed our call to
_format_url_section in our generated code. We also add dummy query parameters to avoid collisions.

```yaml
directive:
- from: swagger-document
  where: $["x-ms-paths"]
  transform: >
   Object.keys($).map(id => {
     if (id.includes('/{shareName}/{directory}/{fileName}'))
     {
       $[id.replace('/{shareName}/{directory}/{fileName}', '?dummyFile')] = $[id];
       delete $[id];
     }
     else if (id.includes('/{shareName}/{directory}'))
     {
       $[id.replace('/{shareName}/{directory}', '?dummyDir')] = $[id];
       delete $[id];
     }
     else if (id.includes('/{shareName}'))
     {
       $[id.replace('/{shareName}', '?dummyShare')] = $[id];
       delete $[id];
     }
   });
```
