# Release History

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