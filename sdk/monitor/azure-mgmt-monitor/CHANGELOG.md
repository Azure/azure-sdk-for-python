# Release History

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
  supported options, see the [parameters accept in init documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)
- You can't import a `version` module anymore, use `__version__` instead
- Operations that used to return a `msrest.polling.LROPoller` now returns a `azure.core.polling.LROPoller` and are prefixed with `begin_`.
- Exceptions tree have been simplified and most exceptions are now `azure.core.exceptions.HttpResponseError` (`CloudError` has been removed).
- Most of the operation kwarg have changed. Some of the most noticeable:

  - `raw` has been removed. Equivalent feature can be found using `cls`, a callback that will give access to internal HTTP response for advanced user
  - For a complete set of
  supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/core/azure-core-tracing-opentelemetry) for an overview.


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
