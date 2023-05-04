# Release History

## 6.0.1 (2023-05-04)

### Other Changes

  - Fixed annotation about namespace

## 6.0.0 (2023-03-20)

### Features Added

  - Added operation MetricDefinitionsOperations.list_at_subscription_scope
  - Added operation MetricsOperations.list_at_subscription_scope
  - Added operation MetricsOperations.list_at_subscription_scope_post
  - Added operation group AzureMonitorWorkspacesOperations
  - Added operation group MonitorOperationsOperations
  - Added operation group TenantActionGroupsOperations
  - Model AzureMonitorPrivateLinkScope has a new parameter system_data
  - Model Condition has a new parameter metric_name
  - Model DataCollectionEndpoint has a new parameter failover_configuration
  - Model DataCollectionEndpoint has a new parameter metadata
  - Model DataCollectionEndpoint has a new parameter metrics_ingestion
  - Model DataCollectionEndpoint has a new parameter private_link_scoped_resources
  - Model DataCollectionEndpointResource has a new parameter failover_configuration
  - Model DataCollectionEndpointResource has a new parameter identity
  - Model DataCollectionEndpointResource has a new parameter metadata
  - Model DataCollectionEndpointResource has a new parameter metrics_ingestion
  - Model DataCollectionEndpointResource has a new parameter private_link_scoped_resources
  - Model DataCollectionEndpointResourceProperties has a new parameter failover_configuration
  - Model DataCollectionEndpointResourceProperties has a new parameter metadata
  - Model DataCollectionEndpointResourceProperties has a new parameter metrics_ingestion
  - Model DataCollectionEndpointResourceProperties has a new parameter private_link_scoped_resources
  - Model DataCollectionRuleAssociationMetadata has a new parameter provisioned_by_resource_id
  - Model DataCollectionRuleDataSources has a new parameter data_imports
  - Model DataCollectionRuleDataSources has a new parameter platform_telemetry
  - Model DataCollectionRuleDataSources has a new parameter prometheus_forwarder
  - Model DataCollectionRuleDataSources has a new parameter windows_firewall_logs
  - Model DataCollectionRuleDestinations has a new parameter event_hubs
  - Model DataCollectionRuleDestinations has a new parameter event_hubs_direct
  - Model DataCollectionRuleDestinations has a new parameter monitoring_accounts
  - Model DataCollectionRuleDestinations has a new parameter storage_accounts
  - Model DataCollectionRuleDestinations has a new parameter storage_blobs_direct
  - Model DataCollectionRuleDestinations has a new parameter storage_tables_direct
  - Model DataCollectionRuleMetadata has a new parameter provisioned_by_resource_id
  - Model DataCollectionRuleResource has a new parameter identity
  - Model DataFlow has a new parameter built_in_transform
  - Model DataSourcesSpec has a new parameter data_imports
  - Model DataSourcesSpec has a new parameter platform_telemetry
  - Model DataSourcesSpec has a new parameter prometheus_forwarder
  - Model DataSourcesSpec has a new parameter windows_firewall_logs
  - Model DestinationsSpec has a new parameter event_hubs
  - Model DestinationsSpec has a new parameter event_hubs_direct
  - Model DestinationsSpec has a new parameter monitoring_accounts
  - Model DestinationsSpec has a new parameter storage_accounts
  - Model DestinationsSpec has a new parameter storage_blobs_direct
  - Model DestinationsSpec has a new parameter storage_tables_direct
  - Model Metadata has a new parameter provisioned_by_resource_id
  - Model Operation has a new parameter action_type
  - Model Operation has a new parameter origin
  - Model PrivateLinkResource has a new parameter required_zone_names
  - Model ResourceForUpdate has a new parameter identity
  - Model ScheduledQueryRuleResource has a new parameter auto_mitigate
  - Model ScheduledQueryRuleResource has a new parameter check_workspace_alerts_storage_configured
  - Model ScheduledQueryRuleResource has a new parameter identity
  - Model ScheduledQueryRuleResource has a new parameter is_workspace_alerts_storage_configured
  - Model ScheduledQueryRuleResource has a new parameter public_network_access
  - Model ScheduledQueryRuleResource has a new parameter rule_resolve_configuration
  - Model ScheduledQueryRuleResource has a new parameter skip_query_validation
  - Model ScheduledQueryRuleResource has a new parameter system_data
  - Model ScheduledQueryRuleResourceCollection has a new parameter next_link
  - Model ScheduledQueryRuleResourcePatch has a new parameter auto_mitigate
  - Model ScheduledQueryRuleResourcePatch has a new parameter check_workspace_alerts_storage_configured
  - Model ScheduledQueryRuleResourcePatch has a new parameter identity
  - Model ScheduledQueryRuleResourcePatch has a new parameter is_workspace_alerts_storage_configured
  - Model ScheduledQueryRuleResourcePatch has a new parameter public_network_access
  - Model ScheduledQueryRuleResourcePatch has a new parameter rule_resolve_configuration
  - Model ScheduledQueryRuleResourcePatch has a new parameter skip_query_validation
  - Model ScopedResource has a new parameter system_data
  - Operation MetricsOperations.list has a new optional parameter auto_adjust_timegrain
  - Operation MetricsOperations.list has a new optional parameter validate_dimensions

