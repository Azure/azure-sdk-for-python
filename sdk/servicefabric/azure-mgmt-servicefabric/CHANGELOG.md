# Release History

## 2.0.0 (2021-09-02)

**Features**

  - Model NodeTypeDescription has a new parameter multiple_availability_zones
  - Model NodeTypeDescription has a new parameter is_stateless
  - Model ApplicationResource has a new parameter system_data
  - Model ApplicationResourceUpdate has a new parameter system_data
  - Model Cluster has a new parameter wave_upgrade_paused
  - Model Cluster has a new parameter system_data
  - Model Cluster has a new parameter upgrade_pause_end_timestamp_utc
  - Model Cluster has a new parameter notifications
  - Model Cluster has a new parameter sf_zonal_upgrade_mode
  - Model Cluster has a new parameter vmss_zonal_upgrade_mode
  - Model Cluster has a new parameter upgrade_pause_start_timestamp_utc
  - Model Cluster has a new parameter upgrade_wave
  - Model Cluster has a new parameter infrastructure_service_manager
  - Model ProxyResource has a new parameter system_data
  - Model OperationResult has a new parameter is_data_action
  - Model ApplicationTypeVersionResource has a new parameter system_data
  - Model ServiceResourceUpdate has a new parameter system_data
  - Model ClusterUpdateParameters has a new parameter wave_upgrade_paused
  - Model ClusterUpdateParameters has a new parameter upgrade_pause_end_timestamp_utc
  - Model ClusterUpdateParameters has a new parameter notifications
  - Model ClusterUpdateParameters has a new parameter sf_zonal_upgrade_mode
  - Model ClusterUpdateParameters has a new parameter vmss_zonal_upgrade_mode
  - Model ClusterUpdateParameters has a new parameter upgrade_pause_start_timestamp_utc
  - Model ClusterUpdateParameters has a new parameter upgrade_wave
  - Model ClusterUpdateParameters has a new parameter infrastructure_service_manager
  - Model ApplicationTypeResource has a new parameter system_data
  - Model Resource has a new parameter system_data
  - Model ServiceResource has a new parameter system_data
  - Model ApplicationUpgradePolicy has a new parameter recreate_application
  - Added operation ClustersOperations.list_upgradable_versions

**Breaking changes**

  - Removed operation group ManagedClusterVersionsOperations
  - Removed operation group ManagedclusterOperations
  - Removed operation group ManagedClustersOperations
  - Removed operation group ApplicationOperations
  - Removed operation group NodeTypesOperations
  - Removed operation group NodetypeOperations

## 1.0.0 (2021-06-03)

**Features**

  - Model ManagedCluster has a new parameter addon_features
  - Model ManagedClusterUpdateParameters has a new parameter addon_features
  - Added operation group ManagedclusterOperations
  - Added operation group ApplicationOperations
  - Added operation group NodetypeOperations

**Breaking changes**

  - Operation ApplicationTypesOperations.create_or_update has a new signature
  - Operation NodeTypesOperations.begin_delete_node has a new signature
  - Operation NodeTypesOperations.begin_reimage has a new signature
  - Operation NodeTypesOperations.begin_restart has a new signature
  - Operation NodeTypesOperations.begin_restart has a new signature
  - Operation NodeTypesOperations.begin_reimage has a new signature
  - Operation NodeTypesOperations.begin_delete_node has a new signature
  - Operation ApplicationTypesOperations.create_or_update has a new signature
  - Model ManagedCluster no longer has parameter cluster_upgrade_description
  - Model ManagedCluster no longer has parameter cluster_upgrade_mode
  - Model ManagedClusterUpdateParameters no longer has parameter cluster_upgrade_description
  - Model ManagedClusterUpdateParameters no longer has parameter cluster_upgrade_mode

## 1.0.0b1 (2020-12-02)

This is beta preview version.

This version uses a next-generation code generator that introduces important breaking changes, but also important new features (like unified authentication and async programming).

**General breaking changes**

- Credential system has been completly revamped:

  - `azure.common.credentials` or `msrestazure.azure_active_directory` instances are no longer supported, use the `azure-identity` classes instead: https://pypi.org/project/azure-identity/
  - `credentials` parameter has been renamed `credential`

- The `config` attribute no longer exists on a client, configuration should be passed as kwarg. Example: `MyClient(credential, subscription_id, enable_logging=True)`. For a complete set of
  supported options, see the [parameters accept in init documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)
- You can't import a `version` module anymore, use `__version__` instead
- Operations that used to return a `msrest.polling.LROPoller` now returns a `azure.core.polling.LROPoller` and are prefixed with `begin_`.
- Exceptions tree have been simplified and most exceptions are now `azure.core.exceptions.HttpResponseError` (`CloudError` has been removed).
- Most of the operation kwarg have changed. Some of the most noticeable:

  - `raw` has been removed. Equivalent feature can be found using `cls`, a callback that will give access to internal HTTP response for advanced user
  - For a complete set of
  supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core-tracing-opentelemetry) for an overview.

## 0.5.0 (2020-07-28)

**Features**

  - Model StatelessServiceProperties has a new parameter instance_close_delay_duration
  - Model StatelessServiceProperties has a new parameter service_dns_name
  - Model StatelessServiceUpdateProperties has a new parameter instance_close_delay_duration
  - Model ServiceResource has a new parameter service_dns_name
  - Model ServiceResourceProperties has a new parameter service_dns_name
  - Model Cluster has a new parameter application_type_versions_cleanup_policy
  - Model ApplicationResourceUpdate has a new parameter managed_identities
  - Model StatefulServiceProperties has a new parameter service_dns_name
  - Model ApplicationUpgradePolicy has a new parameter upgrade_mode
  - Model DiagnosticsStorageAccountConfig has a new parameter protected_account_key_name2
  - Model ApplicationResource has a new parameter identity
  - Model ApplicationResource has a new parameter managed_identities
  - Model ClusterUpdateParameters has a new parameter application_type_versions_cleanup_policy
  - Added operation group NodeTypesOperations
  - Added operation group ManagedClusterVersionsOperations
  - Added operation group ManagedClustersOperations

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
