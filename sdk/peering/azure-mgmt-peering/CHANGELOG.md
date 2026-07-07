# Release History

## 2.0.0 (2026-07-07)

### Features Added

  - Client `PeeringManagementClient` added method `send_request`
  - Client `PeeringManagementClient` added operation group `connection_monitor_tests`
  - Client `PeeringManagementClient` added operation group `registered_asns`
  - Client `PeeringManagementClient` added operation group `received_routes`
  - Client `PeeringManagementClient` added operation group `rp_unbilled_prefixes`
  - Client `PeeringManagementClient` added operation group `registered_prefixes`
  - Client `PeeringManagementClient` added operation group `cdn_peering_prefixes`
  - Client `PeeringManagementClient` added operation group `looking_glass`
  - Client `PeeringManagementClient` added operation group `peering_service_countries`
  - Enum `ConnectionState` added member `EXTERNAL_BLOCKER`
  - Enum `ConnectionState` added member `TYPE_CHANGE_IN_PROGRESS`
  - Enum `ConnectionState` added member `TYPE_CHANGE_REQUESTED`
  - Model `DirectConnection` added property `microsoft_tracking_id`
  - Model `DirectConnection` added property `error_message`
  - Enum `DirectPeeringType` added member `EDGE_ZONE_FOR_OPERATORS`
  - Enum `DirectPeeringType` added member `IX`
  - Enum `DirectPeeringType` added member `IX_RS`
  - Enum `DirectPeeringType` added member `PEER_PROP`
  - Enum `DirectPeeringType` added member `VOICE`
  - Enum `Enum0` added member `UNAVAILABLE`
  - Model `ExchangeConnection` added property `error_message`
  - Enum `LearnedType` added member `VIA_SERVICE_PROVIDER`
  - Model `Operation` added property `properties`
  - Model `PeerAsn` added property `system_data`
  - Model `Peering` added property `system_data`
  - Model `PeeringLocation` added property `system_data`
  - Model `PeeringService` added property `sku`
  - Model `PeeringService` added property `system_data`
  - Model `PeeringServiceLocation` added property `system_data`
  - Model `PeeringServicePrefix` added property `system_data`
  - Model `PeeringServiceProvider` added property `system_data`
  - Enum `PrefixValidationState` added member `WARNING`
  - Enum `ProvisioningState` added member `CANCELED`
  - Model `Resource` added property `system_data`
  - Added model `CdnPeeringPrefix`
  - Added model `CdnPeeringPrefixProperties`
  - Added enum `Command`
  - Added model `ConnectionMonitorTest`
  - Added model `ConnectionMonitorTestProperties`
  - Added model `ConnectivityProbe`
  - Added model `ContactDetail`
  - Added enum `CreatedByType`
  - Added model `ErrorAdditionalInfo`
  - Added model `LogAnalyticsWorkspaceProperties`
  - Added enum `LookingGlassCommand`
  - Added model `LookingGlassOutput`
  - Added enum `LookingGlassSourceType`
  - Added model `MetricDimension`
  - Added model `MetricSpecification`
  - Added model `OperationProperties`
  - Added enum `PeeringLocationsDirectPeeringType`
  - Added model `PeeringReceivedRoute`
  - Added model `PeeringRegisteredAsn`
  - Added model `PeeringRegisteredAsnProperties`
  - Added model `PeeringRegisteredPrefix`
  - Added model `PeeringRegisteredPrefixProperties`
  - Added model `PeeringServiceCountry`
  - Added model `PeeringServicePrefixEvent`
  - Added model `PeeringServiceSku`
  - Added enum `Protocol`
  - Added model `ProxyResource`
  - Added enum `Role`
  - Added model `RpUnbilledPrefix`
  - Added model `ServiceSpecification`
  - Added model `SystemData`
  - Added model `TrackedResource`
  - Operation group `LegacyPeeringsOperations` added parameter `asn` in method `list`
  - Operation group `LegacyPeeringsOperations` added parameter `direct_peering_type` in method `list`
  - Operation group `PeeringServiceLocationsOperations` added parameter `country` in method `list`
  - Operation group `PeeringServicesOperations` added method `initialize_connection_monitor`
  - Operation group `PrefixesOperations` added parameter `expand` in method `list_by_peering_service`
  - Operation group `PrefixesOperations` added method `create_or_update`
  - Operation group `PrefixesOperations` added method `delete`
  - Added operation group `CdnPeeringPrefixesOperations`
  - Added operation group `ConnectionMonitorTestsOperations`
  - Added operation group `LookingGlassOperations`
  - Added operation group `PeeringServiceCountriesOperations`
  - Added operation group `ReceivedRoutesOperations`
  - Added operation group `RegisteredAsnsOperations`
  - Added operation group `RegisteredPrefixesOperations`
  - Added operation group `RpUnbilledPrefixesOperations`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Deleted enum value `Enum0.UN_AVAILABLE`
  - Model `ErrorResponse` moved instance variable `code` and `message` under property `error` whose type is `ErrorDetail`
  - Deleted or renamed enum value `LearnedType.VIA_PARTNER`
  - Model `PeerAsn` moved instance variable `peer_asn`, `peer_name` and `validation_state` under property `properties` whose type is `PeerAsnProperties`
  - Model `PeerAsn` deleted or renamed its instance variable `peer_contact_info`
  - Model `Peering` moved instance variable `direct`, `exchange`, `peering_location` and `provisioning_state` under property `properties` whose type is `PeeringProperties`
  - Model `PeeringLocation` moved instance variable `direct`, `exchange`, `peering_location`, `country` and `azure_region` under property `properties` whose type is `PeeringLocationProperties`
  - Model `PeeringService` moved instance variable `peering_service_location`, `peering_service_provider` and `provisioning_state` under property `properties` whose type is `PeeringServiceProperties`
  - Model `PeeringServiceLocation` moved instance variable `country`, `state` and `azure_region` under property `properties` whose type is `PeeringServiceLocationProperties`
  - Model `PeeringServicePrefix` moved instance variable `prefix`, `prefix_validation_state`, `learned_type` and `provisioning_state` under property `properties` whose type is `PeeringServicePrefixProperties`
  - Model `PeeringServiceProvider` moved instance variable `service_provider_name` under property `properties` whose type is `PeeringServiceProviderProperties`
  - Deleted or renamed model `ContactInfo`
  - Renamed enum `Enum1` to `LegacyPeeringsKind`
  - Renamed enum `Enum14` to `PeeringLocationsKind`
  - Deleted or renamed enum `Enum15`
  - Deleted or renamed enum `Name`
  - Method `LegacyPeeringsOperations.list` changed its parameter `peering_location`/`kind` from `positional_or_keyword` to `keyword_only`
  - Method `PeeringLocationsOperations.list` changed its parameter `kind`/`direct_peering_type` from `positional_or_keyword` to `keyword_only`
  - Deleted or renamed operation group `PeeringServicePrefixesOperations`

