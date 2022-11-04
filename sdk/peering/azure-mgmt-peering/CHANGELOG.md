# Release History

## 2.0.0b1 (2022-11-01)

### Features Added

  - Added operation PeeringServicesOperations.initialize_connection_monitor
  - Added operation PrefixesOperations.create_or_update
  - Added operation PrefixesOperations.delete
  - Added operation PrefixesOperations.get
  - Added operation group CdnPeeringPrefixesOperations
  - Added operation group ConnectionMonitorTestsOperations
  - Added operation group LookingGlassOperations
  - Added operation group PeeringServiceCountriesOperations
  - Added operation group ReceivedRoutesOperations
  - Added operation group RegisteredAsnsOperations
  - Added operation group RegisteredPrefixesOperations
  - Added operation group RpUnbilledPrefixesOperations
  - Model DirectConnection has a new parameter error_message
  - Model DirectConnection has a new parameter microsoft_tracking_id
  - Model ErrorResponse has a new parameter error
  - Model ExchangeConnection has a new parameter error_message
  - Model Operation has a new parameter service_specification
  - Model PeerAsn has a new parameter error_message
  - Model PeerAsn has a new parameter peer_contact_detail
  - Model PeeringService has a new parameter log_analytics_workspace_properties
  - Model PeeringService has a new parameter provider_backup_peering_location
  - Model PeeringService has a new parameter provider_primary_peering_location
  - Model PeeringService has a new parameter sku
  - Model PeeringServicePrefix has a new parameter error_message
  - Model PeeringServicePrefix has a new parameter events
  - Model PeeringServicePrefix has a new parameter peering_service_prefix_key
  - Model PeeringServiceProvider has a new parameter peering_locations

### Breaking Changes

  - Model ErrorResponse no longer has parameter code
  - Model ErrorResponse no longer has parameter message
  - Model PeerAsn no longer has parameter peer_contact_info
  - Operation LegacyPeeringsOperations.list has a new parameter asn
  - Operation LegacyPeeringsOperations.list has a new parameter direct_peering_type
  - Operation PeeringServiceLocationsOperations.list has a new parameter country
  - Operation PrefixesOperations.list_by_peering_service has a new parameter expand
  - Removed operation group PeeringServicePrefixesOperations

## 1.0.0 (2021-04-25)

**Features**

  - Model PeerAsn has a new parameter peer_contact_info
  - Added operation group PeeringServicePrefixesOperations

**Breaking changes**

  - Operation PrefixesOperations.list_by_peering_service has a new signature
  - Operation PeeringServiceLocationsOperations.list has a new signature
  - Operation LegacyPeeringsOperations.list has a new signature
  - Model DirectConnection no longer has parameter error_message
  - Model DirectConnection no longer has parameter microsoft_tracking_id
  - Model PeeringServicePrefix no longer has parameter events
  - Model PeeringServicePrefix no longer has parameter error_message
  - Model PeeringServicePrefix no longer has parameter peering_service_prefix_key
  - Model ExchangeConnection no longer has parameter error_message
  - Model PeerAsn no longer has parameter error_message
  - Model PeerAsn no longer has parameter peer_contact_detail
  - Model PeeringService no longer has parameter sku
  - Model ErrorResponse has a new signature
  - Removed operation PrefixesOperations.delete
  - Removed operation PrefixesOperations.create_or_update
  - Removed operation PrefixesOperations.get
  - Removed operation group CdnPeeringPrefixesOperations
  - Removed operation group ReceivedRoutesOperations
  - Removed operation group RegisteredAsnsOperations
  - Removed operation group PeeringServiceCountriesOperations
  - Removed operation group RegisteredPrefixesOperations

## 1.0.0b1 (2020-12-07)

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

## 0.2.0 (2020-04-12)

**Features**

  - Model PeeringServicePrefix has a new parameter peering_service_prefix_key
  - Model PeerAsn has a new parameter peer_contact_detail
  - Model PeeringService has a new parameter sku
  - Added operation group RegisteredPrefixesOperations
  - Added operation group PeeringServiceCountriesOperations
  - Added operation group RegisteredAsnsOperations

**Breaking changes**

  - Operation LegacyPeeringsOperations.list has a new signature
  - Operation PrefixesOperations.create_or_update has a new signature
  - Operation PeeringServiceLocationsOperations.list has a new signature
  - Model PeerAsn no longer has parameter peer_contact_info

## 0.1.0rc2 (2019-10-24)

**Breaking changes**

  - Migrated operations from PeeringServicePrefixesOperations to
    PrefixesOperations

## 0.1.0rc1 (2019-09-26)

  - Initial Release
