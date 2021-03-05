# Release History

## 12.0.0 (2020-11-25)

## 12.0.0b1 (2020-10-12)

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

## 7.0.0rc2 (2020-09-01)

**Features**

  - Model RedisRebootParameters has a new parameter ports
  - Model RedisInstanceDetails has a new parameter is_master

**Breaking changes**

  - Operation RedisOperations.force_reboot has a new signature

## 7.0.0rc1 (2019-12-07)

**Features**

  - Model RedisUpdateParameters has a new parameter
    replicas_per_master
  - Model RedisCreateParameters has a new parameter
    replicas_per_master
  - Model RedisResource has a new parameter instances
  - Model RedisResource has a new parameter replicas_per_master

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes if from some import. In summary, some modules
were incorrectly visible/importable and have been renamed. This fixed
several issues caused by usage of classes that were not supposed to be
used in the first place.

  - RedisManagementClient cannot be imported from
    `azure.mgmt.redis.redis_management_client` anymore (import from
    `azure.mgmt.redis` works like before)
  - RedisManagementClientConfiguration import has been moved from
    `azure.mgmt.redis.redis_management_client` to
    `azure.mgmt.redis`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.redis.models.my_class` (import from
    `azure.mgmt.redis.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.redis.operations.my_class_operations` (import from
    `azure.mgmt.redis.operations` works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 6.0.0 (2019-01-15)

**Note**

  - azure-mgmt-nspkg is not installed anymore on Python 3 (PEP420-based
    namespace package)

**Features**

  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance
  - Model RedisCreateParameters has a new parameter
    minimum_tls_version
  - Model RedisResource has a new parameter minimum_tls_version
  - Model RedisUpdateParameters has a new parameter
    minimum_tls_version
  - Added operation PatchSchedulesOperations.list_by_redis_resource
  - Added operation RedisOperations.list_upgrade_notifications
  - Added operation RedisOperations.check_name_availability

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

## 5.0.0 (2018-02-08)

**Disclaimer**

Several model (like RedisCreateParameters) have positional arguments
shuffled, due to constraints in our code generator. This is not breaking
if you use keyword arguments. If you are using positional arguments, we
strongly suggest to use keyword only arguments for Model creation, since
next version 6.0.0 will use keyword only arguments for models.

**Breaking changes**

  - RedisCreateParameters parameters orders shuffled (see disclaimer)
  - RedisUpdateParameters parameters orders shuffled (see disclaimer)
  - Merging redis_firewall_rule operations group into firewall_rules
  - Rename firewall_rules.list to
    firewall_rules.list_by_redis_resource

**Features**

  - All operation groups have now a "models" attribute
  - Add linked_server operations group

New ApiVersion 2017-10-01

## 4.1.1 (2017-10-25)

**Bugfixes**

  - Fix "tags" attribute in redis update

## 4.1.0 (2017-04-18)

**Features**

  - Add firewall rules operations

**Notes**

  - This wheel package is now built with the azure wheel extension

## 4.0.0 (2017-01-13)

**Bugfixes**

  - Fix error if patching when not exist

**Breaking change**

  - `redis.update` is no longer an async operation

## 3.0.0 (2016-11-14)

**New features**

  - Add "Everyday" and "Weekend" to schedule enums
  - Improve technical documention

**Breaking change**

  - Simplify `patch_schedules.create_or_update` parameters

## 2.0.0 (2016-10-20)

  - Major bug fixes and refactoring.

## 1.0.0 (2016-08-09)

  - Initial Release (API Version 2016-04-01)