### Breaking Changes

  - Model AzureMonitorPrivateLinkScope has a new required parameter access_mode_settings
  - Model Operation no longer has parameter service_specification
  - Model OperationDisplay no longer has parameter publisher
  - Model PrivateEndpointConnectionListResult no longer has parameter next_link
  - Model PrivateLinkResourceListResult no longer has parameter next_link
  - Removed operation ActionGroupsOperations.begin_create_notifications_at_resource_group_level
  - Removed operation ActionGroupsOperations.begin_post_test_notifications
  - Removed operation ActionGroupsOperations.get_test_notifications
  - Removed operation ActionGroupsOperations.get_test_notifications_at_resource_group_level

## 5.0.1 (2022-09-30)

### Bugs Fixed
  
  - Fix paging problem about `api_version`

## 5.0.0 (2022-09-19)

### Features Added

  - Model Resource has a new parameter system_data
  - Model Resource has a new parameter tags

### Breaking Changes

  - Model Resource has a new required parameter location

## 4.0.1 (2022-08-02)

**Other Change**

  - Fix package structure

## 4.0.0 (2022-08-02)

**Features**

  - Added operation ActionGroupsOperations.begin_create_notifications_at_action_group_resource_level
  - Added operation ActionGroupsOperations.begin_create_notifications_at_resource_group_level
  - Added operation ActionGroupsOperations.get_test_notifications_at_action_group_resource_level
  - Added operation ActionGroupsOperations.get_test_notifications_at_resource_group_level

**Breaking changes**

  - Model ActionGroupResource no longer has parameter identity
  - Model ActionGroupResource no longer has parameter kind
  - Model AzureResource no longer has parameter identity
  - Model AzureResource no longer has parameter kind
  - Removed operation group BaselineOperations
  - Removed operation group MetricBaselineOperations

## 3.1.0 (2022-03-16)

**Features**

  - Added operation DataCollectionRuleAssociationsOperations.list_by_data_collection_endpoint
  - Model DataCollectionRule has a new parameter data_collection_endpoint_id
  - Model DataCollectionRule has a new parameter metadata
  - Model DataCollectionRule has a new parameter stream_declarations
  - Model DataCollectionRuleAssociation has a new parameter metadata
  - Model DataCollectionRuleAssociationProxyOnlyResource has a new parameter metadata
  - Model DataCollectionRuleAssociationProxyOnlyResourceProperties has a new parameter metadata
  - Model DataCollectionRuleDataSources has a new parameter iis_logs
  - Model DataCollectionRuleDataSources has a new parameter log_files
  - Model DataCollectionRuleResource has a new parameter data_collection_endpoint_id
  - Model DataCollectionRuleResource has a new parameter metadata
  - Model DataCollectionRuleResource has a new parameter stream_declarations
  - Model DataCollectionRuleResourceProperties has a new parameter data_collection_endpoint_id
  - Model DataCollectionRuleResourceProperties has a new parameter metadata
  - Model DataCollectionRuleResourceProperties has a new parameter stream_declarations
  - Model DataFlow has a new parameter output_stream
  - Model DataFlow has a new parameter transform_kql
  - Model DataSourcesSpec has a new parameter iis_logs
  - Model DataSourcesSpec has a new parameter log_files

## 3.0.0 (2021-11-05)

