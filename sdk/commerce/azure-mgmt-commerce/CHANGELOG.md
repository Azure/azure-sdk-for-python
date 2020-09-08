# Release History


## 2.0.0rc1 (2020-09-08)

Release as Multi-API package.

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes if you were importing from the v20xx_yy_zz
API folders. In summary, some modules were incorrectly
visible/importable and have been renamed. This fixed several issues
caused by usage of classes that were not supposed to be used in the
first place.

  - ComputeManagementClient cannot be imported from
    `azure.mgmt.compute.v20xx_yy_zz.compute_management_client`
    anymore (import from `azure.mgmt.compute.v20xx_yy_zz` works like
    before)
  - ComputeManagementClientConfiguration import has been moved from
    `azure.mgmt.compute.v20xx_yy_zz.compute_management_client` to
    `azure.mgmt.compute.v20xx_yy_zz`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.compute.v20xx_yy_zz.models.my_class`
    (import from `azure.mgmt.compute.v20xx_yy_zz.models` works like
    before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.compute.v20xx_yy_zz.operations.my_class_operations`
    (import from `azure.mgmt.compute.v20xx_yy_zz.operations` works
    like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 1.0.1 (2018-02-21)

  - usage_aggregation.quantity is now correctly declared as float
  - All operation groups have now a "models" attribute

## 1.0.0 (2017-06-23)

  - Initial stable release

This wheel package is now built with the azure wheel extension

If moved from 0.30.0rc6, expect some tiny renaming like (not
exhaustive):

  - reportedstart_time renamed to reported_start_time
  - self.Name renamed to self.name in some classes
