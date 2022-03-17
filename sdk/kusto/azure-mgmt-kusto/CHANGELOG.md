# Release History

## 2.2.0 (2022-02-22)

**Features**

  - Added operation group OperationsResultsLocationOperations
  - Model Cluster has a new parameter private_endpoint_connections
  - Model Cluster has a new parameter public_ip_type
  - Model Cluster has a new parameter virtual_cluster_graduation_properties
  - Model ClusterPrincipalAssignment has a new parameter aad_object_id
  - Model ClusterUpdate has a new parameter private_endpoint_connections
  - Model ClusterUpdate has a new parameter public_ip_type
  - Model ClusterUpdate has a new parameter virtual_cluster_graduation_properties
  - Model DatabasePrincipalAssignment has a new parameter aad_object_id
  - Model EventGridDataConnection has a new parameter database_routing
  - Model EventGridDataConnection has a new parameter event_grid_resource_id
  - Model EventGridDataConnection has a new parameter managed_identity_object_id
  - Model EventGridDataConnection has a new parameter managed_identity_resource_id
  - Model EventHubDataConnection has a new parameter database_routing
  - Model EventHubDataConnection has a new parameter managed_identity_object_id
  - Model IotHubDataConnection has a new parameter database_routing
  - Model OperationResult has a new parameter provisioning_state
  - Model Script has a new parameter script_content

## 2.1.0 (2021-09-22)

**Features**

  - Model Cluster has a new parameter accepted_audiences
  - Model Cluster has a new parameter allowed_fqdn_list
  - Model Cluster has a new parameter enable_auto_stop
  - Model Cluster has a new parameter allowed_ip_range_list
  - Model Cluster has a new parameter system_data
  - Model Cluster has a new parameter restrict_outbound_network_access
  - Model Cluster has a new parameter public_network_access
  - Model ClusterUpdate has a new parameter accepted_audiences
  - Model ClusterUpdate has a new parameter allowed_fqdn_list
  - Model ClusterUpdate has a new parameter enable_auto_stop
  - Model ClusterUpdate has a new parameter allowed_ip_range_list
  - Model ClusterUpdate has a new parameter restrict_outbound_network_access
  - Model ClusterUpdate has a new parameter public_network_access
  - Added operation AttachedDatabaseConfigurationsOperations.check_name_availability
  - Added operation ClustersOperations.list_outbound_network_dependencies_endpoints
  - Added operation group PrivateEndpointConnectionsOperations
  - Added operation group ManagedPrivateEndpointsOperations
  - Added operation group PrivateLinkResourcesOperations

## 2.0.0 (2021-04-26)

**Features**

  - Model EventHubDataConnection has a new parameter managed_identity_resource_id
  - Model Cluster has a new parameter etag
  - Model AttachedDatabaseConfiguration has a new parameter table_level_sharing_properties
  - Added operation group ScriptsOperations
  - Added operation group OperationsResultsOperations

**Breaking changes**

  - Operation ClustersOperations.begin_update has a new signature
  - Operation ClustersOperations.begin_create_or_update has a new signature

## 1.0.0 (2021-02-04)

- GA release

## 1.0.0b1 (2020-11-30)

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

## 0.7.0 (2020-03-20)

**Features**

- Model ClusterUpdate has a new parameter enable_purge
- Model ClusterUpdate has a new parameter language_extensions
- Model Cluster has a new parameter enable_purge
- Model Cluster has a new parameter language_extensions
- Added operation ClustersOperations.add_language_extensions
- Added operation ClustersOperations.remove_language_extensions
- Added operation ClustersOperations.list_language_extensions

## 0.6.0 (2020-01-31)

**Features**

- Model Cluster has a new parameter state_reason
- Model ReadWriteDatabase has a new parameter is_followed
- Model EventHubDataConnection has a new parameter compression
- Model ClusterUpdate has a new parameter state_reason
- Added operation ClustersOperations.diagnose_virtual_network
- Added operation group DatabasePrincipalAssignmentsOperations
- Added operation group ClusterPrincipalAssignmentsOperations

## 0.5.0 (2019-11-11)

**Features**

  - Model ClusterUpdate has a new parameter key_vault_properties
  - Model ClusterUpdate has a new parameter identity
  - Model Cluster has a new parameter key_vault_properties
  - Model Cluster has a new parameter identity
  - Added operation ClustersOperations.detach_follower_databases
  - Added operation ClustersOperations.list_follower_databases
  - Added operation group AttachedDatabaseConfigurationsOperations

