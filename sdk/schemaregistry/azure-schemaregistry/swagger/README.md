# Azure ServiceBus for Python

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
cd C:\Work\SchemaRegistry\
autorest --use=@autorest/python@5.0.0-preview.6
```
### Settings
``` yaml
input-file: https://raw.githubusercontent.com/Azure/azure-sdk-for-java/master/sdk/schemaregistry/azure-data-schemaregistry/swagger/swagger.json
output-folder: ../azure/schemaregistry/_generated
namespace: azure.schemaregistry._generated
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
enable-xml: false
vanilla: true
clear-output-folder: true
python: true
package-version: "1.0.0b1"
```
