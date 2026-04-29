# Release History

## 1.1.0b6 (2026-04-29)

### Features Added

  - Client `PolicyInsightsClient` added method `send_request`
  - Model `FieldRestriction` added property `values_property`
  - Model `PendingField` added property `values_property`
  - Model `PolicyMetadata` added property `properties`
  - Model `PolicyMetadata` added property `system_data`
  - Model `Resource` added property `system_data`
  - Model `SlimPolicyMetadata` added property `properties`
  - Added model `AttestationsListForResourceGroupQueryOptions`
  - Added model `AttestationsListForResourceQueryOptions`
  - Added model `AttestationsListForSubscriptionQueryOptions`
  - Added model `ComponentPolicyStatesListQueryResultsForPolicyDefinitionQueryOptions`
  - Added model `ComponentPolicyStatesListQueryResultsForResourceGroupLevelPolicyAssignmentQueryOptions`
  - Added model `ComponentPolicyStatesListQueryResultsForResourceGroupQueryOptions`
  - Added model `ComponentPolicyStatesListQueryResultsForResourceQueryOptions`
  - Added model `ComponentPolicyStatesListQueryResultsForSubscriptionLevelPolicyAssignmentQueryOptions`
  - Added model `ComponentPolicyStatesListQueryResultsForSubscriptionQueryOptions`
  - Added model `PolicyEventsListQueryResultsForManagementGroupQueryOptions`
  - Added model `PolicyEventsListQueryResultsForPolicyDefinitionQueryOptions`
  - Added model `PolicyEventsListQueryResultsForPolicySetDefinitionQueryOptions`
  - Added model `PolicyEventsListQueryResultsForResourceGroupLevelPolicyAssignmentQueryOptions`
  - Added model `PolicyEventsListQueryResultsForResourceGroupQueryOptions`
  - Added model `PolicyEventsListQueryResultsForResourceQueryOptions`
  - Added model `PolicyEventsListQueryResultsForSubscriptionLevelPolicyAssignmentQueryOptions`
  - Added model `PolicyEventsListQueryResultsForSubscriptionQueryOptions`
  - Added model `PolicyMetadataListQueryOptions`
  - Added model `PolicyStatesListQueryResultsForManagementGroupQueryOptions`
  - Added model `PolicyStatesListQueryResultsForPolicyDefinitionQueryOptions`
  - Added model `PolicyStatesListQueryResultsForPolicySetDefinitionQueryOptions`
  - Added model `PolicyStatesListQueryResultsForResourceGroupLevelPolicyAssignmentQueryOptions`
  - Added model `PolicyStatesListQueryResultsForResourceGroupQueryOptions`
  - Added model `PolicyStatesListQueryResultsForResourceQueryOptions`
  - Added model `PolicyStatesListQueryResultsForSubscriptionLevelPolicyAssignmentQueryOptions`
  - Added model `PolicyStatesListQueryResultsForSubscriptionQueryOptions`
  - Added model `PolicyStatesSummarizeForManagementGroupQueryOptions`
  - Added model `PolicyStatesSummarizeForPolicyDefinitionQueryOptions`
  - Added model `PolicyStatesSummarizeForPolicySetDefinitionQueryOptions`
  - Added model `PolicyStatesSummarizeForResourceGroupLevelPolicyAssignmentQueryOptions`
  - Added model `PolicyStatesSummarizeForResourceGroupQueryOptions`
  - Added model `PolicyStatesSummarizeForResourceQueryOptions`
  - Added model `PolicyStatesSummarizeForSubscriptionLevelPolicyAssignmentQueryOptions`
  - Added model `PolicyStatesSummarizeForSubscriptionQueryOptions`
  - Added model `PolicyTrackedResourcesListQueryResultsForManagementGroupQueryOptions`
  - Added model `PolicyTrackedResourcesListQueryResultsForResourceGroupQueryOptions`
  - Added model `PolicyTrackedResourcesListQueryResultsForResourceQueryOptions`
  - Added model `PolicyTrackedResourcesListQueryResultsForSubscriptionQueryOptions`
  - Added model `ProxyResource`
  - Added model `RemediationsListDeploymentsAtManagementGroupQueryOptions`
  - Added model `RemediationsListDeploymentsAtResourceGroupQueryOptions`
  - Added model `RemediationsListDeploymentsAtResourceQueryOptions`
  - Added model `RemediationsListDeploymentsAtSubscriptionQueryOptions`
  - Added model `RemediationsListForManagementGroupQueryOptions`
  - Added model `RemediationsListForResourceGroupQueryOptions`
  - Added model `RemediationsListForResourceQueryOptions`
  - Added model `RemediationsListForSubscriptionQueryOptions`

