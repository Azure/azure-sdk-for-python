# Release History

## 7.1.0 (2020-01-09)

**Features**

  - Model EncryptionService has a new parameter key_type

## 7.0.0 (2019-12-04)

**Features**

  - Model StorageAccountCreateParameters has a new parameter
    routing_preference
  - Model BlobServiceProperties has a new parameter sku
  - Model FileServiceProperties has a new parameter
    share_delete_retention_policy
  - Model FileServiceProperties has a new parameter sku
  - Model StorageAccount has a new parameter routing_preference
  - Model StorageAccountUpdateParameters has a new parameter
    routing_preference
  - Model Endpoints has a new parameter internet_endpoints
  - Model Endpoints has a new parameter microsoft_endpoints

**Breaking changes**

  - Operation FileServicesOperations.set_service_properties has a new
    signature
  - Model Sku has a new signature

## 6.0.0 (2019-10-25)

**Features**

  - Model StorageAccount has a new parameter
    private_endpoint_connections
  - Added operation group PrivateEndpointConnectionsOperations
  - Added operation group PrivateLinkResourcesOperations

**Breaking changes**

  - Operation FileSharesOperations.list has a new signature
  - Operation BlobContainersOperations.list has a new signature

## 5.0.0 (2019-10-21)

**Features**

  - Model AzureFilesIdentityBasedAuthentication has a new parameter
    active_directory_properties

**Breaking changes**

  - Operation StorageAccountsOperations.list_keys has a new signature

## 4.2.0 (2019-10-07)

**Features**

  - Model StorageAccountCreateParameters has a new parameter
    large_file_shares_state
  - Model StorageAccountUpdateParameters has a new parameter
    large_file_shares_state
  - Model StorageAccount has a new parameter large_file_shares_state

## 4.1.0 (2019-09-27)

**Features**

  - Model BlobServiceProperties has a new parameter change_feed
  - Added operation BlobServicesOperations.list
  - Added operation group FileServicesOperations
  - Added operation group FileSharesOperations

## 4.0.0 (2019-06-12)

**Features**

  - Model StorageAccount has a new parameter
    azure_files_identity_based_authentication
  - Model StorageAccountCreateParameters has a new parameter
    azure_files_identity_based_authentication
  - Model StorageAccountUpdateParameters has a new parameter
    azure_files_identity_based_authentication

**Breaking changes**

  - Model StorageAccount no longer has parameter
    enable_azure_files_aad_integration
  - Model StorageAccountCreateParameters no longer has parameter
    enable_azure_files_aad_integration
  - Model StorageAccountUpdateParameters no longer has parameter
    enable_azure_files_aad_integration

