# Azure DataLake for Python

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
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/storage/data-plane/Azure.Storage.Files.DataLake/preview/2023-05-03/DataLakeStorage.json
output-folder: ../azure/storage/filedatalake/_generated
namespace: azure.storage.filedatalake
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
  where: $["x-ms-paths"]["/{filesystem}?restype=container&comp=list&hierarchy"].get
  transform: >
    delete $["x-ms-pageable"];
```

### Remove Filesystem and PathName from parameter list since they are not needed
``` yaml
directive:
- from: swagger-document
  where: $["x-ms-paths"]
  transform: >
    for (const property in $)
    {
        if (property.includes('/{filesystem}/{path}'))
        {
            $[property]["parameters"] = $[property]["parameters"].filter(function(param) { return (typeof param['$ref'] === "undefined") || (false == param['$ref'].endsWith("#/parameters/FileSystem") && false == param['$ref'].endsWith("#/parameters/Path"))});
        }
        else if (property.includes('/{filesystem}'))
        {
            $[property]["parameters"] = $[property]["parameters"].filter(function(param) { return (typeof param['$ref'] === "undefined") || (false == param['$ref'].endsWith("#/parameters/FileSystem"))});
        }
    }
```

### Remove x-ms-pageable
Currently breaking the latest version of autorest.python
``` yaml
directive:
- from: swagger-document
  where: $["x-ms-paths"]["/{filesystem}?resource=filesystem"].get
  transform: >
    delete $["x-ms-pageable"];
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
        if ($[property]["parameters"] === undefined)
        {
            $[property]["parameters"] = []
        }
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

## Don't include FileSystem and Path in path - we have direct URIs.

This directive is necessary for Python (also this directive is copied from .net) because we removed our call to
_format_url_section in our generated code.

```yaml
directive:
- from: swagger-document
  where: $["x-ms-paths"]
  transform: >
    for (const property in $)
    {
        if (property.includes('/{filesystem}/{path}'))
        {
            var oldName = property;
            var newName = property.replace('/{filesystem}/{path}', '');
            if (!newName.includes('?'))
            {
              newName = newName + '?' + 'filesystem_path'
            }
            $[newName] = $[oldName];
            delete $[oldName];
        }
        else if (property.includes('/{filesystem}'))
        {
            var oldName = property;
            var newName = property.replace('/{filesystem}', '');
            if (!newName.includes('?'))
            {
              newName = newName + '?' + 'filesystem'
            }
            $[newName] = $[oldName];
            delete $[oldName];
        }
    }
```