**Features**

  - Model LogAnalyticsDestination has a new parameter workspace_id
  - Model LogSettings has a new parameter category_group
  - Model Baseline has a new parameter timestamps
  - Model Baseline has a new parameter error_type
  - Model Baseline has a new parameter prediction_result_type
  - Model Metric has a new parameter error_message
  - Model Metric has a new parameter error_code
  - Model Metric has a new parameter display_description
  - Model ManagementGroupDiagnosticSettingsResource has a new parameter system_data
  - Model ManagementGroupDiagnosticSettingsResource has a new parameter marketplace_partner_id
  - Model DataCollectionRuleAssociationProxyOnlyResourceProperties has a new parameter data_collection_endpoint_id
  - Model SubscriptionDiagnosticSettingsResource has a new parameter system_data
  - Model SubscriptionDiagnosticSettingsResource has a new parameter marketplace_partner_id
  - Model TimeSeriesBaseline has a new parameter metadata_values
  - Model DataCollectionRuleAssociationProxyOnlyResource has a new parameter system_data
  - Model DataCollectionRuleAssociationProxyOnlyResource has a new parameter data_collection_endpoint_id
  - Model CalculateBaselineResponse has a new parameter internal_operation_id
  - Model CalculateBaselineResponse has a new parameter statistics
  - Model CalculateBaselineResponse has a new parameter error_type
  - Model DataCollectionRule has a new parameter immutable_id
  - Model AlertRuleResourcePatch has a new parameter provisioning_state
  - Model AlertRuleResourcePatch has a new parameter action
  - Model OperationDisplay has a new parameter description
  - Model OperationDisplay has a new parameter publisher
  - Model ManagementGroupLogSettings has a new parameter category_group
  - Model SubscriptionLogSettings has a new parameter category_group
  - Model DiagnosticSettingsCategoryResource has a new parameter system_data
  - Model DiagnosticSettingsCategoryResource has a new parameter category_groups
  - Model BaselineResponse has a new parameter internal_operation_id
  - Model BaselineResponse has a new parameter metdata
  - Model BaselineResponse has a new parameter error_type
  - Model BaselineResponse has a new parameter prediction_result_type
  - Model ActionGroupResource has a new parameter event_hub_receivers
  - Model ActionGroupResource has a new parameter kind
  - Model ActionGroupResource has a new parameter identity
  - Model AutoscaleSettingResource has a new parameter system_data
  - Model AutoscaleSettingResource has a new parameter predictive_autoscale_policy
  - Model AutoscaleSettingResource has a new parameter target_resource_location
  - Model ScheduledQueryRuleResourcePatch has a new parameter is_legacy_log_analytics_rule
  - Model ScheduledQueryRuleResourcePatch has a new parameter override_query_time_range
  - Model ScheduledQueryRuleResourcePatch has a new parameter display_name
  - Model ScheduledQueryRuleResourcePatch has a new parameter created_with_api_version
  - Model ExtensionDataSource has a new parameter input_data_sources
  - Model LogSearchRuleResource has a new parameter created_with_api_version
  - Model LogSearchRuleResource has a new parameter kind
  - Model LogSearchRuleResource has a new parameter auto_mitigate
  - Model LogSearchRuleResource has a new parameter display_name
  - Model LogSearchRuleResource has a new parameter etag
  - Model LogSearchRuleResource has a new parameter is_legacy_log_analytics_rule
  - Model AutoscaleSettingResourcePatch has a new parameter predictive_autoscale_policy
  - Model AutoscaleSettingResourcePatch has a new parameter target_resource_location
  - Model RuleDataSource has a new parameter resource_location
  - Model RuleDataSource has a new parameter metric_namespace
  - Model RuleDataSource has a new parameter legacy_resource_id
  - Model AlertRuleResource has a new parameter provisioning_state
  - Model AlertRuleResource has a new parameter action
  - Model Operation has a new parameter service_specification
  - Model Operation has a new parameter is_data_action
  - Model MetricDefinition has a new parameter metric_class
  - Model MetricDefinition has a new parameter category
  - Model MetricDefinition has a new parameter display_description
  - Model DataCollectionRuleAssociation has a new parameter data_collection_endpoint_id
  - Model MetricTrigger has a new parameter metric_resource_location
  - Model MetricTrigger has a new parameter divide_per_instance
  - Model MetricAlertResource has a new parameter is_migrated
  - Model RuleManagementEventDataSource has a new parameter resource_location
  - Model RuleManagementEventDataSource has a new parameter metric_namespace
  - Model RuleManagementEventDataSource has a new parameter legacy_resource_id
  - Model MetricAlertResourcePatch has a new parameter is_migrated
  - Model ScheduledQueryRuleResource has a new parameter created_with_api_version
  - Model ScheduledQueryRuleResource has a new parameter kind
  - Model ScheduledQueryRuleResource has a new parameter etag
  - Model ScheduledQueryRuleResource has a new parameter display_name
  - Model ScheduledQueryRuleResource has a new parameter is_legacy_log_analytics_rule
  - Model ScheduledQueryRuleResource has a new parameter override_query_time_range
  - Model RuleMetricDataSource has a new parameter resource_location
  - Model RuleMetricDataSource has a new parameter metric_namespace
  - Model RuleMetricDataSource has a new parameter legacy_resource_id
  - Model DiagnosticSettingsResource has a new parameter system_data
  - Model DiagnosticSettingsResource has a new parameter marketplace_partner_id
  - Model MetricNamespace has a new parameter classification
  - Model DataCollectionRuleResource has a new parameter system_data
  - Model DataCollectionRuleResource has a new parameter immutable_id
  - Model DataCollectionRuleResource has a new parameter kind
  - Model DataCollectionRuleResourceProperties has a new parameter immutable_id
  - Added operation ActionGroupsOperations.begin_post_test_notifications
  - Added operation ActionGroupsOperations.get_test_notifications
  - Added operation group PredictiveMetricOperations
  - Added operation group DataCollectionEndpointsOperations

