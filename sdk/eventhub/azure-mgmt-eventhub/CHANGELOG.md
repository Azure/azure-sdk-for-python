# Release History

## 8.0.0 (2020-09-16)

**Features**

  - Model NetworkRuleSet has a new parameter trusted_service_access_enabled
  - Added operation group PrivateEndpointConnectionsOperations
  - Added operation group PrivateLinkResourcesOperations

## 8.0.0b1 (2020-06-17)

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

## 4.0.0 (2020-06-12)

**Features**

  - Model Cluster has a new parameter updated_at
  - Model Cluster has a new parameter created_at
  - Added operation ClustersOperations.update
  - Added operation ClustersOperations.create_or_update
  - Added operation ClustersOperations.list_available_cluster_region

** Breaking changes**

  - Model Cluster no longer has parameter created
  - Model Cluster no longer has parameter updated
  - Removed operation ClustersOperations.put
  - Removed operation ClustersOperations.list_available_clusters
  - Removed operation ClustersOperations.patch

## 3.1.0 (2020-05-13)

**Features**

  - Model EHNamespace has a new parameter encryption
  - Model EHNamespace has a new parameter identity
  - Model EHNamespace has a new parameter cluster_arm_id
  - Added operation NamespacesOperations.list_keys
  - Added operation NamespacesOperations.get_authorization_rule
  - Added operation NamespacesOperations.check_name_availability
  - Added operation NamespacesOperations.list_authorization_rules
  - Added operation NamespacesOperations.regenerate_keys
  - Added operation NamespacesOperations.create_or_update_authorization_rule
  - Added operation NamespacesOperations.delete_authorization_rule

## 3.0.0 (2019-06-18)

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes if you were importing from the v20xx_yy_zz
API folders. In summary, some modules were incorrectly
visible/importable and have been renamed. This fixed several issues
caused by usage of classes that were not supposed to be used in the
first place.

  - EventHubManagementClient cannot be imported from
    `azure.mgmt.eventhub.v20xx_yy_zz.event_hub_management_client`
    anymore (import from `azure.mgmt.eventhub.v20xx_yy_zz` works
    like before)
  - EventHubManagementClientConfiguration import has been moved from
    `azure.mgmt.eventhub.v20xx_yy_zz.event_hub_management_client`
    to `azure.mgmt.eventhub.v20xx_yy_zz`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.eventhub.v20xx_yy_zz.models.my_class`
    (import from `azure.mgmt.eventhub.v20xx_yy_zz.models` works like
    before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.eventhub.v20xx_yy_zz.operations.my_class_operations`
    (import from `azure.mgmt.eventhub.v20xx_yy_zz.operations` works
    like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 2.6.0 (2019-04-29)

**Preview features**

  - Added operation ClustersOperations.put
  - Added operation ClustersOperations.list_available_clusters
  - Added operation ClustersOperations.list_namespaces
  - Added operation ClustersOperations.delete

**Bugfixes**

  - Remove useless files packaged by mistake
    (azure.mgmt.eventhub.operations folder)

## 2.5.0 (2019-04-09)

**Features**

  - Added operation
    NamespacesOperations.create_or_update_network_rule_set for the
    2017-04-01 API version
  - Added operation NamespacesOperations.get_network_rule_set for the
    2017-04-01 API version

## 2.4.0 (2019-03-06)

**Features**

  - MultiApi support for 2015-08-01, 2017-04-01 and 2018-01-01-preview
  - 2017-04-01 is the default API version

## 2.3.0 (2019-02-04)

**Features**

  - Model CaptureDescription has a new parameter skip_empty_archives

## 2.2.0 (2018-10-29)

**Features**

  - Add kafka_enabled attribute

**Note**

  - azure-mgmt-nspkg is not installed anymore on Python 3 (PEP420-based
    namespace package)

## 2.1.0 (2018-07-31)

**Features**

  - Add pending_replication_operations_count support

**Bugfixes**

  - Fix some Python3 models

## 2.0.0 (2018-05-04)

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

**Features**

  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance
  - Add region operations group
  - Add skip/top to relevant operations
  - Add get_messaging_plan operation

**Bugfixes**

  - Compatibility of the sdist with wheel 0.31.0

## 1.2.0 (2017-12-12)

**Features**

  - Add alternate_name to some models (GEO DR pairing)
  - Add disaster_recovery_configs.check_name_availability
  - Add disaster_recovery_configs.list_authorization_rules
  - Add disaster_recovery_configs.get_authorization_rule
  - Add disaster_recovery_configs.list_keys

**Bugfixes**

  - "rights" is now required, as expected, for operations called
    create_or_update_authorization_rule
  - Fix message_retention_in_days validation rule
  - Fix partition_count validation rule

## 1.1.0 (2017-10-26)

**Features**

  - Add disaster_recovery_configs operation group
  - Add Geo DR

## 1.0.0 (2017-06-27)

  - New API Version 2017-04-01
  - Expect breaking changes, migrating from an unstable client

This wheel package is built with the azure wheel extension

## 0.2.0 (2016-10-27)

**Breaking changes**

  - CreateOrUpdate has flatten its parameters, moving from one big
    Properties object to several small specifics.

## 0.1.0 (2016-10-27)

  - Initial Release