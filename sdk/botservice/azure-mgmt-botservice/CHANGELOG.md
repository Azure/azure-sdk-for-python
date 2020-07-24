# Release History

## 1.0.0 (2020-06-02)

General Breaking changes
This version uses a next-generation code generator that might introduce breaking changes if from some import. In summary, some modules were incorrectly visible/importable and have been renamed. This fixed several issues caused by usage of classes that were not supposed to be used in the first place.

* AzureBotService cannot be imported from azure.mgmt.botservice.azure_bot_service anymore (import from azure.mgmt.botservice works like before)
* A model MyClass from a "models" sub-module cannot be imported anymore using azure.mgmt.botservice.models.my_class (import from azure.mgmt.botservice.models works like before)
* An operation class MyClassOperations from an operations sub-module cannot be imported anymore using azure.mgmt.botservice.operations.my_class_operations (import from azure.mgmt.botservice.operations works like before)

Last but not least, HTTP connection pooling is now enabled by default. You should always use a client as a context manager, or call close(), or use no more than one client per process.

## 0.1.0 (2018-08-07)

  - Initial Release
