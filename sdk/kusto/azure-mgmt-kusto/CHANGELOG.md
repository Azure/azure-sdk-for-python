# Release History

## 4.0.0b1 (2026-06-02)

### Features Added

  - Client `KustoManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `KustoManagementClient` added method `send_request`
  - Model `AttachedDatabaseConfiguration` added property `system_data`
  - Model `AttachedDatabaseConfigurationsCheckNameRequest` added property `type`
  - Model `ClusterCheckNameRequest` added property `type`
  - Model `ClusterPrincipalAssignment` added property `system_data`
  - Model `ClusterPrincipalAssignmentCheckNameRequest` added property `type`
  - Model `ClusterUpdate` added property `system_data`
  - Model `CosmosDbDataConnection` added property `system_data`
  - Model `DataConnection` added property `system_data`
  - Model `DataConnectionCheckNameRequest` added property `type`
  - Enum `DataConnectionKind` added member `EVENT_GRID_WITH_MANAGED_IDENTITY`
  - Enum `DataConnectionKind` added member `EVENT_HUB_WITH_MANAGED_IDENTITY`
  - Model `Database` added property `system_data`
  - Model `DatabasePrincipalAssignment` added property `system_data`
  - Model `DatabasePrincipalAssignmentCheckNameRequest` added property `type`
  - Model `DatabasePrincipalListResult` added property `next_link`
  - Model `EventGridDataConnection` added property `system_data`
  - Enum `EventGridDataFormat` added member `AZMONSTREAM`
  - Model `EventHubDataConnection` added property `system_data`
  - Enum `EventHubDataFormat` added member `AZMONSTREAM`
  - Model `IotHubDataConnection` added property `system_data`
  - Enum `IotHubDataFormat` added member `AZMONSTREAM`
  - Model `KeyVaultProperties` added property `federated_identity_client_id`
  - Model `LanguageExtensionsList` added property `next_link`
  - Model `ManagedPrivateEndpointsCheckNameRequest` added property `type`
  - Model `OperationResult` added property `error`
  - Model `OutboundNetworkDependenciesEndpoint` added property `system_data`
  - Model `ProxyResource` added property `system_data`
  - Enum `PublicNetworkAccess` added member `SECURED_BY_PERIMETER`
  - Model `ReadOnlyFollowingDatabase` added property `system_data`
  - Model `ReadWriteDatabase` added property `system_data`
  - Model `Resource` added property `system_data`
  - Model `SandboxCustomImage` added property `system_data`
  - Model `SandboxCustomImagesCheckNameRequest` added property `type`
  - Model `ScriptCheckNameRequest` added property `type`
  - Model `TrackedResource` added property `system_data`
  - Added model `EventGridConnectionWithManagedIdentityProperties`
  - Added model `EventGridDataConnectionWithManagedIdentity`
  - Added model `EventHubConnectionWithManagedIdentityProperties`
  - Added model `EventHubDataConnectionWithManagedIdentity`
  - Added model `OperationResultErrorProperties`

### Breaking Changes

  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - Model `ClusterPrincipalAssignment` moved instance variable `principal_id`, `role`, `tenant_id`, `principal_type`, `tenant_name`, `principal_name`, `provisioning_state` and `aad_object_id` under property `properties` whose type is `ClusterPrincipalProperties`
  - Model `ClusterUpdate` moved instance variable `state`, `provisioning_state`, `uri`, `data_ingestion_uri`, `state_reason`, `trusted_external_tenants`, `optimized_autoscale`, `enable_disk_encryption`, `enable_streaming_ingest`, `virtual_network_configuration`, `key_vault_properties`, `enable_purge`, `language_extensions`, `enable_double_encryption`, `public_network_access`, `allowed_ip_range_list`, `engine_type`, `accepted_audiences`, `enable_auto_stop`, `restrict_outbound_network_access`, `allowed_fqdn_list`, `callout_policies`, `public_ip_type`, `virtual_cluster_graduation_properties`, `private_endpoint_connections`, `migration_cluster` and `zone_status` under property `properties` whose type is `ClusterProperties`
  - Model `DatabasePrincipalAssignment` moved instance variable `principal_id`, `role`, `tenant_id`, `principal_type`, `tenant_name`, `principal_name`, `provisioning_state` and `aad_object_id` under property `properties` whose type is `DatabasePrincipalProperties`
  - Model `EventGridDataConnection` moved instance variable `storage_account_resource_id`, `event_grid_resource_id`, `event_hub_resource_id`, `consumer_group`, `table_name`, `mapping_rule_name`, `data_format`, `ignore_first_record`, `blob_storage_event_type`, `managed_identity_resource_id`, `managed_identity_object_id`, `database_routing` and `provisioning_state` under property `properties` whose type is `EventGridConnectionProperties`
  - Model `EventHubDataConnection` moved instance variable `event_hub_resource_id`, `consumer_group`, `table_name`, `mapping_rule_name`, `data_format`, `event_system_properties`, `compression`, `provisioning_state`, `managed_identity_resource_id`, `managed_identity_object_id`, `database_routing` and `retrieval_start_date` under property `properties` whose type is `EventHubConnectionProperties`
  - Model `FollowerDatabaseDefinitionGet` moved instance variable `cluster_resource_id`, `attached_database_configuration_name`, `database_name`, `table_level_sharing_properties` and `database_share_origin` under property `properties` whose type is `FollowerDatabaseProperties`
  - Model `IotHubDataConnection` moved instance variable `iot_hub_resource_id`, `consumer_group`, `table_name`, `mapping_rule_name`, `data_format`, `event_system_properties`, `shared_access_policy_name`, `database_routing`, `retrieval_start_date` and `provisioning_state` under property `properties` whose type is `IotHubConnectionProperties`
  - Method `ClustersOperations.begin_create_or_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `ClustersOperations.begin_update` replaced positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`
  - Parameter `caller_role` of `DatabasesOperations.begin_create_or_update` is now optional
  - Method `DatabasesOperations.begin_create_or_update` changed its parameter `caller_role` from `positional_or_keyword` to `keyword_only`
  - Parameter `caller_role` of `DatabasesOperations.begin_update` is now optional
  - Method `DatabasesOperations.begin_update` changed its parameter `caller_role` from `positional_or_keyword` to `keyword_only`
  - Method `DatabasesOperations.list_by_cluster` changed its parameter `skiptoken` from `positional_or_keyword` to `keyword_only`

### Other Changes

  - Deleted model `FollowerDatabaseListResultGet`/`ListResourceSkusResult`/`SkuDescriptionList` which actually were not used by SDK users

## 3.4.0 (2024-01-24)

### Features Added

  - Model `Cluster` added property `callout_policies`
  - Model `Cluster` added property `zone_status`
  - Enum `ClusterPrincipalRole` added member `ALL_DATABASES_MONITOR`
  - Model `ClusterUpdate` added property `callout_policies`
  - Model `ClusterUpdate` added property `zone_status`
  - Enum `LanguageExtensionImageName` added member `PYTHON3_11_7`
  - Enum `LanguageExtensionImageName` added member `PYTHON3_11_7_DL`
  - Model `SandboxCustomImage` added property `base_image_name`
  - Model `Script` added property `script_level`
  - Model `Script` added property `principal_permissions_action`
  - Added model `CalloutPoliciesList`
  - Added model `CalloutPolicy`
  - Added model `CalloutPolicyToRemove`
  - Added enum `CalloutType`
  - Added model `FollowerDatabaseDefinitionGet`
  - Added model `FollowerDatabaseListResultGet`
  - Added enum `OutboundAccess`
  - Added enum `PrincipalPermissionsAction`
  - Added enum `ScriptLevel`
  - Added enum `ZoneStatus`
  - Model `ClustersOperations` added method `begin_add_callout_policies`
  - Model `ClustersOperations` added method `begin_remove_callout_policy`
  - Model `ClustersOperations` added method `list_callout_policies`
  - Model `ClustersOperations` added method `list_follower_databases_get`

## 3.3.0 (2023-10-23)

### Features Added

  - Added operation group SandboxCustomImagesOperations
  - Model ClusterUpdate has a new parameter zones
  - Model EndpointDetail has a new parameter ip_address
  - Model LanguageExtension has a new parameter language_extension_custom_image_name
  - Model VirtualNetworkConfiguration has a new parameter state

## 3.2.0 (2023-07-21)

### Features Added

  - Added operation ClustersOperations.begin_migrate
  - Added operation group DatabaseOperations
  - Model Cluster has a new parameter migration_cluster
  - Model ClusterUpdate has a new parameter migration_cluster
  - Model DatabaseListResult has a new parameter next_link
  - Model ReadOnlyFollowingDatabase has a new parameter suspension_details
  - Model ReadWriteDatabase has a new parameter key_vault_properties
  - Model ReadWriteDatabase has a new parameter suspension_details
  - Operation DatabasesOperations.list_by_cluster has a new optional parameter skiptoken
  - Operation DatabasesOperations.list_by_cluster has a new optional parameter top

## 3.1.0 (2023-02-15)

### Features Added

  - Added operation group SkusOperations
  - Model LanguageExtension has a new parameter language_extension_image_name
  - Model SkuLocationInfoItem has a new parameter zone_details
  - Model TableLevelSharingProperties has a new parameter functions_to_exclude
  - Model TableLevelSharingProperties has a new parameter functions_to_include

## 3.1.0b1 (2022-12-27)

### Features Added

  - Added operation group SkusOperations
  - Model LanguageExtension has a new parameter language_extension_image_name
  - Model SkuLocationInfoItem has a new parameter zone_details

## 3.0.0 (2022-09-15)

### Features Added

  - Model AttachedDatabaseConfiguration has a new parameter database_name_override
  - Model AttachedDatabaseConfiguration has a new parameter database_name_prefix
  - Model EventHubDataConnection has a new parameter retrieval_start_date
  - Model FollowerDatabaseDefinition has a new parameter database_share_origin
  - Model FollowerDatabaseDefinition has a new parameter table_level_sharing_properties
  - Model IotHubDataConnection has a new parameter retrieval_start_date
  - Model ReadOnlyFollowingDatabase has a new parameter database_share_origin
  - Model ReadOnlyFollowingDatabase has a new parameter original_database_name
  - Model ReadOnlyFollowingDatabase has a new parameter table_level_sharing_properties

### Breaking Changes

  - Operation DatabasesOperations.begin_create_or_update has a new parameter caller_role
  - Operation DatabasesOperations.begin_update has a new parameter caller_role

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