**Breaking changes**

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes while using imports. In summary, some modules
were incorrectly visible/importable and have been renamed. This fixed
several issues caused by usage of classes that were not supposed to be
used in the first place.

  - StorageManagementClient cannot be imported from
    `azure.mgmt.storage.storage_management_client` anymore (import
    from `azure.mgmt.storage` works like before)
  - StorageManagementClientConfiguration import has been moved from
    `azure.mgmt.storage.network_management_client` to
    `azure.mgmt.storage`
  - StorageManagementClient cannot be imported from
    `azure.mgmt.storage.v20xx_yy_zz.network_management_client`
    anymore (import from `azure.mgmt.storage.v20xx_yy_zz` works like
    before)
  - StorageManagementClientConfiguration import has been moved from
    `azure.mgmt.storage.v20xx_yy_zz.network_management_client` to
    `azure.mgmt.storage.v20xx_yy_zz`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.storage.v20xx_yy_zz.models.my_class`
    (import from `azure.mgmt.storage.v20xx_yy_zz.models` works like
    before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.storage.v20xx_yy_zz.operations.my_class_operations`
    (import from `azure.mgmt.storage.v20xx_yy_zz.operations` works
    like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one storage mgmt client per process.

## 3.3.0 (2019-04-22)

**Features**

  - Model BlobServiceProperties has a new parameter
    automatic_snapshot_policy_enabled
  - Added operation
    StorageAccountsOperations.revoke_user_delegation_keys
  - Added operation BlobContainerOperations.lease

## 3.2.0 (2019-04-10)

**Features**

  - Added operation BlobContainersOperations.lease for API versions
    2018_02_01 and later

## 3.1.1 (2019-01-02)

**Bugfixes**

  - Fix #4013 - "use_sub_domain" should be "use_sub_domain_name"

## 3.1.0 (2018-11-15)

**Features**

  - Model StorageAccount has a new parameter geo_replication_stats
  - Model StorageAccount has a new parameter failover_in_progress
  - Added operation StorageAccountsOperations.failover
  - Added operation group BlobServicesOperations
  - Operation StorageAccountsOperations.get_properties now support
    expand parameter

## 3.0.0 (2018-09-27)

**Features**

  - Model StorageAccount has a new parameter
    enable_azure_files_aad_integration
  - Model StorageAccountCreateParameters has a new parameter
    enable_azure_files_aad_integration
  - Model StorageAccountUpdateParameters has a new parameter
    enable_azure_files_aad_integration
  - Added operation group ManagementPoliciesOperations. This is
    considered preview and breaking changes might happen.

**Breaking changes**

  - "usage" has been renamed "usages", and the "list" operation has been
    replaced by "list_by_location". Ability to make usage requests
    locally is not available anymore.

**Note**

  - azure-mgmt-nspkg is not installed anymore on Python 3 (PEP420-based
    namespace package)

## 2.0.0 (2018-08-01)

**Bugfixes**

  - Set the signed resource as optional instead of required

## 2.0.0rc4 (2018-06-26)

**Features (2018-02-01/2018-03-01-preview)**

Support HDFS feature and web endpoint in Account properties

  - Model StorageAccountCreateParameters has a new parameter
    is_hns_enabled
  - Model Endpoints has a new parameter web
  - Model Endpoints has a new parameter dfs
  - Model StorageAccount has a new parameter is_hns_enabled

## 2.0.0rc3 (2018-05-30)

**Features**

  - Add preview version of management policy (API 2018-03-01-preview
    only). This is considered preview and breaking changes might happen
    if you opt in for that Api Version.

**Bugfixes**

  - Correct azure-common dependency

## 2.0.0rc2 (2018-05-16)

**Bugfixes**

  - Fix default "models" import to 2018-02-01

## 2.0.0rc1 (2018-05-11)

**Features**

  - Add blob containers operations, immutability policy
  - Add usage.list_by_location
  - Client now supports Azure profiles.
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

## 1.5.0 (2017-12-12)

**Features**

  - Add StorageV2 as valid kind
  - Add official support for API version 2017-10-01

## 1.4.0 (2017-09-26)

**Bug fixes**

  - Add skus operations group to the generic client

**Features**

  - Add official support for API version 2016-01-01

## 1.3.0 (2017-09-08)

**Features**

  - Adds list_skus operation (2017-06-01)

**Breaking changes**

  - Rename the preview attribute "network_acls" to "network_rule_set"

## 1.2.1 (2017-08-14)

**Bugfixes**

  - Remove "tests" packaged by mistake (#1365)

## 1.2.0 (2017-07-19)

**Features**

  - Api version 2017-06-01 is now the default
  - This API version adds Network ACLs objects (2017-06-01 as preview)

## 1.1.0 (2017-06-28)

  - Added support for https traffic only (2016-12-01)

## 1.0.0 (2017-05-15)

  - Tag 1.0.0rc1 as stable (same content)

## 1.0.0rc1 (2017-04-11)

**Features**

To help customers with sovereign clouds (not general Azure), this
version has official multi ApiVersion support for 2015-06-15 and
2016-12-01

## 0.31.0 (2017-01-19)

  - New `list_account_sas` operation
  - New `list_service_sas` operation
  - Name syntax are now checked before RestAPI call, not the server
    (exception changed)

Based on API version 2016-12-01.

## 0.30.0 (2016-11-14)

  - Initial release. Based on API version 2016-01-01 Note that this is
    the same content as 0.30.0rc6, committed as 0.30.0.

## 0.20.0 (2015-08-31)

  - Initial preview release. Based on API version 2015-05-01-preview.