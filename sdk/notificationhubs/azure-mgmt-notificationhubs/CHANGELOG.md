# Release History

## 8.0.0 (2022-01-06)

**Breaking changes**

  - Return type of `list_keys` in `NamespacesOperions` changed from  `SharedAccessAuthorizationRuleListResult` to `ResourceListKeys`

## 7.0.0 (2020-12-22)

- GA release

## 7.0.0b1 (2020-10-28)

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

## 2.1.0 (2019-04-30)

**Features**

  - Added operation NotificationHubsOperations.patch
  - Added operation NotificationHubsOperations.debug_send

## 2.0.0 (2018-05-25)

**Features**

  - Model NamespaceResource has a new parameter updated_at
  - Model NamespaceResource has a new parameter metric_id
  - Model NamespaceResource has a new parameter data_center
  - Model NamespaceCreateOrUpdateParameters has a new parameter
    updated_at
  - Model NamespaceCreateOrUpdateParameters has a new parameter
    metric_id
  - Model NamespaceCreateOrUpdateParameters has a new parameter
    data_center
  - Added operation
    NotificationHubsOperations.check_notification_hub_availability
  - Added operation group Operations
  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance

**Breaking changes**

  - Operation
    NotificationHubsOperations.create_or_update_authorization_rule
    has a new signature
  - Operation
    NamespacesOperations.create_or_update_authorization_rule has a
    new signature
  - Removed operation NotificationHubsOperations.check_availability
    (replaced by
    NotificationHubsOperations.check_notification_hub_availability)
  - Model SharedAccessAuthorizationRuleResource has a new signature
  - Model SharedAccessAuthorizationRuleProperties has a new signature
  - Model SharedAccessAuthorizationRuleCreateOrUpdateParameters has a
    new signature
  - Removed operation group NameOperations (replaced by
    NotificationHubsOperations.check_notification_hub_availability)
  - Removed operation group HubsOperations (merged in
    NotificationHubsOperations)

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

## 1.0.0 (2017-06-27)

  - New API Version 2017-04-01
  - Expect breaking changes, migrating from an unstable client

This wheel package is built with the azure wheel extension

## 0.30.0 (2016-10-05)

  - Preview release. Based on API version 2016-03-01.
