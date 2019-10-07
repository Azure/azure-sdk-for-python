.. :changelog:

Release History
===============

0.4.0 (2019-07-04)
++++++++++++++++++

**Features**

- Model SqlVirtualMachine has a new parameter sql_management

**General Breaking changes**

This version uses a next-generation code generator that *might* introduce breaking changes if from some import.
In summary, some modules were incorrectly visible/importable and have been renamed. This fixed several issues caused by usage of classes that were not supposed to be used in the first place.

- SqlVirtualMachineManagementClient cannot be imported from `azure.mgmt.sqlvirtualmachine.sql_virtual_machine_management_client` anymore (import from `azure.mgmt.sqlvirtualmachine` works like before)
- SqlVirtualMachineManagementClientConfiguration import has been moved from `azure.mgmt.sqlvirtualmachine.sql_virtual_machine_management_client` to `azure.mgmt.sqlvirtualmachine`
- A model `MyClass` from a "models" sub-module cannot be imported anymore using `azure.mgmt.sqlvirtualmachine.models.my_class` (import from `azure.mgmt.sqlvirtualmachine.models` works like before)
- An operation class `MyClassOperations` from an `operations` sub-module cannot be imported anymore using `azure.mgmt.sqlvirtualmachine.operations.my_class_operations` (import from `azure.mgmt.sqlvirtualmachine.operations` works like before)

Last but not least, HTTP connection pooling is now enabled by default. You should always use a client as a context manager, or call close(), or use no more than one client per process.

0.3.0 (2019-06-03)
++++++++++++++++++

**Features**

- sql_image_sku is now writable

0.2.0 (2018-12-07)
++++++++++++++++++

**Features**

- Model SqlStorageUpdateSettings has a new parameter starting_device_id

**Breaking changes**

- Model AdditionalFeaturesServerConfigurations no longer has parameter backup_permissions_for_azure_backup_svc

0.1.0 (2018-11-27)
++++++++++++++++++

* Initial Release