**Breaking changes**

  - Operation DatabasesOperations.check_name_availability has a new
    signature
  - Model Database no longer has parameter soft_delete_period
  - Model Database no longer has parameter hot_cache_period
  - Model Database no longer has parameter statistics
  - Model Database no longer has parameter provisioning_state
  - Model Database has a new required parameter kind

## 0.4.0 (2019-08-27)

**Features**

  - Model Cluster has a new parameter enable_disk_encryption
  - Model Cluster has a new parameter zones
  - Model Cluster has a new parameter optimized_autoscale
  - Model Cluster has a new parameter virtual_network_configuration
  - Model Cluster has a new parameter enable_streaming_ingest
  - Model EventHubDataConnection has a new parameter
    event_system_properties
  - Model CheckNameResult has a new parameter reason
  - Model DatabasePrincipal has a new parameter tenant_name
  - Model ClusterUpdate has a new parameter enable_disk_encryption
  - Model ClusterUpdate has a new parameter optimized_autoscale
  - Model ClusterUpdate has a new parameter enable_streaming_ingest
  - Model ClusterUpdate has a new parameter
    virtual_network_configuration
  - Added operation DataConnectionsOperations.check_name_availability

**General breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes if from some import. In summary, some modules
were incorrectly visible/importable and have been renamed. This fixed
several issues caused by usage of classes that were not supposed to be
used in the first place.

  - KustoManagementClient cannot be imported from
    `azure.mgmt.kusto.kusto_management_client` anymore (import from
    `azure.mgmt.kusto` works like before)
  - KustoManagementClientConfiguration import has been moved from
    `azure.mgmt.kusto.kusto_management_client` to
    `azure.mgmt.kusto`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.kusto.models.my_class` (import from
    `azure.mgmt.kusto.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.kusto.operations.my_class_operations` (import from
    `azure.mgmt.kusto.operations` works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 0.3.0 (2019-02-06)

**Features**

  - Model DatabaseUpdate has a new parameter hot_cache_period
  - Model DatabaseUpdate has a new parameter soft_delete_period
  - Model Database has a new parameter hot_cache_period
  - Model Database has a new parameter soft_delete_period
  - Added operation group DataConnectionsOperations

**Breaking changes**

  - Model DatabaseUpdate no longer has parameter
    hot_cache_period_in_days
  - Model DatabaseUpdate no longer has parameter etag
  - Model DatabaseUpdate no longer has parameter
    soft_delete_period_in_days
  - Model Database no longer has parameter tags
  - Model Database no longer has parameter etag
  - Model Database no longer has parameter hot_cache_period_in_days
  - Model Database no longer has parameter
    soft_delete_period_in_days
  - Model Cluster no longer has parameter etag
  - Model ClusterUpdate no longer has parameter etag
  - Removed operation group EventHubConnectionsOperations

## 0.2.0 (2018-11-27)

**Features**

  - Model Cluster has a new parameter uri
  - Model Cluster has a new parameter state
  - Model Cluster has a new parameter data_ingestion_uri
  - Model Cluster has a new parameter trusted_external_tenants
  - Model DatabaseUpdate has a new parameter etag
  - Model DatabaseUpdate has a new parameter statistics
  - Model DatabaseUpdate has a new parameter
    hot_cache_period_in_days
  - Model Database has a new parameter statistics
  - Model Database has a new parameter hot_cache_period_in_days
  - Model ClusterUpdate has a new parameter uri
  - Model ClusterUpdate has a new parameter etag
  - Model ClusterUpdate has a new parameter state
  - Model ClusterUpdate has a new parameter sku
  - Model ClusterUpdate has a new parameter tags
  - Model ClusterUpdate has a new parameter data_ingestion_uri
  - Model ClusterUpdate has a new parameter trusted_external_tenants
  - Added operation DatabasesOperations.list_principals
  - Added operation DatabasesOperations.check_name_availability
  - Added operation DatabasesOperations.add_principals
  - Added operation DatabasesOperations.remove_principals
  - Added operation ClustersOperations.list_skus
  - Added operation ClustersOperations.list_skus_by_resource
  - Added operation ClustersOperations.start
  - Added operation ClustersOperations.check_name_availability
  - Added operation ClustersOperations.stop
  - Added operation group EventHubConnectionsOperations

**Breaking changes**

  - Operation DatabasesOperations.update has a new signature
  - Operation ClustersOperations.update has a new signature
  - Operation DatabasesOperations.update has a new signature
  - Operation ClustersOperations.create_or_update has a new signature
  - Model Cluster has a new required parameter sku

## 0.1.0 (2018-08-09)

  - Initial Release
