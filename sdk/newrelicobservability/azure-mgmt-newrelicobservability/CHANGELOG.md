# Release History

## 2.0.0b1 (2025-11-17)

### Features Added

  - Model `NewRelicObservabilityMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Client `NewRelicObservabilityMgmtClient` added operation group `saa_s`
  - Model `MarketplaceSaaSInfo` added property `publisher_id`
  - Model `MarketplaceSaaSInfo` added property `offer_id`
  - Model `NewRelicMonitorResource` added property `saa_s_data`
  - Model `NewRelicMonitorResourceUpdate` added property `saa_s_data`
  - Added model `ActivateSaaSParameterRequest`
  - Added model `LatestLinkedSaaSResponse`
  - Added model `ResubscribeProperties`
  - Added model `SaaSData`
  - Added model `SaaSResourceDetailsResponse`
  - Model `MonitoredSubscriptionsOperations` added method `begin_create_or_update`
  - Model `MonitorsOperations` added method `begin_link_saa_s`
  - Model `MonitorsOperations` added method `begin_resubscribe`
  - Model `MonitorsOperations` added method `begin_update`
  - Model `MonitorsOperations` added method `latest_linked_saa_s`
  - Model `MonitorsOperations` added method `refresh_ingestion_key`
  - Added operation group `SaaSOperations`

### Breaking Changes

  - Deleted or renamed model `BillingCycle`
  - Deleted or renamed method `MonitoredSubscriptionsOperations.begin_createor_update`
  - Deleted or renamed method `MonitorsOperations.update`

## 1.1.0 (2024-03-18)

### Features Added

  - Added operation MonitorsOperations.list_linked_resources
  - Added operation group BillingInfoOperations
  - Added operation group ConnectedPartnerResourcesOperations
  - Added operation group MonitoredSubscriptionsOperations
  - Model NewRelicMonitorResource has a new parameter saa_s_azure_subscription_status
  - Model NewRelicMonitorResource has a new parameter subscription_state

## 1.0.0 (2023-05-20)

### Other Changes

  - First GA

## 1.0.0b1 (2023-03-24)

* Initial Release