### Breaking Changes

  - Model `FieldRestriction` deleted or renamed its instance variable `values`
  - Model `PendingField` deleted or renamed its instance variable `values`
  - Model `PolicyMetadata` deleted or renamed its instance variable `metadata_id`
  - Model `PolicyMetadata` deleted or renamed its instance variable `category`
  - Model `PolicyMetadata` deleted or renamed its instance variable `title`
  - Model `PolicyMetadata` deleted or renamed its instance variable `owner`
  - Model `PolicyMetadata` deleted or renamed its instance variable `additional_content_url`
  - Model `PolicyMetadata` deleted or renamed its instance variable `metadata`
  - Model `PolicyMetadata` deleted or renamed its instance variable `description`
  - Model `PolicyMetadata` deleted or renamed its instance variable `requirements`
  - Model `SlimPolicyMetadata` deleted or renamed its instance variable `metadata_id`
  - Model `SlimPolicyMetadata` deleted or renamed its instance variable `category`
  - Model `SlimPolicyMetadata` deleted or renamed its instance variable `title`
  - Model `SlimPolicyMetadata` deleted or renamed its instance variable `owner`
  - Model `SlimPolicyMetadata` deleted or renamed its instance variable `additional_content_url`
  - Model `SlimPolicyMetadata` deleted or renamed its instance variable `metadata`
  - Deleted or renamed model `ErrorDefinitionAutoGenerated`
  - Deleted or renamed model `ErrorDefinitionAutoGenerated2`
  - Deleted or renamed model `ErrorResponseAutoGenerated`
  - Deleted or renamed model `ErrorResponseAutoGenerated2`
  - Deleted or renamed model `PolicyEventsQueryResults`
  - Deleted or renamed model `PolicyMetadataCollection`
  - Deleted or renamed model `PolicyStatesQueryResults`
  - Deleted or renamed model `PolicyTrackedResourcesQueryResults`
  - Deleted or renamed model `QueryOptions`
  - Method `AttestationsOperations.list_for_resource` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `AttestationsOperations.list_for_resource_group` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `AttestationsOperations.list_for_subscription` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_policy_definition` deleted or renamed its parameter `top` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_policy_definition` deleted or renamed its parameter `order_by` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_policy_definition` deleted or renamed its parameter `select` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_policy_definition` deleted or renamed its parameter `from_parameter` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_policy_definition` deleted or renamed its parameter `to` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_policy_definition` deleted or renamed its parameter `filter` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_policy_definition` deleted or renamed its parameter `apply` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_resource` deleted or renamed its parameter `top` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_resource` deleted or renamed its parameter `order_by` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_resource` deleted or renamed its parameter `select` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_resource` deleted or renamed its parameter `from_parameter` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_resource` deleted or renamed its parameter `to` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_resource` deleted or renamed its parameter `filter` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_resource` deleted or renamed its parameter `apply` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_resource` deleted or renamed its parameter `expand` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_resource_group` deleted or renamed its parameter `top` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_resource_group` deleted or renamed its parameter `order_by` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_resource_group` deleted or renamed its parameter `select` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_resource_group` deleted or renamed its parameter `from_parameter` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_resource_group` deleted or renamed its parameter `to` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_resource_group` deleted or renamed its parameter `filter` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_resource_group` deleted or renamed its parameter `apply` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_resource_group_level_policy_assignment` deleted or renamed its parameter `top` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_resource_group_level_policy_assignment` deleted or renamed its parameter `order_by` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_resource_group_level_policy_assignment` deleted or renamed its parameter `select` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_resource_group_level_policy_assignment` deleted or renamed its parameter `from_parameter` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_resource_group_level_policy_assignment` deleted or renamed its parameter `to` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_resource_group_level_policy_assignment` deleted or renamed its parameter `filter` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_resource_group_level_policy_assignment` deleted or renamed its parameter `apply` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_subscription` deleted or renamed its parameter `top` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_subscription` deleted or renamed its parameter `order_by` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_subscription` deleted or renamed its parameter `select` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_subscription` deleted or renamed its parameter `from_parameter` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_subscription` deleted or renamed its parameter `to` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_subscription` deleted or renamed its parameter `filter` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_subscription` deleted or renamed its parameter `apply` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_subscription_level_policy_assignment` deleted or renamed its parameter `top` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_subscription_level_policy_assignment` deleted or renamed its parameter `order_by` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_subscription_level_policy_assignment` deleted or renamed its parameter `select` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_subscription_level_policy_assignment` deleted or renamed its parameter `from_parameter` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_subscription_level_policy_assignment` deleted or renamed its parameter `to` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_subscription_level_policy_assignment` deleted or renamed its parameter `filter` of kind `positional_or_keyword`
  - Method `ComponentPolicyStatesOperations.list_query_results_for_subscription_level_policy_assignment` deleted or renamed its parameter `apply` of kind `positional_or_keyword`
  - Method `PolicyEventsOperations.list_query_results_for_management_group` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `PolicyEventsOperations.list_query_results_for_policy_definition` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `PolicyEventsOperations.list_query_results_for_policy_set_definition` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `PolicyEventsOperations.list_query_results_for_resource` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `PolicyEventsOperations.list_query_results_for_resource_group` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `PolicyEventsOperations.list_query_results_for_resource_group_level_policy_assignment` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `PolicyEventsOperations.list_query_results_for_subscription` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `PolicyEventsOperations.list_query_results_for_subscription_level_policy_assignment` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `PolicyMetadataOperations.list` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `PolicyStatesOperations.list_query_results_for_management_group` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `PolicyStatesOperations.list_query_results_for_policy_definition` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `PolicyStatesOperations.list_query_results_for_policy_set_definition` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `PolicyStatesOperations.list_query_results_for_resource` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `PolicyStatesOperations.list_query_results_for_resource_group` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `PolicyStatesOperations.list_query_results_for_resource_group_level_policy_assignment` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `PolicyStatesOperations.list_query_results_for_subscription` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `PolicyStatesOperations.list_query_results_for_subscription_level_policy_assignment` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `PolicyStatesOperations.summarize_for_management_group` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `PolicyStatesOperations.summarize_for_policy_definition` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `PolicyStatesOperations.summarize_for_policy_set_definition` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `PolicyStatesOperations.summarize_for_resource` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `PolicyStatesOperations.summarize_for_resource_group` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `PolicyStatesOperations.summarize_for_resource_group_level_policy_assignment` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `PolicyStatesOperations.summarize_for_subscription` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `PolicyStatesOperations.summarize_for_subscription_level_policy_assignment` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `PolicyTrackedResourcesOperations.list_query_results_for_management_group` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `PolicyTrackedResourcesOperations.list_query_results_for_resource` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `PolicyTrackedResourcesOperations.list_query_results_for_resource_group` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `PolicyTrackedResourcesOperations.list_query_results_for_subscription` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `RemediationsOperations.list_deployments_at_management_group` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `RemediationsOperations.list_deployments_at_resource` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `RemediationsOperations.list_deployments_at_resource_group` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `RemediationsOperations.list_deployments_at_subscription` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `RemediationsOperations.list_for_management_group` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `RemediationsOperations.list_for_resource` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `RemediationsOperations.list_for_resource_group` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`
  - Method `RemediationsOperations.list_for_subscription` deleted or renamed its parameter `query_options` of kind `positional_or_keyword`

## 1.1.0b5 (2025-07-21)

### Features Added

  - Model `CheckRestrictionsRequest` added property `include_audit_effect`
  - Model `FieldRestriction` added property `policy_effect`
  - Model `FieldRestriction` added property `reason`
  - Enum `FieldRestrictionResult` added member `AUDIT`
  - Model `PolicyEvaluationResult` added property `effect_details`
  - Model `RemediationFilters` added property `resource_ids`
  - Added model `CheckRestrictionEvaluationDetails`
  - Added model `PolicyEffectDetails`

## 1.1.0b4 (2022-12-29)

### Features Added

  - Added operation group ComponentPolicyStatesOperations
  - Model Operation has a new parameter is_data_action

## 1.1.0b3 (2022-10-10)

### Features Added

  - Added operation PolicyRestrictionsOperations.check_at_management_group_scope
  - Model Attestation has a new parameter assessment_date
  - Model Attestation has a new parameter metadata

### Breaking Changes

  - Operation PolicyEventsOperations.list_query_results_for_management_group has a new parameter policy_events_resource
  - Operation PolicyEventsOperations.list_query_results_for_policy_definition has a new parameter policy_events_resource
  - Operation PolicyEventsOperations.list_query_results_for_policy_set_definition has a new parameter policy_events_resource
  - Operation PolicyEventsOperations.list_query_results_for_resource has a new parameter policy_events_resource
  - Operation PolicyEventsOperations.list_query_results_for_resource_group has a new parameter policy_events_resource
  - Operation PolicyEventsOperations.list_query_results_for_resource_group_level_policy_assignment has a new parameter policy_events_resource
  - Operation PolicyEventsOperations.list_query_results_for_subscription has a new parameter policy_events_resource
  - Operation PolicyEventsOperations.list_query_results_for_subscription_level_policy_assignment has a new parameter policy_events_resource
  - Operation PolicyStatesOperations.summarize_for_management_group has a new parameter policy_states_summary_resource
  - Operation PolicyStatesOperations.summarize_for_policy_definition has a new parameter policy_states_summary_resource
  - Operation PolicyStatesOperations.summarize_for_policy_set_definition has a new parameter policy_states_summary_resource
  - Operation PolicyStatesOperations.summarize_for_resource has a new parameter policy_states_summary_resource
  - Operation PolicyStatesOperations.summarize_for_resource_group has a new parameter policy_states_summary_resource
  - Operation PolicyStatesOperations.summarize_for_resource_group_level_policy_assignment has a new parameter policy_states_summary_resource
  - Operation PolicyStatesOperations.summarize_for_subscription has a new parameter policy_states_summary_resource
  - Operation PolicyStatesOperations.summarize_for_subscription_level_policy_assignment has a new parameter policy_states_summary_resource
  - Operation PolicyTrackedResourcesOperations.list_query_results_for_management_group has a new parameter policy_tracked_resources_resource
  - Operation PolicyTrackedResourcesOperations.list_query_results_for_resource has a new parameter policy_tracked_resources_resource
  - Operation PolicyTrackedResourcesOperations.list_query_results_for_resource_group has a new parameter policy_tracked_resources_resource
  - Operation PolicyTrackedResourcesOperations.list_query_results_for_subscription has a new parameter policy_tracked_resources_resource

## 1.1.0b2 (2021-12-04)

**Features**

  - Model Remediation has a new parameter failure_threshold
  - Model Remediation has a new parameter parallel_deployments
  - Model Remediation has a new parameter status_message
  - Model Remediation has a new parameter system_data
  - Model Remediation has a new parameter correlation_id
  - Model Remediation has a new parameter resource_count

## 1.1.0b1 (2021-08-23)

**Features**

  - Added operation group AttestationsOperations

## 1.0.0 (2020-12-22)

**Features**

  - Model ExpressionEvaluationDetails has a new parameter expression_kind
  - Added operation group PolicyRestrictionsOperations

## 1.0.0b1 (2020-10-26)

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

## 0.5.0 (2020-03-20)

**Features**

  - Model PolicyState has a new parameter policy_set_definition_version
  - Model PolicyState has a new parameter policy_definition_version
  - Model PolicyState has a new parameter policy_assignment_version
  - Added operation PolicyStatesOperations.trigger_subscription_evaluation
  - Added operation PolicyStatesOperations.trigger_resource_group_evaluation

## 0.4.0 (2019-12-31)

**Features**

  - Model PolicyDefinitionSummary has a new parameter
    policy_definition_group_names
  - Model Remediation has a new parameter resource_discovery_mode
  - Model PolicyAssignmentSummary has a new parameter policy_groups
  - Model PolicyState has a new parameter
    policy_definition_group_names
  - Model SummaryResults has a new parameter policy_group_details
  - Model SummaryResults has a new parameter policy_details
  - Model SummaryResults has a new parameter resource_details
  - Added operation group PolicyMetadataOperations

**Breaking changes**

  - Removed operation PolicyStatesOperations.get_metadata

**General Breaking Changes**

This version uses a next-generation code generator that might introduce
breaking changes if from some import. In summary, some modules were
incorrectly visible/importable and have been renamed. This fixed several
issues caused by usage of classes that were not supposed to be used in
the first place. PolicyInsightsClient cannot be imported from
azure.mgmt.policyinsights.policy_insights_client anymore (import from
azure.mgmt.policyinsights works like before)
PolicyInsightsClientConfiguration import has been moved from
azure.mgmt.policyinsights.policy_insights_client to
azure.mgmt.policyinsights A model MyClass from a "models" sub-module
cannot be imported anymore using
azure.mgmt.policyinsights.models.my_class (import from
azure.mgmt.policyinsights.models works like before) An operation class
MyClassOperations from an operations sub-module cannot be imported
anymore using azure.mgmt.policyinsights.operations.my_class_operations
(import from azure.mgmt.policyinsights.operations works like before)
Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 0.3.1 (2019-04-16)

**Bugfixes**

  - Fix expressionValues and targetValues type

## 0.3.0 (2019-03-12)

**Features**

  - Model QueryOptions has a new parameter expand
  - Model PolicyState has a new parameter policy_evaluation_details
  - Model PolicyState has a new parameter compliance_state

## 0.2.0 (2019-01-02)

**Features**

  - Added operation group RemediationsOperations
  - Added operation group PolicyTrackedResourcesOperations

## 0.1.0 (2018-05-04)

  - Initial Release
