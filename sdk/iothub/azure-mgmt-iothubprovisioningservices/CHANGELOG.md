# Release History

## 1.2.0b3 (2025-10-09)

### Features Added

  - Model `IotDpsClient` added parameter `cloud_setting` in method `__init__`
  - Client `IotDpsClient` added method `send_request`
  - Model `GroupIdInformation` added property `system_data`
  - Model `IotDpsPropertiesDescription` added property `device_registry_namespace`
  - Model `Resource` added property `system_data`
  - Added enum `DeviceRegistryNamespaceAuthenticationType`
  - Added model `DeviceRegistryNamespaceDescription`
  - Added model `ErrorAdditionalInfo`
  - Added model `ErrorDetail`
  - Added model `ErrorResponse`
  - Added model `ProxyResource`
  - Added model `TrackedResource`
  - Model `DpsCertificateOperations` added parameter `etag` in method `create_or_update`
  - Model `DpsCertificateOperations` added parameter `match_condition` in method `create_or_update`
  - Model `DpsCertificateOperations` added parameter `etag` in method `delete`
  - Model `DpsCertificateOperations` added parameter `match_condition` in method `delete`
  - Model `DpsCertificateOperations` added parameter `etag` in method `generate_verification_code`
  - Model `DpsCertificateOperations` added parameter `match_condition` in method `generate_verification_code`
  - Model `DpsCertificateOperations` added parameter `etag` in method `get`
  - Model `DpsCertificateOperations` added parameter `match_condition` in method `get`
  - Model `DpsCertificateOperations` added parameter `etag` in method `verify_certificate`
  - Model `DpsCertificateOperations` added parameter `match_condition` in method `verify_certificate`

