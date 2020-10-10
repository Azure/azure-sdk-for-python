# Azure Queue Storage for Python

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
autorest README.md --use=@autorest/python@5.1.0-preview.7
```

### Settings
```yaml
input-file: appconfiguration.json
output-folder: ../azure/appconfiguration/_generated
namespace: azure.appconfiguration
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
enable-xml: false
vanilla: true
clear-output-folder: true
add-credentials: true
python: true
```
