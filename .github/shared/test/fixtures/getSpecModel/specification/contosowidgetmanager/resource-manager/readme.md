# containerstorage

> see https://aka.ms/autorest
This is the AutoRest configuration file for Contoso.

## Getting Started

To build the SDKs for My API, simply install AutoRest via `npm` (`npm install -g autorest`) and then run:

> `autorest readme.md`
To see additional help and options, run:

> `autorest --help`
For other options on installation see [Installing AutoRest](https://aka.ms/autorest/install) on the AutoRest github page.

---

## Configuration

### Basic Information

These are the global settings for the containerstorage.

```yaml
openapi-type: arm
openapi-subtype: rpaas
tag: package-2021-11-01
```

### Tag: package-2021-11-01

These settings apply only when `--tag=package-2021-11-01` is specified on the command line.

`$(this-folder)` points to the folder where the readme.md file is located. It
may be used in some specs. In those cases, it can effectively be treated as "."
because the values in input-files are already relative to the current readme.md
file.

Some files may also have a backslash in the path. Path separators should be 
forward slashes, but backslash is supported.

```yaml $(tag) == 'package-2021-11-01'
input-file:
  - $(this-folder)/Microsoft.Contoso/stable/2021-11-01\contoso.json
```

### Tag: package-2021-10-01-preview

These settings apply only when `--tag=package-2021-10-01-preview` is specified on the command line.

input-file can be a single file or an array of files. Test the single value
scenario.

```yaml $(tag) == 'package-2021-10-01-preview'
input-file: Microsoft.Contoso/preview/2021-10-01-preview/contoso.json
```

### Tag: empty-properties

This tag has no yaml entities defined and is intended to test parser scenarios
around empty properties.

``` yaml $(tag) == 'empty-properties'

```

### Tag: no-input-files

This tag has no input-files and is intended to test parser scenarios around no
input-files.

``` yaml $(tag) == 'no-input-files'
some-thing: 
  - some-thing-1
  - some-thing-2
```

---
