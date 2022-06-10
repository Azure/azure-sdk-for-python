# Release History

## 10.0.0 (2022-06-10)

**Features**

  - Model IntegrationServiceEnvironment has a new parameter identity
  - Model Workflow has a new parameter identity

**Breaking changes**

  - Operation IntegrationServiceEnvironmentManagedApisOperations.begin_put has a new parameter integration_service_environment_managed_api

## 9.0.0 (2020-12-18)

**Features**

  - Model IntegrationServiceEnvironmentProperties has a new parameter encryption_configuration

## 9.0.0b1 (2020-10-31)

This is beta preview version.
For detailed changelog please refer to equivalent stable version 3.0.0 (https://pypi.org/project/azure-mgmt-logic/3.0.0/)

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
  - For a complete set of supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core-tracing-opentelemetry) for an overview.

## 4.0.0rc2 (2019-01-11)

**Bugfixes**

  - Fixed JSON parsing problem that could raise unexpected exceptions

## 4.0.0rc1 (2018-12-10)

**Features**

  - Added operation WorkflowsOperations.validate_by_location
  - Added operation WorkflowsOperations.validate_by_resource_group
  - Added operation IntegrationAccountsOperations.list_callback_url
  - Added operation group WorkflowRunActionRequestHistoriesOperations
  - Added operation group Operations
  - Added operation group WorkflowRunActionScopeRepetitionsOperations
  - Added operation group WorkflowVersionTriggersOperations
  - Added operation group IntegrationAccountSessionsOperations
  - Added operation group IntegrationAccountCertificatesOperations
  - Added operation group IntegrationAccountSchemasOperations
  - Added operation group
    WorkflowRunActionRepetitionsRequestHistoriesOperations
  - Added operation group IntegrationAccountAgreementsOperations
  - Added operation group IntegrationAccountMapsOperations
  - Added operation group IntegrationAccountPartnersOperations

**Breaking changes**

  - Removed operation WorkflowsOperations.validate_workflow
  - Removed operation WorkflowsOperations.validate
  - Removed operation WorkflowVersionsOperations.list_callback_url
  - Removed operation IntegrationAccountsOperations.get_callback_url
  - Removed operation group AgreementsOperations
  - Removed operation group SessionsOperations
  - Removed operation group CertificatesOperations
  - Removed operation group SchemasOperations
  - Removed operation group MapsOperations
  - Removed operation group WorkflowRunActionScopedRepetitionsOperations
  - Removed operation group PartnersOperations

## 3.0.0 (2018-05-18)

**Features**

  - Model WorkflowTriggerListCallbackUrlQueries has a new parameter se
  - Model WorkflowRun has a new parameter wait_end_time
  - Model WorkflowRunTrigger has a new parameter scheduled_time
  - Added operation IntegrationAccountsOperations.log_tracking_events
  - Added operation
    IntegrationAccountsOperations.regenerate_access_key
  - Added operation IntegrationAccountsOperations.list_key_vault_keys
  - Added operation
    WorkflowRunActionsOperations.list_expression_traces
  - Added operation PartnersOperations.list_content_callback_url
  - Added operation AgreementsOperations.list_content_callback_url
  - Added operation SchemasOperations.list_content_callback_url
  - Added operation WorkflowsOperations.move
  - Added operation WorkflowsOperations.validate_workflow
  - Added operation WorkflowsOperations.list_callback_url
  - Added operation WorkflowTriggersOperations.get_schema_json
  - Added operation WorkflowTriggersOperations.reset
  - Added operation WorkflowTriggersOperations.set_state
  - Added operation MapsOperations.list_content_callback_url
  - Added operation group IntegrationAccountAssembliesOperations
  - Added operation group WorkflowRunActionScopedRepetitionsOperations
  - Added operation group WorkflowRunActionRepetitionsOperations
  - Added operation group
    IntegrationAccountBatchConfigurationsOperations
  - Added operation group WorkflowRunOperations
  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes.

  - Model signatures now use only keyword-argument syntax. All
    positional arguments must be re-written as keyword-arguments. To
    keep auto-completion in most cases, models are now generated for
    Python 2 and Python 3. Python 3 uses the "\*" syntax for
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

## 2.1.0 (2017-04-18)

  - Add several new workflows methods

**Note**

This wheel package is now built with the azure wheel extension

## 2.0.0 (2017-03-16)

  - Major new release(API Version 2016-06-01)

## 1.0.0 (2016-08-30)

  - Initial Release
      - Workflow in ApiVersion 2016-06-01
      - Everything else API Version 2015-08-01-preview
