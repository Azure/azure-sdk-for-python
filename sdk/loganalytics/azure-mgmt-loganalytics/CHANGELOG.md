# Release History

## 0.0.0 (it should be perview) (2022-07-06)



## 13.0.0b5 (2022-07-06)

**Features**

  - Model.DataSourceType has a new enum type `INGESTION`

## 13.0.0b4 (2022-04-08)

**Fixes**

  - Reverted change about client name

## 13.0.0b3 (2022-04-07)

**Features**

  - Added operation group QueriesOperations
  - Added operation group QueryPacksOperations

## 13.0.0b2 (2022-02-14)

**Features**

  - Added operation TablesOperations.migrate

## 13.0.0b1 (2022-01-18)

**Features**

  - Added operation TablesOperations.begin_create_or_update
  - Added operation TablesOperations.begin_delete
  - Added operation TablesOperations.begin_update
  - Model Table has a new parameter archive_retention_in_days
  - Model Table has a new parameter last_plan_modified_date
  - Model Table has a new parameter plan
  - Model Table has a new parameter provisioning_state
  - Model Table has a new parameter restored_logs
  - Model Table has a new parameter result_statistics
  - Model Table has a new parameter schema
  - Model Table has a new parameter search_results
  - Model Table has a new parameter system_data
  - Model Table has a new parameter total_retention_in_days
  - Model Workspace has a new parameter default_data_collection_rule_resource_id
  - Model Workspace has a new parameter system_data
  - Model WorkspacePatch has a new parameter default_data_collection_rule_resource_id

**Breaking changes**

  - Model Table no longer has parameter is_troubleshoot_enabled
  - Model Table no longer has parameter is_troubleshooting_allowed
  - Model Table no longer has parameter last_troubleshoot_date
  - Removed operation TablesOperations.create
  - Removed operation TablesOperations.update

## 12.0.0 (2021-11-16)

**Features**

  - Model Table has a new parameter is_troubleshooting_allowed
  - Model Table has a new parameter last_troubleshoot_date
  - Model Table has a new parameter is_troubleshoot_enabled
  - Added operation TablesOperations.create
  - Added operation ClustersOperations.begin_update

**Breaking changes**

  - Removed operation ClustersOperations.update

## 11.0.0 (2021-07-12)

**Features**

  - Model ClusterPatch has a new parameter billing_type
  - Model Workspace has a new parameter features
  - Model WorkspacePatch has a new parameter features
  - Model WorkspaceFeatures has a new parameter disable_local_auth

**Breaking changes**

  - Model Workspace no longer has parameter immediate_purge_data_on30_days
  - Model Workspace no longer has parameter enable_log_access_using_only_resource_permissions
  - Model Workspace no longer has parameter cluster_resource_id
  - Model Workspace no longer has parameter enable_data_export
  - Model WorkspacePatch no longer has parameter immediate_purge_data_on30_days
  - Model WorkspacePatch no longer has parameter enable_log_access_using_only_resource_permissions
  - Model WorkspacePatch no longer has parameter cluster_resource_id
  - Model WorkspacePatch no longer has parameter enable_data_export
  - Model CapacityReservationProperties no longer has parameter max_capacity

## 10.0.0 (2021-05-13)

**Features**

  - Model WorkspacePatch has a new parameter cluster_resource_id
  - Model WorkspacePatch has a new parameter immediate_purge_data_on30_days
  - Model WorkspacePatch has a new parameter enable_data_export
  - Model WorkspacePatch has a new parameter enable_log_access_using_only_resource_permissions
  - Model Workspace has a new parameter cluster_resource_id
  - Model Workspace has a new parameter immediate_purge_data_on30_days
  - Model Workspace has a new parameter enable_data_export
  - Model Workspace has a new parameter enable_log_access_using_only_resource_permissions

**Breaking changes**

  - Model WorkspacePatch no longer has parameter features
  - Model Table no longer has parameter is_troubleshooting_allowed
  - Model Table no longer has parameter is_troubleshoot_enabled
  - Model Table no longer has parameter last_troubleshoot_date
  - Model WorkspaceSku no longer has parameter max_capacity_reservation_level
  - Model Workspace no longer has parameter features

## 9.0.0 (2021-04-06)

