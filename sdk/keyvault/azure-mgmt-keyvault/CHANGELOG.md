# Release History

## 10.0.0 (2022-05-23)

**Breaking changes**

  - Model Key no longer has parameter release_policy
  - Model Key no longer has parameter rotation_policy
  - Model KeyProperties no longer has parameter release_policy
  - Model KeyProperties no longer has parameter rotation_policy

## 9.3.0 (2021-11-11)

**Features**

  - Added some enum value


## 9.2.0 (2021-10-15)

**Features**

  - Model VaultProperties has a new parameter public_network_access
  - Model VaultPatchProperties has a new parameter public_network_access
  - Model KeyAttributes has a new parameter exportable
  - Model Key has a new parameter release_policy
  - Model Key has a new parameter rotation_policy
  - Model KeyProperties has a new parameter release_policy
  - Model KeyProperties has a new parameter rotation_policy

## 9.1.0 (2021-08-26)

**Features**

  - Model VirtualNetworkRule has a new parameter ignore_missing_vnet_service_endpoint
  - Model VaultProperties has a new parameter hsm_pool_resource_id
  - Model PrivateEndpointConnectionItem has a new parameter etag
  - Model PrivateEndpointConnectionItem has a new parameter id
  - Model ServiceSpecification has a new parameter metric_specifications

## 9.0.0 (2021-04-19)

**Features**

  - Model DeletedVaultProperties has a new parameter purge_protection_enabled
  - Model Operation has a new parameter is_data_action
  - Model Vault has a new parameter system_data
  - Model ManagedHsmProperties has a new parameter scheduled_purge_date
  - Model ManagedHsmProperties has a new parameter public_network_access
  - Model ManagedHsmProperties has a new parameter network_acls
  - Model ManagedHsmProperties has a new parameter private_endpoint_connections
  - Model VaultProperties has a new parameter provisioning_state
  - Model PrivateLinkServiceConnectionState has a new parameter actions_required
  - Model ManagedHsmResource has a new parameter system_data
  - Model ManagedHsm has a new parameter system_data
  - Model PrivateEndpointConnection has a new parameter etag
  - Added operation ManagedHsmsOperations.get_deleted
  - Added operation ManagedHsmsOperations.list_deleted
  - Added operation ManagedHsmsOperations.begin_purge_deleted
  - Added operation PrivateEndpointConnectionsOperations.list_by_resource
  - Added operation group SecretsOperations
  - Added operation group MHSMPrivateLinkResourcesOperations
  - Added operation group KeysOperations
  - Added operation group MHSMPrivateEndpointConnectionsOperations

**Breaking changes**

  - Model PrivateLinkServiceConnectionState no longer has parameter action_required

## 8.0.0 (2020-09-29)

**Features**

  - Model ManagedHsmProperties has a new parameter hsm_uri

**Breaking changes**

  - Model ManagedHsmProperties no longer has parameter hsm_pool_uri

## 7.0.0 (2020-09-15)

- Release as a stable version

## 7.0.0b3 (2020-09-09)

**Features**

  - Added operation group ManagedHsmsOperations

## 7.0.0b2 (2020-07-21)

**Bugfixes**
  - Use service api_version "2015-11-01" instead of "2016-10-01".

## 7.0.0b1 (2020-06-17)

This is beta preview version.
For detailed changelog please refer to equivalent stable version 2.2.0 (https://pypi.org/project/azure-mgmt-keyvault/2.2.0/)

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

## 2.2.0 (2020-03-20)

**Features**

  - Model VaultProperties has a new parameter enable_rbac_authorization
  - Model VaultProperties has a new parameter soft_delete_retention_in_days
  - Model VaultPatchProperties has a new parameter enable_rbac_authorization
  - Model VaultPatchProperties has a new parameter soft_delete_retention_in_days

## 2.1.1 (2020-02-07)

**Bugfixes**

  - Fixed multi-API client issues

## 2.1.0 (2020-01-30)

**Features**

  - Model VaultProperties has a new parameter private_endpoint_connections
  - Added operation group PrivateEndpointConnectionsOperations
  - Added operation group PrivateLinkResourcesOperations

## 2.0.0 (2019-06-18)

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes if you were importing from the v20xx_yy_zz
API folders. In summary, some modules were incorrectly
visible/importable and have been renamed. This fixed several issues
caused by usage of classes that were not supposed to be used in the
first place.

  - KeyVaultManagementClient cannot be imported from
    `azure.mgmt.key_vault.v20xx_yy_zz.key_vault_management_client`
    anymore (import from `azure.mgmt.key_vault.v20xx_yy_zz` works
    like before)
  - KeyVaultManagementClientConfiguration import has been moved from
    `azure.mgmt.key_vault.v20xx_yy_zz.key_vault_management_client`
    to `azure.mgmt.key_vault.v20xx_yy_zz`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using
    `azure.mgmt.key_vault.v20xx_yy_zz.models.my_class` (import
    from `azure.mgmt.key_vault.v20xx_yy_zz.models` works like
    before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.key_vault.v20xx_yy_zz.operations.my_class_operations`
    (import from `azure.mgmt.key_vault.v20xx_yy_zz.operations`
    works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 1.1.0 (2018-08-07)

  - Adding support for multi-api and API profiles

## 1.0.0 (2018-06-27)

  - Moving azure-mgmt-keyvault to stable API version 2018-02-14

## 1.0.0b1 (2018-04-10)

  - Upgraded to autorest 3.0 generated code

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

## 1.0.0a2 (2018-03-28)

  - Upgrading to API version 2018-02-14-preview
  - Breaking change in vault create_or_update now returns a
    'LROPoller' objects rather than the Vault, to allow callers to
    determine when the vault is ready to accept traffic. Callers should
    use the result() method to block until the vault is accessible.
  - Adding network_acls vault property for limiting network access to a
    vault
  - Adding managed storage account key backup, restore and soft delete
    support
  - Adding vault property enable_purge_protection for enhance
    protection against vault deletion

## 0.40.0 (2017-06-06)

  - upgrading to API version 2016-10-01
  - adding keyvault management plane updates to enable the soft delete
    feature for a new or existing keyvault

**Notes**

  - this contains a backwards breaking change removing the All value
    from KeyPermissions, SecretPermissions and CertificatePermissions

## 0.31.0 (2017-04-19)

**Bugfixes**

  - Fix possible deserialization error, but updating from
    list<enumtype> to list<str> when applicable

**Notes**

  - This wheel package is now built with the azure wheel extension

## 0.30.1 (2016-12-15)

  - Fix list Vault by subscription method return type

## 0.30.0 (2016-10-04)

  - Initial preview release (API Version 2016-10-02)
