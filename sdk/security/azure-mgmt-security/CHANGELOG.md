# Release History

## 1.0.0 (2020-12-15)

**Bugfixes**

  - Fix unreasonable boolean enumeration type

## 1.0.0b1 (2020-11-02)

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

## 0.5.0 (2020-10-29)

**Features**

  - Model SecureScoreControlDetails has a new parameter weight
  - Model SecureScoreControlDetails has a new parameter percentage
  - Model SecureScoreItem has a new parameter weight
  - Model SecureScoreItem has a new parameter percentage
  - Model SecureScoreControlScore has a new parameter percentage
  - Added operation AlertsOperations.get_resource_group_level
  - Added operation AlertsOperations.get_subscription_level
  - Added operation AlertsOperations.update_resource_group_level_state_to_resolve
  - Added operation AlertsOperations.list_subscription_level_by_region
  - Added operation AlertsOperations.list_resource_group_level_by_region
  - Added operation AlertsOperations.update_subscription_level_state_to_resolve
  - Added operation AlertsOperations.update_subscription_level_state_to_dismiss
  - Added operation AlertsOperations.update_resource_group_level_state_to_dismiss
  - Added operation AlertsOperations.update_subscription_level_state_to_activate
  - Added operation AlertsOperations.update_resource_group_level_state_to_activate
  - Added operation group IotRecommendationTypesOperations
  - Added operation group ConnectorsOperations
  - Added operation group DeviceOperations
  - Added operation group DevicesForSubscriptionOperations
  - Added operation group IotDefenderSettingsOperations
  - Added operation group IotAlertsOperations
  - Added operation group DevicesForHubOperations
  - Added operation group IotSensorsOperations
  - Added operation group IotRecommendationsOperations
  - Added operation group SecuritySolutionsOperations
  - Added operation group SecuritySolutionsReferenceDataOperations
  - Added operation group OnPremiseIotSensorsOperations
  - Added operation group IotAlertTypesOperations

**Breaking changes**

  - Model Alert has a new signature
  - Removed operation AlertsOperations.list_subscription_level_alerts_by_region
  - Removed operation AlertsOperations.update_resource_group_level_alert_state_to_dismiss
  - Removed operation AlertsOperations.get_resource_group_level_alerts
  - Removed operation AlertsOperations.update_subscription_level_alert_state_to_reactivate
  - Removed operation AlertsOperations.get_subscription_level_alert
  - Removed operation AlertsOperations.list_resource_group_level_alerts_by_region
  - Removed operation AlertsOperations.update_resource_group_level_alert_state_to_reactivate
  - Removed operation AlertsOperations.update_subscription_level_alert_state_to_dismiss
  
## 0.4.1 (2020-06-12)

**Bugfixes**

  - skip url-encoding for resource id

## 0.4.0 (2020-06-05)

**Features**

  - Model IoTSecuritySolutionModel has a new parameter unmasked_ip_logging_status
  - Model InformationProtectionPolicy has a new parameter version
  - Model JitNetworkAccessRequest has a new parameter justification
  - Model SensitivityLabel has a new parameter description
  - Model SensitivityLabel has a new parameter rank
  - Model InformationType has a new parameter description
  - Model AppWhitelistingGroup has a new parameter protection_mode
  - Model JitNetworkAccessPolicyInitiateRequest has a new parameter justification
  - Model VmRecommendation has a new parameter enforcement_support
  - Model IoTSecurityAggregatedAlert has a new parameter top_devices_list
  - Added operation AdaptiveApplicationControlsOperations.delete
  - Added operation AlertsOperations.update_resource_group_level_alert_state_to_dismiss
  - Added operation AlertsOperations.update_subscription_level_alert_state_to_dismiss
  - Added operation AlertsOperations.update_subscription_level_alert_state_to_reactivate
  - Added operation AlertsOperations.update_resource_group_level_alert_state_to_reactivate
  - Added operation IotSecuritySolutionOperations.list_by_subscription
  - Added operation IotSecuritySolutionOperations.list_by_resource_group
  - Added operation IotSecuritySolutionOperations.create_or_update
  - Added operation group SecureScoreControlDefinitionsOperations
  - Added operation group AssessmentsMetadataOperations
  - Added operation group SecureScoreControlsOperations
  - Added operation group AlertsSuppressionRulesOperations
  - Added operation group IotSecuritySolutionsAnalyticsAggregatedAlertOperations
  - Added operation group SubAssessmentsOperations
  - Added operation group AutomationsOperations
  - Added operation group IotSecuritySolutionsAnalyticsRecommendationOperations
  - Added operation group SecureScoresOperations
  - Added operation group IotSecuritySolutionAnalyticsOperations
  - Added operation group AdaptiveNetworkHardeningsOperations
  - Added operation group AssessmentsOperations
  - Added operation group DeviceSecurityGroupsOperations

