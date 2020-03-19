.. :changelog:

Release History
===============

2.0.0 (2019-12-25)
++++++++++++++++++

**Features**

- Added operation AppsOperations.list_templates

**General Breaking Changes**

This version uses a next-generation code generator that might introduce breaking changes if from some import. In summary, some modules were incorrectly visible/importable and have been renamed. This fixed several issues caused by usage of classes that were not supposed to be used in the first place.
IoTCentralClient cannot be imported from azure.mgmt.iotcentreal.iot_central_client anymore (import from azure.mgmt.iotcentreal works like before)
IoTCentralClientConfiguration import has been moved from azure.mgmt.iotcentreal.iot_central_client to azure.mgmt.iotcentreal
A model MyClass from a "models" sub-module cannot be imported anymore using azure.mgmt.iotcentreal.models.my_class (import from azure.mgmt.iotcentreal.models works like before)
An operation class MyClassOperations from an operations sub-module cannot be imported anymore using azure.mgmt.iotcentreal.operations.my_class_operations (import from azure.mgmt.iotcentreal.operations works like before)
Last but not least, HTTP connection pooling is now enabled by default. You should always use a client as a context manager, or call close(), or use no more than one client per process.

1.0.0 (2018-10-26)
++++++++++++++++++

**Features**

- Model OperationInputs has a new parameter type
- Model ErrorDetails has a new parameter details
- Added operation AppsOperations.check_subdomain_availability

**Breaking changes**

- Operation AppsOperations.check_name_availability has a new signature

**Note**

- azure-mgmt-nspkg is not installed anymore on Python 3 (PEP420-based namespace package)

0.2.0 (2018-08-07)
++++++++++++++++++

* Replace API version by 2018-09-01

0.1.0 (2018-07-16)
++++++++++++++++++

* Initial Release with support for 2017-07-01-privatepreview
