# Release History

## 2.1.0 (2022-07-28)

**Features**

  - Model PrivateEndpointConnectionVaultProperties has a new parameter location
  - Model PrivateEndpointConnectionVaultProperties has a new parameter name
  - Model PrivateEndpointConnectionVaultProperties has a new parameter type
  - Model ResourceCertificateAndAadDetails has a new parameter aad_audience
  - Model Sku has a new parameter capacity
  - Model Sku has a new parameter family
  - Model Sku has a new parameter size
  - Model VaultProperties has a new parameter backup_storage_version
  - Model VaultProperties has a new parameter monitoring_settings
  - Model VaultProperties has a new parameter move_details
  - Model VaultProperties has a new parameter move_state
  - Model VaultProperties has a new parameter redundancy_settings

## 2.0.0 (2021-07-12)

**Features**

  - Model PatchTrackedResource has a new parameter etag
  - Model Resource has a new parameter etag
  - Model VaultProperties has a new parameter encryption
  - Model PatchVault has a new parameter etag
  - Model Sku has a new parameter tier
  - Model VaultExtendedInfoResource has a new parameter etag
  - Model ResourceCertificateAndAadDetails has a new parameter service_resource_id
  - Model Vault has a new parameter system_data
  - Model Vault has a new parameter etag
  - Model IdentityData has a new parameter user_assigned_identities
  - Model TrackedResource has a new parameter etag
  - Added operation VaultsOperations.begin_update
  - Added operation VaultsOperations.begin_create_or_update
  - Added operation group RecoveryServicesClientOperationsMixin

**Breaking changes**

  - Model PatchTrackedResource no longer has parameter e_tag
  - Model Resource no longer has parameter e_tag
  - Model PatchVault no longer has parameter e_tag
  - Model VaultExtendedInfoResource no longer has parameter e_tag
  - Model Vault no longer has parameter e_tag
  - Model TrackedResource no longer has parameter e_tag
  - Removed operation VaultsOperations.create_or_update
  - Removed operation VaultsOperations.update

## 1.0.0 (2020-12-17)

**Features**

  - Model PatchVault has a new parameter identity

## 1.0.0b1 (2020-11-10)

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

## 0.5.0 (2020-04-21)

**Features**

  - Model Vault has a new parameter identity
  - Model VaultProperties has a new parameter private_endpoint_state_for_backup
  - Model VaultProperties has a new parameter private_endpoint_connections
  - Model VaultProperties has a new parameter private_endpoint_state_for_site_recovery
  - Added operation group PrivateLinkResourcesOperations

**General Breaking Changes**

This version uses a next-generation code generator that *might*
introduce breaking changes. In summary, some modules were incorrectly
visible/importable and have been renamed. This fixed several issues
caused by usage of classes that were not supposed to be used in the
first place.

  - RecoveryServicesClient cannot be imported from
    `azure.mgmt.recoveryservices.cost_management_client` anymore (import from
    `azure.mgmt.recoveryservices` works like before)
  - RecoveryServicesClientConfiguration import has been moved from
    `azure.mgmt.recoveryservices.cost_management_client` to `azure.mgmt.recoveryservices`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.recoveryservices.models.my_class` (import from
    `azure.mgmt.recoveryservices.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.recoveryservices.operations.my_class_operations` (import from
    `azure.mgmt.recoveryservices.operations` works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 0.4.0 (2019-04-05)

**Features**

  - Added operation recovery_services.check_name_availability

## 0.3.0 (2018-05-25)

**Breaking Changes**

  - Removed operation group BackupVaultConfigsOperations (moved to
    azure-mgmt-recoveryservicesbackup)
  - Removed operation group BackupStorageConfigsOperations (moved to
    azure-mgmt-recoveryservicesbackup)

**Features**

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

## 0.2.0 (2017-10-16)

**Bugfixes**

  - blob_duration is now a str (from iso-8601)
  - "service_specification" is renamed
    "properties.service_specification"
  - Fix operations list

## 0.1.1 (2019-03-12)

  - Updating permissible versions of the msrestazure package to unblock
    [Azure/azure-cli#6973](https://github.com/Azure/azure-cli/issues/6973).

## 0.1.0 (2017-07-20)

  - Initial Release
