# Release History

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