**Features**

  - Model WorkspacePatch has a new parameter created_date
  - Model WorkspacePatch has a new parameter features
  - Model WorkspacePatch has a new parameter modified_date
  - Model WorkspacePatch has a new parameter force_cmk_for_query
  - Model Cluster has a new parameter last_modified_date
  - Model Cluster has a new parameter billing_type
  - Model Cluster has a new parameter is_double_encryption_enabled
  - Model Cluster has a new parameter is_availability_zones_enabled
  - Model Cluster has a new parameter created_date
  - Model Cluster has a new parameter capacity_reservation_properties
  - Model Cluster has a new parameter associated_workspaces
  - Model Table has a new parameter is_troubleshooting_allowed
  - Model Table has a new parameter last_troubleshoot_date
  - Model Table has a new parameter is_troubleshoot_enabled
  - Model Identity has a new parameter user_assigned_identities
  - Model ClusterPatch has a new parameter identity
  - Model KeyVaultProperties has a new parameter key_rsa_size
  - Model Workspace has a new parameter created_date
  - Model Workspace has a new parameter features
  - Model Workspace has a new parameter modified_date
  - Model Workspace has a new parameter force_cmk_for_query

**Breaking changes**

  - Model Cluster no longer has parameter next_link
  - Model ErrorResponse has a new signature

## 8.0.0 (2020-12-25)

**Breaking changes**

  - Change client name from OperationalInsightsManagementClient to LogAnalyticsManagementClient

## 7.0.0 (2020-12-17)

- GA release

## 7.0.0b1 (2020-11-16)

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

## 2.0.0(2020-11-09)

**Breaking changes**

  - Model DataExport no longer has parameter all_tables

## 1.0.0 (2020-08-31)

**Features**

  - REST call api-version changes from 2020-03-01-preview to 2020-08-01
  - DataSourceType has new enum values

## 0.7.0 (2020-07-09)

**Features**

  - Model DataSource has a new parameter etag
  - Model SavedSearch has a new parameter etag

**Breaking changes**

  - Model DataSource no longer has parameter e_tag
  - Model SavedSearch no longer has parameter e_tag

## 0.6.0 (2020-05-28)

**Features**

  - Model SavedSearch has a new parameter function_parameters
  - Model SavedSearch has a new parameter function_alias
  - Model WorkspacePatch has a new parameter workspace_capping
  - Model Workspace has a new parameter workspace_capping
  - Added operation group AvailableServiceTiersOperations
  - Added operation group TablesOperations
  - Added operation group DeletedWorkspacesOperations

**Breaking changes**

  - Operation WorkspacesOperations.delete has a new signature
  - Removed operation WorkspacesOperations.available_service_tiers
  - Model WorkspaceSku has a new signature

## 0.5.0 (2020-04-22)

**Breaking changes**

  - Reverted client name back to LogAnalyticsManagementClient as previous change was not intentional

## 0.4.0 (2020-04-20)

**Features**

  - Model LinkedService has a new parameter provisioning_state
  - Added operation WorkspacesOperations.available_service_tiers
  - Added operation group ManagementGroupsOperations
  - Added operation group GatewaysOperations
  - Added operation group OperationStatusesOperations
  - Added operation group SchemaOperations
  - Added operation group WorkspacePurgeOperations
  - Added operation group UsagesOperations
  - Added operation group SharedKeysOperations
  - Added operation group StorageInsightConfigsOperations
  - Added operation group IntelligencePacksOperations

**Breaking changes**

  - Removed operation WorkspacesOperations.list_usages
  - Removed operation WorkspacesOperations.get_shared_keys
  - Removed operation WorkspacesOperations.disable_intelligence_pack
  - Removed operation WorkspacesOperations.list_intelligence_packs
  - Removed operation WorkspacesOperations.list_management_groups
  - Removed operation WorkspacesOperations.enable_intelligence_pack
  - Removed operation group StorageInsightsOperations
  - Removed operation group OperationalInsightsManagementClientOperationsMixin

## 0.3.0 (2020-04-08)

**Features**

  - Model OperationDisplay has a new parameter description
  - Model LinkedService has a new parameter write_access_resource_id
  - Model Workspace has a new parameter public_network_access_for_ingestion
  - Model Workspace has a new parameter public_network_access_for_query
  - Model Workspace has a new parameter private_link_scoped_resources
  - Added operation group DataExportsOperations
  - Added operation group LinkedStorageAccountsOperations
  - Added operation group OperationalInsightsManagementClientOperationsMixin
  - Added operation group ClustersOperations

