# Azure Queue Storage for Python

> see https://aka.ms/autorest


### Generation
```ps
cd <swagger-folder>
autorest README.md --use=@autorest/python@5.1.0-preview.7
```

### Settings
```yaml
input-file: computation.json
output-folder: ../azure/computation/_generated
namespace: azure.computation
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
enable-xml: false
vanilla: true
clear-output-folder: true
add-credentials: true
python: true
```