**Breaking changes**

  - Parameter scopes of model MetricAlertResource is now required
  - Operation ActivityLogAlertsOperations.update has a new signature
  - Operation ActivityLogAlertsOperations.create_or_update has a new signature
  - Operation SubscriptionDiagnosticSettingsOperations.list has a new signature
  - Operation SubscriptionDiagnosticSettingsOperations.get has a new signature
  - Operation SubscriptionDiagnosticSettingsOperations.delete has a new signature
  - Operation SubscriptionDiagnosticSettingsOperations.create_or_update has a new signature
  - Model PerfCounterDataSource no longer has parameter scheduled_transfer_period
  - Model ManagementGroupDiagnosticSettingsResource no longer has parameter location
  - Model SubscriptionDiagnosticSettingsResource no longer has parameter location
  - Model TimeSeriesBaseline no longer has parameter metadata
  - Model ErrorResponse no longer has parameter target
  - Model ErrorResponse no longer has parameter details
  - Model ErrorResponse no longer has parameter additional_info
  - Model WindowsEventLogDataSource no longer has parameter scheduled_transfer_period
  - Model BaselineResponse no longer has parameter metadata


## 2.0.0 (2020-12-25)

**Breaking changes**

- Client name changed from MonitorClient to MonitorManagementClient

## 1.0.1 (2020-09-18)

**Bug fix**

  - Require azure-mgmt-core>=1.2.0 in setup.py

## 1.0.0 (2020-09-16)

**Features**

  - Model MultiMetricCriteria has a new parameter skip_metric_validation
  - Model DynamicMetricCriteria has a new parameter skip_metric_validation
  - Model MetricTrigger has a new parameter dimensions
  - Model MetricTrigger has a new parameter metric_namespace
  - Model MetricCriteria has a new parameter skip_metric_validation
  - Added operation group SubscriptionDiagnosticSettingsOperations
  - Added operation group ManagementGroupDiagnosticSettingsOperations

## 1.0.0b1 (2020-06-17)

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


## 0.10.0 (2020-06-08)

**Features**

  - Model WebtestLocationAvailabilityCriteria has a new parameter additional_properties
  - Added operation group SubscriptionDiagnosticSettingsOperations

**Breaking changes**

  - Model WebtestLocationAvailabilityCriteria has a new required parameter odatatype

## 0.9.0 (2020-04-09)

**Features**

  - Model AzureMonitorPrivateLinkScope has a new parameter private_endpoint_connections

**Breaking changes**

  - Operation PrivateLinkScopedResourcesOperations.create_or_update has a new signature
  - Model PrivateEndpointConnection no longer has parameter tags
  - Model PrivateLinkResource no longer has parameter tags
  - Model ScopedResource no longer has parameter tags
  - Model ProxyResource no longer has parameter tags
  - Operation PrivateEndpointConnectionsOperations.create_or_update has a new signature
  - Model ErrorResponse has a new signature

## 0.8.0 (2020-03-14)

**Features**

- Model DiagnosticSettingsResource has a new parameter log_analytics_destination_type
- Model ProxyResource has a new parameter tags
- Model MetricAlertAction has a new parameter web_hook_properties
- Added operation group PrivateEndpointConnectionsOperations
- Added operation group PrivateLinkScopedResourcesOperations
- Added operation group PrivateLinkScopeOperationStatusOperations
- Added operation group PrivateLinkResourcesOperations
- Added operation group PrivateLinkScopesOperations

**Breaking changes**

- Model MetricAlertAction no longer has parameter webhook_properties
- Model ErrorResponse has a new signature


## 0.7.0 (2019-06-24)

This package now support profiles as parameter for sovereign cloud
support

**Features**

  - Model MultiMetricCriteria has a new parameter metric_namespace
  - Model MultiMetricCriteria has a new parameter dimensions
  - Added operation group ServiceDiagnosticSettingsOperations
  - Added operation group GuestDiagnosticsSettingsOperations
  - Added operation group BaselinesOperations
  - Added operation group GuestDiagnosticsSettingsAssociationOperations
  - Added operation group BaselineOperations

