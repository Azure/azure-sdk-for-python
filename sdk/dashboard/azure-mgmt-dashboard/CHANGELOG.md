# Release History

## 2.0.0 (2025-10-10)

### Features Added

  - Model `DashboardManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `DashboardManagementClient` added method `send_request`
  - Client `DashboardManagementClient` added operation group `integration_fabrics`
  - Client `DashboardManagementClient` added operation group `managed_dashboards`
  - Model `GrafanaAvailablePlugin` added property `type`
  - Model `GrafanaAvailablePlugin` added property `author`
  - Model `GrafanaConfigurations` added property `snapshots`
  - Model `GrafanaConfigurations` added property `users`
  - Model `GrafanaConfigurations` added property `security`
  - Model `GrafanaConfigurations` added property `unified_alerting_screenshots`
  - Model `ManagedGrafanaProperties` added property `creator_can_admin`
  - Model `ManagedGrafanaPropertiesUpdateParameters` added property `creator_can_admin`
  - Model `ResourceSku` added property `size`
  - Added enum `CreatorCanAdmin`
  - Added model `IntegrationFabric`
  - Added model `IntegrationFabricProperties`
  - Added model `IntegrationFabricPropertiesUpdateParameters`
  - Added model `IntegrationFabricUpdateParameters`
  - Added model `ManagedDashboard`
  - Added model `ManagedDashboardProperties`
  - Added model `ManagedDashboardUpdateParameters`
  - Added model `ProxyResource`
  - Added model `Security`
  - Added enum `Size`
  - Added model `Snapshots`
  - Added model `UnifiedAlertingScreenshots`
  - Added model `Users`
  - Model `GrafanaOperations` added method `begin_update`
  - Added operation group `IntegrationFabricsOperations`
  - Added operation group `ManagedDashboardsOperations`

### Breaking Changes

  - Deleted or renamed model `ManagedGrafanaListResponse`
  - Deleted or renamed model `ManagedPrivateEndpointModelListResponse`
  - Deleted or renamed method `GrafanaOperations.update`

## 2.0.0b1 (2025-07-31)

### Features Added

  - Client `DashboardManagementClient` added operation group `integration_fabrics`
  - Client `DashboardManagementClient` added operation group `managed_dashboards`
  - Model `GrafanaConfigurations` added property `snapshots`
  - Model `GrafanaConfigurations` added property `users`
  - Model `GrafanaConfigurations` added property `security`
  - Model `GrafanaConfigurations` added property `unified_alerting_screenshots`
  - Added model `IntegrationFabric`
  - Added model `IntegrationFabricProperties`
  - Added model `IntegrationFabricPropertiesUpdateParameters`
  - Added model `IntegrationFabricUpdateParameters`
  - Added model `ManagedDashboard`
  - Added model `ManagedDashboardProperties`
  - Added model `ManagedDashboardUpdateParameters`
  - Added model `ProxyResource`
  - Added model `Security`
  - Added model `Snapshots`
  - Added model `UnifiedAlertingScreenshots`
  - Added model `Users`
  - Operation group `GrafanaOperations` added method `begin_update`
  - Added operation group `IntegrationFabricsOperations`
  - Added operation group `ManagedDashboardsOperations`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. And please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - Deleted or renamed model `ManagedGrafanaListResponse`
  - Deleted or renamed model `ManagedPrivateEndpointModelListResponse`
  - Deleted or renamed method `GrafanaOperations.update`

## 1.1.0 (2023-11-20)

### Features Added

  - Added operation GrafanaOperations.check_enterprise_details
  - Added operation GrafanaOperations.fetch_available_plugins
  - Added operation group ManagedPrivateEndpointsOperations
  - Model ManagedGrafanaProperties has a new parameter enterprise_configurations
  - Model ManagedGrafanaProperties has a new parameter grafana_configurations
  - Model ManagedGrafanaProperties has a new parameter grafana_major_version
  - Model ManagedGrafanaProperties has a new parameter grafana_plugins
  - Model ManagedGrafanaPropertiesUpdateParameters has a new parameter enterprise_configurations
  - Model ManagedGrafanaPropertiesUpdateParameters has a new parameter grafana_configurations
  - Model ManagedGrafanaPropertiesUpdateParameters has a new parameter grafana_major_version
  - Model ManagedGrafanaPropertiesUpdateParameters has a new parameter grafana_plugins
  - Model ManagedGrafanaUpdateParameters has a new parameter sku

## 1.1.0b1 (2022-12-26)

### Other Changes

  - Added generated samples in github repo
  - Drop support for python<3.7.0

## 1.0.0 (2022-08-17)

**Features**

  - Added operation group PrivateEndpointConnectionsOperations
  - Added operation group PrivateLinkResourcesOperations
  - Model ManagedGrafanaProperties has a new parameter api_key
  - Model ManagedGrafanaProperties has a new parameter deterministic_outbound_ip
  - Model ManagedGrafanaProperties has a new parameter grafana_integrations
  - Model ManagedGrafanaProperties has a new parameter outbound_i_ps
  - Model ManagedGrafanaProperties has a new parameter private_endpoint_connections
  - Model ManagedGrafanaProperties has a new parameter public_network_access
  - Model ManagedGrafanaUpdateParameters has a new parameter properties

## 1.0.0b2 (2022-04-13)

**Features**

  - Add a default value to base_url in DashboardManagementClient

## 1.0.0b1 (2022-04-07)

* Initial Release