**Breaking changes**

  - Operation SettingsOperations.update has a new signature
  - Operation AlertsOperations.list has a new signature
  - Operation AlertsOperations.list_by_resource_group has a new signature
  - Operation AlertsOperations.list_resource_group_level_alerts_by_region has a new signature
  - Operation AlertsOperations.list_subscription_level_alerts_by_region has a new signature
  - Operation JitNetworkAccessPoliciesOperations.initiate has a new signature
  - Operation InformationProtectionPoliciesOperations.create_or_update has a new signature
  - Removed operation AlertsOperations.update_resource_group_level_alert_state
  - Removed operation AlertsOperations.update_subscription_level_alert_state
  - Removed operation IotSecuritySolutionOperations.create
  - Removed operation group IoTSecuritySolutionsResourceGroupOperations
  - Removed operation group IoTSecuritySolutionsAnalyticsRecommendationsOperations
  - Removed operation group IoTSecuritySolutionsAnalyticsRecommendationOperations
  - Removed operation group IoTSecuritySolutionsOperations
  - Removed operation group IoTSecuritySolutionsAnalyticsAggregatedAlertsOperations
  - Removed operation group IoTSecuritySolutionsAnalyticsAggregatedAlertOperations
  - Removed operation group IoTSecuritySolutionsAnalyticsOperations

## 0.3.0 (2019-08-01)

**Features**

  - Model JitNetworkAccessPolicyVirtualMachine has a new parameter
    public_ip_address
  - Model JitNetworkAccessRequestPort has a new parameter mapped_port
  - Added operation group RegulatoryComplianceControlsOperations
  - Added operation group ComplianceResultsOperations
  - Added operation group ServerVulnerabilityAssessmentOperations
  - Added operation group IoTSecuritySolutionsResourceGroupOperations
  - Added operation group AdaptiveApplicationControlsOperations
  - Added operation group IoTSecuritySolutionsOperations
  - Added operation group IotSecuritySolutionOperations
  - Added operation group RegulatoryComplianceStandardsOperations
  - Added operation group IoTSecuritySolutionsAnalyticsOperations
  - Added operation group
    IoTSecuritySolutionsAnalyticsAggregatedAlertOperations
  - Added operation group
    IoTSecuritySolutionsAnalyticsRecommendationsOperations
  - Added operation group RegulatoryComplianceAssessmentsOperations
  - Added operation group
    IoTSecuritySolutionsAnalyticsRecommendationOperations
  - Added operation group
    IoTSecuritySolutionsAnalyticsAggregatedAlertsOperations

**General breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes if from some import. In summary, some modules
were incorrectly visible/importable and have been renamed. This fixed
several issues caused by usage of classes that were not supposed to be
used in the first place.

  - SecurityCenter cannot be imported from
    `azure.mgmt.security.security_center` anymore (import from
    `azure.mgmt.security` works like before)
  - SecurityCenterConfiguration import has been moved from
    `azure.mgmt.security.security_center` to `azure.mgmt.security`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.security.models.my_class` (import from
    `azure.mgmt.security.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.security.operations.my_class_operations` (import
    from `azure.mgmt.security.operations` works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 0.2.0 (2019-04-16)

**Features**

  - Model Pricing has a new parameter free_trial_remaining_time
  - Model Alert has a new parameter is_incident
  - Added operation PricingsOperations.get
  - Added operation PricingsOperations.update
  - Added operation group AllowedConnectionsOperations

**Breaking changes**

  - Operation SettingsOperations.update has a new signature
  - Removed operation PricingsOperations.update_subscription_pricing
  - Removed operation PricingsOperations.list_by_resource_group
  - Removed operation
    PricingsOperations.create_or_update_resource_group_pricing
  - Removed operation PricingsOperations.get_resource_group_pricing
  - Removed operation PricingsOperations.get_subscription_pricing

## 0.1.0 (2018-10-29)

  - Initial Release
