# Release History

## 1.1.0 (2025-11-12)

### Features Added

  - Model `PaloAltoNetworksNgfwMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Client `PaloAltoNetworksNgfwMgmtClient` added operation group `palo_alto_networks_cloudngfw_operations`
  - Client `PaloAltoNetworksNgfwMgmtClient` added operation group `metrics_object_firewall`
  - Model `FirewallResource` added property `is_strata_cloud_managed`
  - Model `FirewallResource` added property `strata_cloud_manager_config`
  - Model `FirewallResourceUpdateProperties` added property `is_strata_cloud_managed`
  - Model `FirewallResourceUpdateProperties` added property `strata_cloud_manager_config`
  - Model `FirewallStatusResource` added property `is_strata_cloud_managed`
  - Model `FirewallStatusResource` added property `strata_cloud_manager_info`
  - Model `NetworkProfile` added property `trusted_ranges`
  - Model `NetworkProfile` added property `private_source_nat_rules_destination`
  - Added model `CloudManagerTenantList`
  - Added enum `EnableStatus`
  - Added model `MetricsObjectFirewallResource`
  - Added model `MetricsObjectFirewallResourceListResult`
  - Added model `ProductSerialNumberRequestStatus`
  - Added model `ProductSerialNumberStatus`
  - Added enum `ProductSerialStatusValues`
  - Added enum `RegistrationStatus`
  - Added model `StrataCloudManagerConfig`
  - Added model `StrataCloudManagerInfo`
  - Added model `SupportInfoModel`
  - Added operation group `MetricsObjectFirewallOperations`
  - Added operation group `PaloAltoNetworksCloudngfwOperationsOperations`

## 2.0.0b1 (2023-11-20)

### Features Added

  - Model NetworkProfile has a new parameter trusted_ranges

### Breaking Changes

  - Removed operation LocalRulestacksOperations.list_app_ids
  - Removed operation LocalRulestacksOperations.list_countries
  - Removed operation LocalRulestacksOperations.list_predefined_url_categories

## 1.0.0 (2023-07-14)

### Other Changes

  - First GA version

## 1.0.0b2 (2023-05-05)

### Features Added

  - Added operation group FirewallStatusOperations

### Other Changes

  - Fixed annotation about namespace

## 1.0.0b1 (2023-05-04)

* Initial Release
