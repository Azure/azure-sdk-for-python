# Blob Storage
> see https://aka.ms/autorest

## Configuration
``` yaml

# Prevent swagger validation because it complains about vendor extensions
# instead of ignoring them per the spec
pipeline:
  swagger-document/individual/schema-validator:
     scope: unused

# Generate blob storage
input-file: ./blob.json
```

## Python

These settings apply only when `--python` is specified on the command line.
``` yaml $(python)
python-mode: create
python:
  azure-arm: true
  license-header: MICROSOFT_MIT_NO_VERSION
  payload-flattening-threshold: 2
  namespace: azure.storage.blob
  package-name: azure-storage-blob
  clear-output-folder: true
```
``` yaml $(python) && $(python-mode) == 'create'
python:
  basic-setup-py: true
  output-folder: ../azure/storage/blob/_generated
```