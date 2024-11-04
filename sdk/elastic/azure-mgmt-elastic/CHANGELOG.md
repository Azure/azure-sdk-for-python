# Release History

## 1.1.0b4 (2024-10-23)

### Features Added

  - Model `MicrosoftElastic` added property `monitored_subscriptions`
  - Model `MicrosoftElastic` added property `billing_info`
  - Model `MicrosoftElastic` added property `connected_partner_resources`
  - Model `MicrosoftElastic` added property `open_ai`
  - Model `DeploymentInfoResponse` added property `elasticsearch_end_point`
  - Model `MarketplaceSaaSInfo` added property `marketplace_status`
  - Model `MarketplaceSaaSInfo` added property `billed_azure_subscription_id`
  - Model `MarketplaceSaaSInfo` added property `subscribed`
  - Model `MarketplaceSaaSInfoMarketplaceSubscription` added property `publisher_id`
  - Model `MarketplaceSaaSInfoMarketplaceSubscription` added property `offer_id`
  - Model `MonitorProperties` added property `plan_details`
  - Model `MonitorProperties` added property `subscription_state`
  - Model `MonitorProperties` added property `saa_s_azure_subscription_status`
  - Model `MonitorProperties` added property `source_campaign_name`
  - Model `MonitorProperties` added property `source_campaign_id`
  - Added model `BillingInfoResponse`
  - Added model `ConnectedPartnerResourceProperties`
  - Added model `ConnectedPartnerResourcesListFormat`
  - Added model `ConnectedPartnerResourcesListResponse`
  - Added model `ElasticOrganizationToAzureSubscriptionMappingResponse`
  - Added model `ElasticOrganizationToAzureSubscriptionMappingResponseProperties`
  - Added model `ErrorAdditionalInfo`
  - Added model `ErrorDetail`
  - Added model `ErrorResponse`
  - Added model `MonitoredSubscription`
  - Added model `MonitoredSubscriptionProperties`
  - Added model `MonitoredSubscriptionPropertiesList`
  - Added model `OpenAIIntegrationProperties`
  - Added model `OpenAIIntegrationRPModel`
  - Added model `OpenAIIntegrationRPModelListResponse`
  - Added model `OpenAIIntegrationStatusResponse`
  - Added model `OpenAIIntegrationStatusResponseProperties`
  - Added enum `Operation`
  - Added model `PartnerBillingEntity`
  - Added model `PlanDetails`
  - Added model `ResubscribeProperties`
  - Added enum `Status`
  - Added model `SubscriptionList`
  - Operation group `OrganizationsOperations` added method `begin_resubscribe`
  - Operation group `OrganizationsOperations` added method `get_elastic_to_azure_subscription_mapping`
  - Added operation group `BillingInfoOperations`
  - Added operation group `ConnectedPartnerResourcesOperations`
  - Added operation group `MonitoredSubscriptionsOperations`
  - Added operation group `OpenAIOperations`

### Breaking Changes

  - Renamed method `update` to `begin_update` in Operation group `MonitorsOperations`

## 1.1.0b3 (2023-05-22)

### Features Added

  - Added operation group ElasticVersionsOperations
  - Model MonitorProperties has a new parameter generate_api_key
  - Model UserApiKeyResponse has a new parameter properties

### Breaking Changes

  - Model ElasticMonitorResource no longer has parameter generate_api_key
  - Model UserApiKeyResponse no longer has parameter api_key
  - Operation OrganizationsOperations.get_api_key no longer has parameter resource_group_name

## 1.1.0b2 (2023-04-20)

### Features Added

  - Added operation group OrganizationsOperations
  - Model DeploymentInfoResponse has a new parameter deployment_url
  - Model DeploymentInfoResponse has a new parameter marketplace_saas_info
  - Model ElasticMonitorResource has a new parameter generate_api_key

## 1.1.0b1 (2022-11-08)

### Features Added

  - Added operation group AllTrafficFiltersOperations
  - Added operation group AssociateTrafficFilterOperations
  - Added operation group CreateAndAssociateIPFilterOperations
  - Added operation group CreateAndAssociatePLFilterOperations
  - Added operation group DetachAndDeleteTrafficFilterOperations
  - Added operation group DetachTrafficFilterOperations
  - Added operation group ExternalUserOperations
  - Added operation group ListAssociatedTrafficFiltersOperations
  - Added operation group MonitorOperations
  - Added operation group TrafficFiltersOperations
  - Added operation group UpgradableVersionsOperations
  - Model MonitorProperties has a new parameter version

## 1.0.0 (2021-08-04)

  - GA Release

## 1.0.0b1 (2021-05-08)

* Initial Release
