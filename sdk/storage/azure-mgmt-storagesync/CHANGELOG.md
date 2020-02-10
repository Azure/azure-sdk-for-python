# Release History

## 0.2.0 (2020-01-09)

**Features**

  - Model ServerEndpoint has a new parameter recall_status
  - Model ServerEndpoint has a new parameter cloud_tiering_status
  - Model CloudEndpointCreateParameters has a new parameter
    friendly_name
  - Added operation CloudEndpointsOperations.trigger_change_detection
  - Added operation group OperationStatusOperations

**General Breaking Changes**

This version uses a next-generation code generator that might introduce
breaking changes if from some import. In summary, some modules were
incorrectly visible/importable and have been renamed. This fixed several
issues caused by usage of classes that were not supposed to be used in
the first place. StorageSyncManagementClient cannot be imported from
azure.mgmt.storagesync.storage_sync_management_client anymore (import
from azure.mgmt.storagesync works like before)
StorageSyncManagementClientConfiguration import has been moved from
azure.mgmt.storagesync.storage_sync_management_client to
azure.mgmt.storagesync A model MyClass from a "models" sub-module cannot
be imported anymore using azure.mgmt.storagesync.models.my_class
(import from azure.mgmt.storagesync.models works like before) An
operation class MyClassOperations from an operations sub-module cannot
be imported anymore using
azure.mgmt.storagesync.operations.my_class_operations (import from
azure.mgmt.storagesync.operations works like before) Last but not least,
HTTP connection pooling is now enabled by default. You should always use
a client as a context manager, or call close(), or use no more than one
client per process.

## 0.1.0 (2019-04-05)

  - Initial Release