**Breaking changes**

  - Operation MetricBaselineOperations.get has a new signature
  - Model MultiMetricCriteria has a new required parameter name
  - Model MultiMetricCriteria has a new required parameter
    time_aggregation
  - Model MultiMetricCriteria has a new required parameter metric_name
  - Model ArmRoleReceiver has a new required parameter
    use_common_alert_schema
  - Model LogicAppReceiver has a new required parameter
    use_common_alert_schema
  - Model AzureFunctionReceiver has a new required parameter
    use_common_alert_schema
  - Model EmailReceiver has a new required parameter
    use_common_alert_schema
  - Model AutomationRunbookReceiver has a new required parameter
    use_common_alert_schema
  - Model WebhookReceiver has a new signature

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes for some imports. In summary, some modules
were incorrectly visible/importable and have been renamed. This fixed
several issues caused by usage of classes that were not supposed to be
used in the first place.

  - MonitorManagementClient cannot be imported from
    `azure.mgmt.monitor.monitor_management_client` anymore (import
    from `azure.mgmt.monitor` works like before)
  - MonitorManagementClientConfiguration import has been moved from
    `azure.mgmt.monitor.monitor_management_client` to
    `azure.mgmt.monitor`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.monitor.models.my_class` (import from
    `azure.mgmt.monitor.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.monitor.operations.my_class_operations` (import from
    `azure.mgmt.monitor.operations` works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 0.6.0 (2018-03-06)

**Features**

  - Model MetricCriteria has a new parameter additional_properties
  - Model MetricAlertResource has a new parameter
    target_resource_region
  - Model MetricAlertResource has a new parameter target_resource_type
  - Model MetricAlertResourcePatch has a new parameter
    target_resource_region
  - Model MetricAlertResourcePatch has a new parameter
    target_resource_type
  - Model ActionGroupResource has a new parameter arm_role_receivers
  - Model DiagnosticSettingsResource has a new parameter
    service_bus_rule_id
  - Added operation AutoscaleSettingsOperations.list_by_subscription
  - Added operation AlertRulesOperations.list_by_subscription
  - Added operation group MetricNamespacesOperations
  - Added operation group VMInsightsOperations

**Breaking changes**

  - Model MetricCriteria has a new required parameter criterion_type

## 0.5.2 (2018-06-06)

**Features**

  - Model ActionGroupResource has a new parameter voice_receivers
  - Model ActionGroupResource has a new parameter
    azure_function_receivers
  - Model ActionGroupResource has a new parameter logic_app_receivers
  - Added operation group MetricAlertsOperations
  - Added operation group ScheduledQueryRulesOperations
  - Added operation group MetricAlertsStatusOperations

## 0.5.1 (2018-04-16)

**Bugfixes**

  - Fix some invalid models in Python 3
  - Compatibility of the sdist with wheel 0.31.0

## 0.5.0 (2017-03-19)

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

  - Fix invalid type of "top" in metrics.list operation

**Features**

  - New operation group metric_baseline
  - Add attribute action_group_resource itsm_receivers
  - Add operation action_groups.update
  - Add new parameter "metricnames" to metrics.list
  - Add new parameter "metricnamespace" to metrics.list
  - All operations group have now a "models" attribute

New ApiVersion version of metrics to 2018-01-01

## 0.4.0 (2017-10-25)

**Features**

  - Merge into this package the "azure-monitor" package including
    following operations groups
      - event categories
      - activity log
      - tenant activity log
      - metrics definitions
      - metrics
  - Adding new multi-dimensional metrics API

**Breaking changes**

  - Some exceptions have moved from CloudError to ErrorResponseException
  - "service_diagnostic_settings" renamed to "diagnostic_settings"
  - Update API version of "metrics". Migrating from "azure-monitor" to
    "metrics" here needs to be rewritten.

**Bug fixes**

  - Improving HTTP status code check for better exception

## 0.3.0 (2017-06-30)

**Features**

  - Add action_groups operation group
  - Add alert_rules.update method
  - Add autoscale_settings.update method
  - Add log_profiles.update method

**Breaking changes**

  - activity_log_alerts.update has now flatten parameters
    "tags/enabled"

## 0.2.1 (2017-04-26)

  - Removal of a REST endpoint not ready to release.

## 0.2.0 (2017-04-19)

  - Add ActivityLogAlerts and DiagnosticSettings
  - Minor improvements, might be breaking
  - This wheel package is now built with the azure wheel extension

## 0.1.0 (2017-02-16)

  - Initial Release
