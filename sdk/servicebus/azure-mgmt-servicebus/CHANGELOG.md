# Release History

## 6.0.0 (2020-11-23)

**Features**

  - Model SBNamespaceUpdateParameters has a new parameter zone_redundant
  - Model SBNamespaceUpdateParameters has a new parameter identity
  - Model SBNamespaceUpdateParameters has a new parameter encryption
  - Model SBNamespace has a new parameter zone_redundant
  - Model SBNamespace has a new parameter identity
  - Model SBNamespace has a new parameter encryption
  - Added operation NamespacesOperations.get_ip_filter_rule
  - Added operation NamespacesOperations.list_ip_filter_rules
  - Added operation NamespacesOperations.delete_virtual_network_rule
  - Added operation NamespacesOperations.list_virtual_network_rules
  - Added operation NamespacesOperations.get_virtual_network_rule
  - Added operation NamespacesOperations.create_or_update_ip_filter_rule
  - Added operation NamespacesOperations.delete_ip_filter_rule
  - Added operation NamespacesOperations.create_or_update_virtual_network_rule
  - Added operation group PrivateLinkResourcesOperations
  - Added operation group PrivateEndpointConnectionsOperations

**Breaking changes**

  - Operation DisasterRecoveryConfigsOperations.fail_over has a new signature
  - Model ErrorResponse has a new signature
  - Removed operation NamespacesOperations.list_network_rule_sets

## 6.0.0b1 (2020-10-12)

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

## 1.0.0 (2020-09-16)

**Features**

  - Model SBNamespace has a new parameter zone_redundant
  - Model SBNamespace has a new parameter encryption
  - Model SBNamespaceUpdateParameters has a new parameter zone_redundant
  - Model SBNamespaceUpdateParameters has a new parameter identity
  - Model SBNamespaceUpdateParameters has a new parameter encryption
  - Added operation NamespacesOperations.create_or_update_virtual_network_rule
  - Added operation NamespacesOperations.create_or_update_ip_filter_rule
  - Added operation NamespacesOperations.list_virtual_network_rules
  - Added operation NamespacesOperations.delete_ip_filter_rule
  - Added operation NamespacesOperations.list_ip_filter_rules
  - Added operation NamespacesOperations.get_ip_filter_rule
  - Added operation NamespacesOperations.get_virtual_network_rule
  - Added operation NamespacesOperations.delete_virtual_network_rule
  - Added operation group PrivateLinkResourcesOperations
  - Added operation group PrivateEndpointConnectionsOperations

**Breaking changes**

  - Model ErrorResponse has a new signature

## 0.6.0 (2019-04-09)

**Features**

  - Added operation NamespacesOperations.get_network_rule_set
  - Added operation NamespacesOperations.migrate
  - Added operation
    NamespacesOperations.create_or_update_network_rule_set

## 0.5.4 (2019-02-15)

**Features**

  - Added operation NamespacesOperations.migrate

## 0.5.3 (2018-10-29)

**Bugfix**

  - Fix sdist broken in 0.5.2. No code change.

## 0.5.2 (2018-09-28)

**Features**

  - Model MigrationConfigProperties has a new parameter migration_state

**Note**

  - azure-mgmt-nspkg is not installed anymore on Python 3 (PEP420-based
    namespace package)

## 0.5.1 (2018-07-09)

**Features**

  - Add pending_replication_operations_count

**Bugfixes**

  - Fix some Py3 import models

## 0.5.0 (2018-04-26)

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

**SDK Features**

  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance

**ServiceBus features**

  - Add dead_lettering_on_filter_evaluation_exceptions
  - Add enable_batched_operations property to ServiceBus Queue
  - Add migration_config operations
  - Add skip and top to list commands
  - Add 'properties' to CorrelationFilter
  - Remove 'enableSubscriptionPartitioning' deprecated property

## 0.4.0 (2017-12-12)

**Features**

  - Add alternate_name to some models (GEO DR pairing)
  - Add disaster_recovery_configs.check_name_availability_method
  - Add disaster_recovery_configs.list_authorization_rules
  - Add disaster_recovery_configs.get_authorization_rule
  - Add disaster_recovery_configs.list_keys

## 0.3.1 (2017-12-08)

**Bugfixes**

  - Add missing forward_to, forward_dead_lettered_messages_to
  - "rights" is now required, as expected, for operations called
    create_or_update_authorization_rule

## 0.3.0 (2017-10-26)

**Features**

  - Add disaster_recovery_configs operation group
  - Add regions operation group
  - Add premium_messgings_regions operation group
  - Add event_hubs operation group
  - Add Geo DR

## 0.2.0 (2017-06-26)

  - New API Version 2017-04-01
  - Expect breaking changes, as a unstable client

This wheel package is built with the azure wheel extension

## 0.1.0 (2016-10-27)

  - Initial Release
