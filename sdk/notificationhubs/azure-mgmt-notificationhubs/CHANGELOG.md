# Release History

## 8.1.0b2 (2024-03-21)

### Features Added

  - Added operation NamespacesOperations.delete
  - Added operation NamespacesOperations.get_pns_credentials
  - Added operation NamespacesOperations.update
  - Added operation NotificationHubsOperations.update
  - Added operation group PrivateEndpointConnectionsOperations
  - Model CheckAvailabilityResult has a new parameter system_data
  - Model DebugSendResponse has a new parameter system_data
  - Model ErrorResponse has a new parameter error
  - Model NamespacePatchParameters has a new parameter properties
  - Model NamespaceResource has a new parameter network_acls
  - Model NamespaceResource has a new parameter pns_credentials
  - Model NamespaceResource has a new parameter private_endpoint_connections
  - Model NamespaceResource has a new parameter public_network_access
  - Model NamespaceResource has a new parameter replication_region
  - Model NamespaceResource has a new parameter system_data
  - Model NamespaceResource has a new parameter zone_redundancy
  - Model NotificationHubPatchParameters has a new parameter browser_credential
  - Model NotificationHubPatchParameters has a new parameter daily_max_active_devices
  - Model NotificationHubPatchParameters has a new parameter fcm_v1_credential
  - Model NotificationHubPatchParameters has a new parameter xiaomi_credential
  - Model NotificationHubResource has a new parameter browser_credential
  - Model NotificationHubResource has a new parameter daily_max_active_devices
  - Model NotificationHubResource has a new parameter fcm_v1_credential
  - Model NotificationHubResource has a new parameter system_data
  - Model NotificationHubResource has a new parameter xiaomi_credential
  - Model Operation has a new parameter is_data_action
  - Model Operation has a new parameter properties
  - Model OperationDisplay has a new parameter description
  - Model PnsCredentialsResource has a new parameter browser_credential
  - Model PnsCredentialsResource has a new parameter fcm_v1_credential
  - Model PnsCredentialsResource has a new parameter system_data
  - Model PnsCredentialsResource has a new parameter xiaomi_credential
  - Model Resource has a new parameter system_data
  - Model SharedAccessAuthorizationRuleResource has a new parameter system_data
  - Model WnsCredential has a new parameter certificate_key
  - Model WnsCredential has a new parameter wns_certificate
  - Operation NamespacesOperations.list has a new optional parameter skip_token
  - Operation NamespacesOperations.list has a new optional parameter top
  - Operation NamespacesOperations.list_all has a new optional parameter skip_token
  - Operation NamespacesOperations.list_all has a new optional parameter top
  - Operation NotificationHubsOperations.list has a new optional parameter skip_token
  - Operation NotificationHubsOperations.list has a new optional parameter top

### Breaking Changes

  - Model DebugSendResponse no longer has parameter sku
  - Model ErrorResponse no longer has parameter code
  - Model ErrorResponse no longer has parameter message
  - Model NotificationHubPatchParameters no longer has parameter id
  - Model NotificationHubPatchParameters no longer has parameter location
  - Model NotificationHubPatchParameters no longer has parameter name_properties_name
  - Model NotificationHubPatchParameters no longer has parameter type
  - Model PnsCredentialsResource no longer has parameter sku
  - Model Resource no longer has parameter location
  - Model Resource no longer has parameter sku
  - Model Resource no longer has parameter tags
  - Model SharedAccessAuthorizationRuleResource no longer has parameter sku
  - Operation NotificationHubsOperations.debug_send no longer has parameter parameters
  - Parameter auth_token_url of model AdmCredential is now required
  - Parameter baidu_api_key of model BaiduCredential is now required
  - Parameter baidu_end_point of model BaiduCredential is now required
  - Parameter baidu_secret_key of model BaiduCredential is now required
  - Parameter certificate_key of model MpnsCredential is now required
  - Parameter client_id of model AdmCredential is now required
  - Parameter client_secret of model AdmCredential is now required
  - Parameter endpoint of model ApnsCredential is now required
  - Parameter google_api_key of model GcmCredential is now required
  - Parameter location of model NamespaceResource is now required
  - Parameter location of model NotificationHubResource is now required
  - Parameter mpns_certificate of model MpnsCredential is now required
  - Parameter rights of model SharedAccessAuthorizationRuleProperties is now required
  - Parameter sku of model NamespaceResource is now required
  - Parameter thumbprint of model MpnsCredential is now required
  - Removed operation NamespacesOperations.begin_delete
  - Removed operation NamespacesOperations.patch
  - Removed operation NotificationHubsOperations.patch
  - Renamed operation NamespacesOperations.create_or_update to NamespacesOperations.begin_create_or_update

## 8.1.0b1 (2022-11-11)

### Other Changes

  - Added generated samples in github repo
  - Drop support for python<3.7.0

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
