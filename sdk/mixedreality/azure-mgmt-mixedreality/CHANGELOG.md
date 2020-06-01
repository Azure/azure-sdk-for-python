# Release History

## 0.2.0 (2020-05-25)

**Features**

  - Added operation SpatialAnchorsAccountsOperations.list_keys
  - Added operation SpatialAnchorsAccountsOperations.get
  - Added operation SpatialAnchorsAccountsOperations.regenerate_keys
  - Added operation SpatialAnchorsAccountsOperations.delete
  - Added operation group MixedRealityClientOperationsMixin
  - Added operation group RemoteRenderingAccountsOperations

**Breaking changes**

  - Operation SpatialAnchorsAccountsOperations.create has a new signature
  - Operation SpatialAnchorsAccountsOperations.update has a new signature
  - Removed operation SpatialAnchorsAccountsOperations.get_keys

**General Breaking Changes**

This version uses a next-generation code generator that *might*
introduce breaking changes. In summary, some modules were incorrectly
visible/importable and have been renamed. This fixed several issues
caused by usage of classes that were not supposed to be used in the
first place.

  - MixedRealityClient cannot be imported from
    `azure.mgmt.mixedreality.mixed_reality_client` anymore (import from
    `azure.mgmt.mixedreality` works like before)
  - MixedRealityClientConfiguration import has been moved from
    `azure.mgmt.mixedreality.mixedreality_client` 
    to `azure.mgmt.mixedreality`  
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.mixedreality.models.my_class` (import from
    `azure.mgmt.mixedreality.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.mixedreality.operations.my_class_operations` (import from
    `azure.mgmt.mixedreality.operations` works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 0.1.0 (2019-02-05)

  - Initial Release
