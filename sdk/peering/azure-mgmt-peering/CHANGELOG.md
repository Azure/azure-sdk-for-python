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
  - Model `PeerAsn` added property `properties`
  - Model `PeerAsn` added property `system_data`
  - Model `Peering` added property `properties`
  - Model `Peering` added property `system_data`
  - Model `PeeringLocation` added property `properties`
  - Model `PeeringLocation` added property `system_data`
  - Model `PeeringService` added property `properties`
  - Model `PeeringService` added property `sku`
  - Model `PeeringService` added property `system_data`
  - Model `PeeringServiceLocation` added property `properties`
  - Model `PeeringServiceLocation` added property `system_data`
  - Model `PeeringServicePrefix` added property `properties`
  - Model `PeeringServicePrefix` added property `system_data`
  - Model `PeeringServiceProvider` added property `properties`
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
  - Added model `ErrorDetail`
  - Added enum `LegacyPeeringsKind`
  - Added model `LogAnalyticsWorkspaceProperties`
  - Added enum `LookingGlassCommand`
  - Added model `LookingGlassOutput`
  - Added enum `LookingGlassSourceType`
  - Added model `MetricDimension`
  - Added model `MetricSpecification`
  - Added model `OperationProperties`
  - Added model `PeerAsnProperties`
  - Added model `PeeringLocationProperties`
  - Added enum `PeeringLocationsDirectPeeringType`
  - Added enum `PeeringLocationsKind`
  - Added model `PeeringProperties`
  - Added model `PeeringReceivedRoute`
  - Added model `PeeringRegisteredAsn`
  - Added model `PeeringRegisteredAsnProperties`
  - Added model `PeeringRegisteredPrefix`
  - Added model `PeeringRegisteredPrefixProperties`
  - Added model `PeeringServiceCountry`
  - Added model `PeeringServiceLocationProperties`
  - Added model `PeeringServicePrefixEvent`
  - Added model `PeeringServicePrefixProperties`
  - Added model `PeeringServiceProperties`
  - Added model `PeeringServiceProviderProperties`
  - Added model `PeeringServiceSku`
  - Added enum `Protocol`
  - Added model `ProxyResource`
  - Added enum `Role`
  - Added model `RpUnbilledPrefix`
  - Added model `ServiceSpecification`
  - Added model `SystemData`
  - Added model `TrackedResource`
  - Model `LegacyPeeringsOperations` added parameter `asn` in method `list`
  - Model `LegacyPeeringsOperations` added parameter `direct_peering_type` in method `list`
  - Model `PeeringServiceLocationsOperations` added parameter `country` in method `list`
  - Model `PeeringServicesOperations` added method `initialize_connection_monitor`
  - Model `PrefixesOperations` added parameter `expand` in method `list_by_peering_service`
  - Model `PrefixesOperations` added method `create_or_update`
  - Model `PrefixesOperations` added method `delete`
  - Added model `CdnPeeringPrefixesOperations`
  - Added model `ConnectionMonitorTestsOperations`
  - Added model `LookingGlassOperations`
  - Added model `PeeringServiceCountriesOperations`
  - Added model `ReceivedRoutesOperations`
  - Added model `RegisteredAsnsOperations`
  - Added model `RegisteredPrefixesOperations`
  - Added model `RpUnbilledPrefixesOperations`

### Breaking Changes

  - Deleted or renamed client operation group `PeeringManagementClient.peering_service_prefixes`
  - Deleted or renamed enum value `Enum0.UN_AVAILABLE`
  - Model `ErrorResponse` deleted or renamed its instance variable `code`
  - Model `ErrorResponse` deleted or renamed its instance variable `message`
  - Deleted or renamed enum value `LearnedType.VIA_PARTNER`
  - Model `PeerAsn` deleted or renamed its instance variable `peer_asn`
  - Model `PeerAsn` deleted or renamed its instance variable `peer_contact_info`
  - Model `PeerAsn` deleted or renamed its instance variable `peer_name`
  - Model `PeerAsn` deleted or renamed its instance variable `validation_state`
  - Model `Peering` deleted or renamed its instance variable `direct`
  - Model `Peering` deleted or renamed its instance variable `exchange`
  - Model `Peering` deleted or renamed its instance variable `peering_location`
  - Model `Peering` deleted or renamed its instance variable `provisioning_state`
  - Model `PeeringLocation` deleted or renamed its instance variable `direct`
  - Model `PeeringLocation` deleted or renamed its instance variable `exchange`
  - Model `PeeringLocation` deleted or renamed its instance variable `peering_location`
  - Model `PeeringLocation` deleted or renamed its instance variable `country`
  - Model `PeeringLocation` deleted or renamed its instance variable `azure_region`
  - Model `PeeringService` deleted or renamed its instance variable `peering_service_location`
  - Model `PeeringService` deleted or renamed its instance variable `peering_service_provider`
  - Model `PeeringService` deleted or renamed its instance variable `provisioning_state`
  - Model `PeeringServiceLocation` deleted or renamed its instance variable `country`
  - Model `PeeringServiceLocation` deleted or renamed its instance variable `state`
  - Model `PeeringServiceLocation` deleted or renamed its instance variable `azure_region`
  - Model `PeeringServicePrefix` deleted or renamed its instance variable `prefix`
  - Model `PeeringServicePrefix` deleted or renamed its instance variable `prefix_validation_state`
  - Model `PeeringServicePrefix` deleted or renamed its instance variable `learned_type`
  - Model `PeeringServicePrefix` deleted or renamed its instance variable `provisioning_state`
  - Model `PeeringServiceProvider` deleted or renamed its instance variable `service_provider_name`
  - Deleted or renamed model `ContactInfo`
  - Deleted or renamed model `Enum1`
  - Deleted or renamed model `Enum14`
  - Deleted or renamed model `Enum15`
  - Deleted or renamed model `Name`
  - Deleted or renamed model `OperationListResult`
  - Deleted or renamed model `PeerAsnListResult`
  - Deleted or renamed model `PeeringListResult`
  - Deleted or renamed model `PeeringLocationListResult`
  - Deleted or renamed model `PeeringServiceListResult`
  - Deleted or renamed model `PeeringServiceLocationListResult`
  - Deleted or renamed model `PeeringServicePrefixListResult`
  - Deleted or renamed model `PeeringServiceProviderListResult`
  - Method `LegacyPeeringsOperations.list` changed its parameter `peering_location` from `positional_or_keyword` to `keyword_only`
  - Method `LegacyPeeringsOperations.list` changed its parameter `kind` from `positional_or_keyword` to `keyword_only`
  - Method `PeeringLocationsOperations.list` changed its parameter `kind` from `positional_or_keyword` to `keyword_only`
  - Method `PeeringLocationsOperations.list` changed its parameter `direct_peering_type` from `positional_or_keyword` to `keyword_only`
  - Deleted or renamed model `PeeringServicePrefixesOperations`

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