**Breaking changes**

  - Parameter location of model Workspace is now required
  - Operation LinkedServicesOperations.create_or_update has a new signature
  - Operation SavedSearchesOperations.delete has a new signature
  - Operation SavedSearchesOperations.create_or_update has a new signature
  - Operation SavedSearchesOperations.get has a new signature
  - Operation LinkedServicesOperations.create_or_update has a new signature
  - Model ProxyResource no longer has parameter tags
  - Model SavedSearchesListResult no longer has parameter metadata
  - Model Resource no longer has parameter location
  - Model Resource no longer has parameter tags
  - Model Workspace no longer has parameter source
  - Model Workspace no longer has parameter portal_url
  - Removed operation WorkspacesOperations.purge
  - Removed operation WorkspacesOperations.get_search_results
  - Removed operation WorkspacesOperations.list_link_targets
  - Removed operation WorkspacesOperations.get_schema
  - Removed operation WorkspacesOperations.update_search_results

**General Breaking Changes**

This version uses a next-generation code generator that *might*
introduce breaking changes. In summary, some modules were incorrectly
visible/importable and have been renamed. This fixed several issues
caused by usage of classes that were not supposed to be used in the
first place.

  - LogAnalyticsManagementClient cannot be imported from
    `azure.mgmt.loganalytics.log_analytics_management_client` anymore
    (import OperationalInsightsManagementClient from
    `azure.mgmt.loganalytics` works like before)
  - LogAnalyticsManagementClientConfiguration import has been moved from
    `azure.mgmt.loganalytics.log_analytics_management_client` to `azure.mgmt.loganalytics`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.loganalytics.models.my_class` (import from
    `azure.mgmt.loganalytics.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.loganalytics.operations.my_class_operations` (import from
    `azure.mgmt.loganalytics.operations` works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 0.2.0 (2018-05-29)

**Features**

  - Model IntelligencePack has a new parameter display_name
  - Model SavedSearch has a new parameter name
  - Model SavedSearch has a new parameter type
  - Added operation WorkspacesOperations.purge
  - Added operation WorkspacesOperations.update
  - Added operation group Operations
  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance

**Breaking changes**

  - Model SavedSearch no longer has parameter etag (replaced by e_tag)
  - Model SearchMetadata no longer has parameter etag (replaced by
    e_tag)

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes.

  - Model signatures now use only keyword-argument syntax. All
    positional arguments must be re-written as keyword-arguments. To
    keep auto-completion in most cases, models are now generated for
    Python 2 and Python 3. Python 3 uses the "*" syntax for
    keyword-only arguments.
  - Enum types now use the "str" mixin (class AzureEnum(str, Enum)) to
    improve the behavior when unrecognized enum values are encountered.
    While this is not a breaking change, the distinctions are important,
    and are documented here:
    <https://docs.python.org/3/library/enum.html#others> At a glance:
      - "is" should not be used at all.
      - "format" will return the string value, where "%s" string
        formatting will return `NameOfEnum.stringvalue`. Format syntax
        should be prefered.
  - New Long Running Operation:
      - Return type changes from
        `msrestazure.azure_operation.AzureOperationPoller` to
        `msrest.polling.LROPoller`. External API is the same.
      - Return type is now **always** a `msrest.polling.LROPoller`,
        regardless of the optional parameters used.
      - The behavior has changed when using `raw=True`. Instead of
        returning the initial call result as `ClientRawResponse`,
        without polling, now this returns an LROPoller. After polling,
        the final resource will be returned as a `ClientRawResponse`.
      - New `polling` parameter. The default behavior is
        `Polling=True` which will poll using ARM algorithm. When
        `Polling=False`, the response of the initial call will be
        returned without polling.
      - `polling` parameter accepts instances of subclasses of
        `msrest.polling.PollingMethod`.
      - `add_done_callback` will no longer raise if called after
        polling is finished, but will instead execute the callback right
        away.

**Bugfixes**

  - Compatibility of the sdist with wheel 0.31.0

## 0.1.0 (2017-11-01)

  - Initial Release

Thank you to jmalobicky for his help testing the package.