### Other Changes

  - Deleted model `OperationListResult`/`PeerAsnListResult`/`PeeringListResult`/`PeeringLocationListResult`/`PeeringServiceListResult`/`PeeringServiceLocationListResult`/`PeeringServicePrefixListResult`/`PeeringServiceProviderListResult` which actually were not used by SDK users

## 1.0.1 (2026-05-19)

### Other Changes

  - Regenerated with latest code generator tool

## 2.0.0b2 (2026-03-27)

### Features Added

  - Client `PeeringManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `PeeringManagementClient` added method `send_request`
  - Model `CdnPeeringPrefix` added property `system_data`
  - Model `ConnectionMonitorTest` added property `system_data`
  - Enum `ConnectionState` added member `EXTERNAL_BLOCKER`
  - Enum `DirectPeeringType` added member `PEER_PROP`
  - Model `ErrorDetail` added property `target`
  - Model `ErrorDetail` added property `details`
  - Model `ErrorDetail` added property `additional_info`
  - Model `PeerAsn` added property `system_data`
  - Model `Peering` added property `system_data`
  - Model `PeeringLocation` added property `system_data`
  - Enum `PeeringLocationsDirectPeeringType` added member `PEER_PROP`
  - Model `PeeringRegisteredAsn` added property `system_data`
  - Model `PeeringRegisteredPrefix` added property `system_data`
  - Model `PeeringService` added property `system_data`
  - Model `PeeringServiceCountry` added property `system_data`
  - Model `PeeringServiceLocation` added property `system_data`
  - Model `PeeringServicePrefix` added property `system_data`
  - Model `PeeringServiceProvider` added property `system_data`
  - Enum `ProvisioningState` added member `CANCELED`
  - Model `Resource` added property `system_data`
  - Added model `ConnectivityProbe`
  - Added enum `CreatedByType`
  - Added model `ErrorAdditionalInfo`
  - Added enum `Protocol`
  - Added model `ProxyResource`
  - Added model `SystemData`
  - Added model `TrackedResource`

### Breaking Changes

  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Method `CdnPeeringPrefixesOperations.list` changed its parameter `peering_location` from `positional_or_keyword` to `keyword_only`
  - Method `LegacyPeeringsOperations.list` changed its parameter `peering_location`/`kind`/`asn`/`direct_peering_type` from `positional_or_keyword` to `keyword_only`
  - Method `LookingGlassOperations.invoke` changed its parameter `command`/`source_type`/`source_location`/`destination_ip` from `positional_or_keyword` to `keyword_only`
  - Method `PeeringLocationsOperations.list` changed its parameter `kind`/`direct_peering_type` from `positional_or_keyword` to `keyword_only`
  - Method `PeeringServiceLocationsOperations.list` changed its parameter `country` from `positional_or_keyword` to `keyword_only`
  - Method `PrefixesOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `PrefixesOperations.list_by_peering_service` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `ReceivedRoutesOperations.list_by_peering` changed its parameter `prefix`/`as_path`/`origin_as_validation_state`/`rpki_validation_state`/`skip_token` from `positional_or_keyword` to `keyword_only`
  - Method `RpUnbilledPrefixesOperations.list` changed its parameter `consolidate` from `positional_or_keyword` to `keyword_only`
  - Deleted or renamed model `PeeringManagementClientOperationsMixin`

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
