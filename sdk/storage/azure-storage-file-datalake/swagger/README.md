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
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/storage/data-plane/Microsoft.StorageDataLake/preview/2020-10-02/DataLakeStorage.json
output-folder: ../azure/storage/filedatalake/_generated
namespace: azure.storage.filedatalake
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

### Add url parameter to each operation and add it to the url
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
        var newName = '{url}' + property;
        $[newName] = $[oldName];
        delete $[oldName];
    }
```
