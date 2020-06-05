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
cd C:\Work\ServiceBus\
autorest --use=@autorest/python@5.0.0-preview.6
```
### Settings
``` yaml
input-file: servicebus-swagger.json
output-folder: ../azure/servicebus/management/_generated
namespace: azure.service._control_client2
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
enable-xml: false
vanilla: true
clear-output-folder: true
python: true
package-version: "2017-04"
```