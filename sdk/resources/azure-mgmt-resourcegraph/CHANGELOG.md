# Release History

## 2.0.0 (2019-06-19)

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes for some import. In summary, some modules
were incorrectly visible/importable and have been renamed. This fixed
several issues caused by usage of classes that were not supposed to be
used in the first place.

  - ResourceGraphClient cannot be imported from
    `azure.mgmt.resourcegraph.resource_graph_client` anymore (import
    from `azure.mgmt.resourcegraph` works like before)
  - ResourceGraphClientConfiguration import has been moved from
    `azure.mgmt.resourcegraph.resource_graph_client` to
    `azure.mgmt.resourcegraph`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.resourcegraph.models.my_class` (import
    from `azure.mgmt.resourcegraph.models` works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 1.1.0 (2019-06-11)

**Note**

This version was incorrectly released with breaking changes inside. You
should use 1.0 or directly move to 2.0 if want to follow semantic
versionning closely.

**Breaking changes**

  - Result format can be table or objectArray

## 1.0.0 (2019-03-28)

  - Increment the version to show it as GA version no change in the
    contract.

## 0.1.0 (2018-09-07)

  - Initial Release
