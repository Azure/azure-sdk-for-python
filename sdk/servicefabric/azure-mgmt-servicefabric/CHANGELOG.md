# Release History

## 0.4.0 (2019-08-19)

**Features**

  - Added operation ClustersOperations.create_or_update
  - Added operation ServicesOperations.create_or_update
  - Added operation ApplicationsOperations.create_or_update
  - Added operation ApplicationTypesOperations.create_or_update
  - Added operation ApplicationTypeVersionsOperations.create_or_update

**Breaking changes**

  - Removed operation ClustersOperations.create
  - Removed operation ServicesOperations.create
  - Removed operation ApplicationsOperations.create
  - Removed operation ApplicationTypesOperations.create
  - Removed operation ApplicationTypeVersionsOperations.create

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes if from some import. In summary, some modules
were incorrectly visible/importable and have been renamed. This fixed
several issues caused by usage of classes that were not supposed to be
used in the first place.

  - ServiceFabricManagementClient cannot be imported from
    `azure.mgmt.servicefabric.service_fabric_management_client`
    anymore (import from `azure.mgmt.servicefabric` works like before)
  - ServiceFabricManagementClientConfiguration import has been moved
    from
    `azure.mgmt.servicefabric.service_fabric_management_client` to
    `azure.mgmt.servicefabric`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.servicefabric.models.my_class` (import
    from `azure.mgmt.servicefabric.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.servicefabric.operations.my_class_operations`
    (import from `azure.mgmt.servicefabric.operations` works like
    before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 0.3.0 (2019-05-30)

**Breaking changes**

  - Model ServiceTypeHealthPolicy has a new signature
  - Model ApplicationHealthPolicy has a new signature
  - Model ErrorModel has a new signature
  - Renamed operation group "application_type" to "application_types"
  - Renamed operation group "service" to "services"
  - Renamed operation group "application" to "applications"
  - Removed operation group "version"

**Features**

  - Add tags and etag attributes where supported
  - Model ClusterHealthPolicy has a new parameter
    application_health_policies
  - Model ClusterUpgradeDeltaHealthPolicy has a new parameter
    application_delta_health_policies
  - Model StatelessServiceProperties has a new parameter
    service_package_activation_mode
  - Model ServiceResource has a new parameter
    service_package_activation_mode
  - Model Cluster has a new parameter
    reverse_proxy_certificate_common_names
  - Model Cluster has a new parameter certificate_common_names
  - Model Cluster has a new parameter event_store_service_enabled
  - Model StatefulServiceProperties has a new parameter
    service_package_activation_mode
  - Model ClusterUpdateParameters has a new parameter
    certificate_common_names
  - Model ClusterUpdateParameters has a new parameter
    event_store_service_enabled

## 0.2.0 (2018-08-01)

  - New preview release, based on 2017-07-01-preview
  - Expect many breaking changes

## 0.1.0 (2017-08-24)

  - Initial preview release