### Breaking Changes

  - Method `DpsCertificateOperations.list` changed from `asynchronous` to `synchronous`
  - Method `IotDpsResourceOperations.list_private_link_resources` changed from `asynchronous` to `synchronous`
  - Model `Resource` deleted or renamed its instance variable `location`
  - Model `Resource` deleted or renamed its instance variable `resourcegroup`
  - Model `Resource` deleted or renamed its instance variable `subscriptionid`
  - Model `Resource` deleted or renamed its instance variable `tags`
  - Deleted or renamed model `CertificateBodyDescription`
  - Deleted or renamed model `CertificateListDescription`
  - Deleted or renamed model `PrivateLinkResources`
  - Method `DpsCertificateOperations.create_or_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `DpsCertificateOperations.delete` changed its parameter `certificate_name1` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.delete` changed its parameter `certificate_raw_bytes` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.delete` changed its parameter `certificate_is_verified` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.delete` changed its parameter `certificate_purpose` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.delete` changed its parameter `certificate_created` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.delete` changed its parameter `certificate_last_updated` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.delete` changed its parameter `certificate_has_private_key` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.delete` changed its parameter `certificate_nonce` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.delete` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `DpsCertificateOperations.generate_verification_code` changed its parameter `certificate_name1` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.generate_verification_code` changed its parameter `certificate_raw_bytes` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.generate_verification_code` changed its parameter `certificate_is_verified` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.generate_verification_code` changed its parameter `certificate_purpose` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.generate_verification_code` changed its parameter `certificate_created` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.generate_verification_code` changed its parameter `certificate_last_updated` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.generate_verification_code` changed its parameter `certificate_has_private_key` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.generate_verification_code` changed its parameter `certificate_nonce` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.generate_verification_code` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `DpsCertificateOperations.get` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `DpsCertificateOperations.verify_certificate` changed its parameter `certificate_name1` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.verify_certificate` changed its parameter `certificate_raw_bytes` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.verify_certificate` changed its parameter `certificate_is_verified` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.verify_certificate` changed its parameter `certificate_purpose` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.verify_certificate` changed its parameter `certificate_created` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.verify_certificate` changed its parameter `certificate_last_updated` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.verify_certificate` changed its parameter `certificate_has_private_key` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.verify_certificate` changed its parameter `certificate_nonce` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.verify_certificate` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `IotDpsResourceOperations.get_operation_result` parameter `asyncinfo` changed default value from `str` to `none`
  - Method `IotDpsResourceOperations.get_operation_result` changed its parameter `asyncinfo` from `positional_or_keyword` to `keyword_only`

## 1.2.0b3 (2025-10-09)

### Features Added

  - Model `GroupIdInformation` added property `system_data`
  - Model `IotDpsPropertiesDescription` added property `device_registry_namespace`
  - Model `Resource` added property `system_data`
  - Added enum `DeviceRegistryNamespaceAuthenticationType`
  - Added model `DeviceRegistryNamespaceDescription`
  - Added model `ErrorAdditionalInfo`
  - Added model `ErrorDetail`
  - Added model `ErrorResponse`
  - Added model `ProxyResource`
  - Added model `TrackedResource`
  - Model `DpsCertificateOperations` added parameter `etag` in method `create_or_update`
  - Model `DpsCertificateOperations` added parameter `match_condition` in method `create_or_update`
  - Model `DpsCertificateOperations` added parameter `etag` in method `delete`
  - Model `DpsCertificateOperations` added parameter `match_condition` in method `delete`
  - Model `DpsCertificateOperations` added parameter `etag` in method `generate_verification_code`
  - Model `DpsCertificateOperations` added parameter `match_condition` in method `generate_verification_code`
  - Model `DpsCertificateOperations` added parameter `etag` in method `get`
  - Model `DpsCertificateOperations` added parameter `match_condition` in method `get`
  - Model `DpsCertificateOperations` added parameter `etag` in method `verify_certificate`
  - Model `DpsCertificateOperations` added parameter `match_condition` in method `verify_certificate`

### Breaking Changes
  - This version introduces new hybrid models which have dual dictionary and model nature. And please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - Deleted or renamed client `IotDpsClient`
  - Method `DpsCertificateOperations.list` changed from `asynchronous` to `synchronous`
  - Method `IotDpsResourceOperations.list_private_link_resources` changed from `asynchronous` to `synchronous`
  - Model `Resource` deleted or renamed its instance variable `location`
  - Model `Resource` deleted or renamed its instance variable `resourcegroup`
  - Model `Resource` deleted or renamed its instance variable `subscriptionid`
  - Model `Resource` deleted or renamed its instance variable `tags`
  - Deleted or renamed model `CertificateBodyDescription`
  - Deleted or renamed model `CertificateListDescription`
  - Deleted or renamed model `PrivateLinkResources`
  - Method `DpsCertificateOperations.create_or_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `DpsCertificateOperations.delete` changed its parameter `certificate_name1` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.delete` changed its parameter `certificate_raw_bytes` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.delete` changed its parameter `certificate_is_verified` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.delete` changed its parameter `certificate_purpose` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.delete` changed its parameter `certificate_created` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.delete` changed its parameter `certificate_last_updated` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.delete` changed its parameter `certificate_has_private_key` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.delete` changed its parameter `certificate_nonce` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.delete` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `DpsCertificateOperations.generate_verification_code` changed its parameter `certificate_name1` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.generate_verification_code` changed its parameter `certificate_raw_bytes` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.generate_verification_code` changed its parameter `certificate_is_verified` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.generate_verification_code` changed its parameter `certificate_purpose` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.generate_verification_code` changed its parameter `certificate_created` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.generate_verification_code` changed its parameter `certificate_last_updated` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.generate_verification_code` changed its parameter `certificate_has_private_key` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.generate_verification_code` changed its parameter `certificate_nonce` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.generate_verification_code` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `DpsCertificateOperations.get` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `DpsCertificateOperations.verify_certificate` changed its parameter `certificate_name1` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.verify_certificate` changed its parameter `certificate_raw_bytes` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.verify_certificate` changed its parameter `certificate_is_verified` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.verify_certificate` changed its parameter `certificate_purpose` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.verify_certificate` changed its parameter `certificate_created` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.verify_certificate` changed its parameter `certificate_last_updated` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.verify_certificate` changed its parameter `certificate_has_private_key` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.verify_certificate` changed its parameter `certificate_nonce` from `positional_or_keyword` to `keyword_only`
  - Method `DpsCertificateOperations.verify_certificate` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Parameter `asyncinfo` of `IotDpsResourceOperations.get_operation_result` is now required
  - Method `IotDpsResourceOperations.get_operation_result` changed its parameter `asyncinfo` from `positional_or_keyword` to `keyword_only`

## 1.2.0b2 (2023-06-16)

### Features Added

  - Model IotDpsPropertiesDescription has a new parameter portal_operations_host_name
  - Model ProvisioningServiceDescription has a new parameter identity
  - Model ProvisioningServiceDescription has a new parameter resourcegroup
  - Model ProvisioningServiceDescription has a new parameter subscriptionid
  - Model Resource has a new parameter resourcegroup
  - Model Resource has a new parameter subscriptionid

## 1.2.0b1 (2022-11-15)

### Features Added

  - Added model ErrorMessage

## 1.1.0 (2022-02-07)

**Features**

  - Model CertificateResponse has a new parameter system_data
  - Model IotDpsPropertiesDescription has a new parameter enable_data_residency
  - Model PrivateEndpointConnection has a new parameter system_data
  - Model ProvisioningServiceDescription has a new parameter system_data

## 1.0.0 (2021-08-18)

**Features**

  - Model CertificateBodyDescription has a new parameter is_verified

## 1.0.0b1 (2021-05-14)

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


## 0.2.0 (2018-04-17)

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

**Features**

  - New ApiVersion 2018-01-22

## 0.1.0 (2018-01-04)

  - Initial Release
