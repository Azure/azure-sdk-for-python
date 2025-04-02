# Release History

## 9.2.0b3 (2025-04-02)

### Features Added

  - Client `SearchManagementClient` added operation group `offerings`
  - Model `SearchService` added property `system_data`
  - Model `SearchService` added property `endpoint`
  - Model `SearchService` added property `compute_type`
  - Model `SearchService` added property `upgrade_available`
  - Model `SearchService` added property `service_upgrade_date`
  - Model `SearchServiceUpdate` added property `system_data`
  - Model `SearchServiceUpdate` added property `endpoint`
  - Model `SearchServiceUpdate` added property `compute_type`
  - Model `SearchServiceUpdate` added property `upgrade_available`
  - Model `SearchServiceUpdate` added property `service_upgrade_date`
  - Added enum `ComputeType`
  - Added enum `CreatedByType`
  - Added enum `FeatureName`
  - Added model `FeatureOffering`
  - Added model `OfferingsByRegion`
  - Added model `OfferingsListResult`
  - Added model `SkuOffering`
  - Added model `SkuOfferingLimits`
  - Added model `SystemData`
  - Operation group `ServicesOperations` added method `begin_upgrade`
  - Added operation group `OfferingsOperations`

## 9.2.0b2 (2024-07-18)

### Other Changes

  - Regular release

## 9.2.0b1 (2024-03-18)

### Features Added

  - Added operation group NetworkSecurityPerimeterConfigurationsOperations
  - Model Identity has a new parameter user_assigned_identities
  - Model NetworkRuleSet has a new parameter bypass
  - Model Operation has a new parameter is_data_action
  - Model Operation has a new parameter origin
  - Model Operation has a new parameter properties
  - Model SearchService has a new parameter disabled_data_exfiltration_options
  - Model SearchService has a new parameter e_tag
  - Model SearchServiceUpdate has a new parameter disabled_data_exfiltration_options
  - Model SearchServiceUpdate has a new parameter e_tag

## 9.1.0 (2023-10-23)

### Features Added

  - Added operation group SearchManagementClientOperationsMixin
  - Added operation group UsagesOperations
  - Model SearchService has a new parameter semantic_search
  - Model SearchServiceUpdate has a new parameter semantic_search

## 9.0.0 (2023-02-15)

### Features Added

  - Model PrivateEndpointConnectionProperties has a new parameter group_id
  - Model PrivateEndpointConnectionProperties has a new parameter provisioning_state
  - Model SearchService has a new parameter auth_options
  - Model SearchService has a new parameter disable_local_auth
  - Model SearchService has a new parameter encryption_with_cmk
  - Model SearchServiceUpdate has a new parameter auth_options
  - Model SearchServiceUpdate has a new parameter disable_local_auth
  - Model SearchServiceUpdate has a new parameter encryption_with_cmk

## 9.0.0b1 (2022-10-28)

### Features Added

  - Model Resource has a new parameter identity
  - Model Resource has a new parameter location
  - Model Resource has a new parameter tags

### Breaking Changes

  - Model PrivateLinkResourceProperties no longer has parameter shareable_private_link_resource_types
  - Model SearchService no longer has parameter shared_private_link_resources
  - Removed operation group SharedPrivateLinkResourcesOperations

## 8.0.0 (2020-12-22)

- GA release

## 8.0.0b1 (2020-10-28)

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

## 3.0.0 (2019-09-28)

**Features**

  - Model SearchService has a new parameter shared_private_link_resources
  - Model SearchService has a new parameter public_network_access
  - Model SearchService has a new parameter private_endpoint_connections
  - Model SearchService has a new parameter network_rule_set
  - Added operation group PrivateEndpointConnectionsOperations
  - Added operation group PrivateLinkResourcesOperations
  - Added operation group SharedPrivateLinkResourcesOperations

**Breaking changes**

  - Parameter location of model SearchService is now required
  - Model Resource no longer has parameter location
  - Model Resource no longer has parameter identity
  - Model Resource no longer has parameter tags

## 2.1.0 (2019-05-24)

**Features**

  - Model SearchService has a new parameter identity
  - Model Resource has a new parameter identity

## 2.0.0 (2018-05-21)

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

  - Add "operations" operation group
  - Add services.update
  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance

**Bugfixes**

  - services.create_or_update is now correctly a Long Running
    Operation
  - Compatibility of the sdist with wheel 0.31.0

## 1.0.0 (2016-06-23)

This wheel package is now built with the azure wheel extension

## 0.1.0 (2016-08-09)

  - Initial Release
