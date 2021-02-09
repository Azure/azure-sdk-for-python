# Release History

## 1.0.0b1 (2020-12-04)

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

## 0.14.0 (2020-05-14)

**Features**

  - Model SapMonitor has a new parameter sap_monitor_collector_version
  - Model SapMonitor has a new parameter monitor_subnet
  - Added operation group ProviderInstancesOperations

**Breaking changes**

  - Model Resource no longer has parameter tags
  - Model Resource no longer has parameter location
  - Model SapMonitor no longer has parameter key_vault_id
  - Model SapMonitor no longer has parameter hana_db_password_key_vault_url
  - Model SapMonitor no longer has parameter hana_db_name
  - Model SapMonitor no longer has parameter hana_db_credentials_msi_id
  - Model SapMonitor no longer has parameter hana_hostname
  - Model SapMonitor no longer has parameter hana_db_username
  - Model SapMonitor no longer has parameter hana_db_password
  - Model SapMonitor no longer has parameter hana_subnet
  - Model SapMonitor no longer has parameter hana_db_sql_port
  - Removed operation group HanaInstancesOperations

## 0.13.0 (2020-02-13)

**Features**

  - New enum values for HanaInstanceSizeNamesEnum

## 0.12.1 (2020-02-05)

**Bugfixes**

  - Correct SKU set

## 0.12.0 (2019-11-20)

**Features**

  - Model SapMonitor has a new parameter enable_customer_analytics
  - Model SapMonitor has a new parameter log_analytics_workspace_id
  - Model SapMonitor has a new parameter
    log_analytics_workspace_shared_key

## 0.11.0 (2019-11-12)

**Features**

  - Model SapMonitor has a new parameter key_vault_id

## 0.10.0 (2019-08-15)

**Features**

  - Model SapMonitor has a new parameter
    log_analytics_workspace_arm_id
  - Model SapMonitor has a new parameter managed_resource_group_name

## 0.9.0 (2019-07-31)

**Features**

  - Model SapMonitor has a new parameter hana_db_credentials_msi_id
  - Model SapMonitor has a new parameter
    hana_db_password_key_vault_url

**Breaking changes**

  - Removed operation HanaInstancesOperations.enable_monitoring

## 0.8.0 (2019-06-26)

**Features**

  - Added operation HanaInstancesOperations.start
  - Added operation HanaInstancesOperations.shutdown
  - Added operation group SapMonitorsOperations

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes if from some import. In summary, some modules
were incorrectly visible/importable and have been renamed. This fixed
several issues caused by usage of classes that were not supposed to be
used in the first place.

  - HanaManagementClient cannot be imported from
    `azure.mgmt.hanaonazure.hana_management_client` anymore (import
    from `azure.mgmt.hanaonazure` works like before)
  - HanaManagementClientConfiguration import has been moved from
    `azure.mgmt.hanaonazure.hana_management_client` to
    `azure.mgmt.hanaonazure`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.hanaonazure.models.my_class` (import
    from `azure.mgmt.hanaonazure.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.hanaonazure.operations.my_class_operations` (import
    from `azure.mgmt.hanaonazure.operations` works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 0.7.1 (2019-06-12)

**Bugfixes**

  - Make mutable some attributes that were read-only by mistake (so they
    can be set on creation)

## 0.7.0 (2019-05-30)

**Features**

  - Model OSProfile has a new parameter ssh_public_key
  - Model HanaInstance has a new parameter partner_node_id
  - Model HanaInstance has a new parameter provisioning_state
  - Added operation HanaInstancesOperations.create
  - Added operation HanaInstancesOperations.delete

## 0.6.0 (2019-05-20)

**Features**

  - Adding new Skus to enums

## 0.5.1 (2019-04-26)

**Bugfixes**

  - Fixing incorrect RestAPI description

## 0.5.0 (2019-04-15)

**Features**

  - Added operation enable_monitoring

## 0.4.0 (2019-02-21)

**Features**

  - Model HanaInstance has a new parameter hw_revision

## 0.3.2 (2019-01-29)

**Features**

  - Add proximity_placement_group

## 0.3.1 (2019-01-24)

**Bugfixes**

  - Fix restart operation

## 0.3.0 (2019-01-03)

**Features**

  - Added operation HanaInstancesOperations.update

## 0.2.1 (2018-08-31)

**Features**

  - Add restart operation

## 0.2.0 (2018-08-06)

**Features**

  - Add power state to Hana instance
  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance

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

## 0.1.1 (2018-05-17)

  - Update HanaHardwareTypeNamesEnum and HanaInstanceSizeNamesEnum
  - Add os_disks to storage_profile

## 0.1.0 (2018-01-17)

  - Initial Release
