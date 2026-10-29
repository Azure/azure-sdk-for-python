# Release History

## 2.0.0b2 (2026-07-07)

### Features Added

  - Client `PaloAltoNetworksNgfwMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Client `PaloAltoNetworksNgfwMgmtClient` added method `send_request`
  - Client `PaloAltoNetworksNgfwMgmtClient` added operation group `custom_capture_configurations_firewall_resources`
  - Client `PaloAltoNetworksNgfwMgmtClient` added operation group `metrics_object_firewall`
  - Client `PaloAltoNetworksNgfwMgmtClient` added operation group `palo_alto_networks_cloudngfw_operations`
  - Model `FirewallResourceUpdateProperties` added property `is_strata_cloud_managed`
  - Model `FirewallResourceUpdateProperties` added property `strata_cloud_manager_config`
  - Model `NetworkProfile` added property `private_source_nat_rules_destination`
  - Added model `CloudManagerTenantList`
  - Added model `CustomCaptureConfigurationsFilter`
  - Added model `CustomCaptureConfigurationsFirewallResource`
  - Added model `CustomCaptureConfigurationsProperties`
  - Added enum `CustomCaptureConfigurationsProtocol`
  - Added enum `CustomCaptureConfigurationsStage`
  - Added enum `CustomCaptureConfigurationsStatus`
  - Added enum `EnableStatus`
  - Added model `MetricsObject`
  - Added model `MetricsObjectFirewallResource`
  - Added model `ProductSerialNumberRequestStatus`
  - Added model `ProductSerialNumberStatus`
  - Added enum `ProductSerialStatusValues`
  - Added enum `RegistrationStatus`
  - Added model `StrataCloudManagerConfig`
  - Added model `StrataCloudManagerInfo`
  - Added model `SupportInfoModel`
  - Operation group `LocalRulestacksOperations` added method `list_app_ids`
  - Operation group `LocalRulestacksOperations` added method `list_countries`
  - Operation group `LocalRulestacksOperations` added method `list_predefined_url_categories`
  - Added operation group `CustomCaptureConfigurationsFirewallResourcesOperations`
  - Added operation group `MetricsObjectFirewallOperations`
  - Added operation group `PaloAltoNetworksCloudngfwOperationsOperations`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Model `CertificateObjectGlobalRulestackResource` moved instance variable `certificate_signer_resource_id`, `certificate_self_signed`, `audit_comment`, `description`, `etag` and `provisioning_state` under property `properties` whose type is `CertificateObject`
  - Model `CertificateObjectLocalRulestackResource` moved instance variable `certificate_signer_resource_id`, `certificate_self_signed`, `audit_comment`, `description`, `etag` and `provisioning_state` under property `properties` whose type is `CertificateObject`
  - Model `FirewallResource` moved instance variable `pan_etag`, `network_profile`, `is_panorama_managed`, `panorama_config`, `associated_rulestack`, `dns_settings`, `front_end_settings`, `provisioning_state`, `plan_data` and `marketplace_details` under property `properties` whose type is `FirewallDeploymentProperties`
  - Model `FirewallStatusResource` moved instance variable `is_panorama_managed`, `health_status`, `health_reason`, `panorama_status` and `provisioning_state` under property `properties` whose type is `FirewallStatusProperty`
  - Model `FqdnListGlobalRulestackResource` moved instance variable `description`, `fqdn_list`, `etag`, `audit_comment` and `provisioning_state` under property `properties` whose type is `FqdnObject`
  - Model `FqdnListLocalRulestackResource` moved instance variable `description`, `fqdn_list`, `etag`, `audit_comment` and `provisioning_state` under property `properties` whose type is `FqdnObject`
  - Model `GlobalRulestackResource` moved instance variable `pan_etag`, `pan_location`, `scope`, `associated_subscriptions`, `description`, `default_mode`, `min_app_id_version`, `provisioning_state` and `security_services` under property `properties` whose type is `RulestackProperties`
  - Model `LocalRulesResource` moved instance variable `etag`, `rule_name`, `priority`, `description`, `rule_state`, `source`, `negate_source`, `destination`, `negate_destination`, `applications`, `category`, `protocol`, `protocol_port_list`, `inbound_inspection_certificate`, `audit_comment`, `action_type`, `enable_logging`, `decryption_rule_type`, `tags` and `provisioning_state` under property `properties` whose type is `RuleEntry`
  - Model `LocalRulestackResource` moved instance variable `pan_etag`, `pan_location`, `scope`, `associated_subscriptions`, `description`, `default_mode`, `min_app_id_version`, `provisioning_state` and `security_services` under property `properties` whose type is `RulestackProperties`
  - Model `PostRulesResource` moved instance variable `etag`, `rule_name`, `priority`, `description`, `rule_state`, `source`, `negate_source`, `destination`, `negate_destination`, `applications`, `category`, `protocol`, `protocol_port_list`, `inbound_inspection_certificate`, `audit_comment`, `action_type`, `enable_logging`, `decryption_rule_type`, `tags` and `provisioning_state` under property `properties` whose type is `RuleEntry`
  - Model `PreRulesResource` moved instance variable `etag`, `rule_name`, `priority`, `description`, `rule_state`, `source`, `negate_source`, `destination`, `negate_destination`, `applications`, `category`, `protocol`, `protocol_port_list`, `inbound_inspection_certificate`, `audit_comment`, `action_type`, `enable_logging`, `decryption_rule_type`, `tags` and `provisioning_state` under property `properties` whose type is `RuleEntry`
  - Model `PrefixListGlobalRulestackResource` moved instance variable `description`, `prefix_list`, `etag`, `audit_comment` and `provisioning_state` under property `properties` whose type is `PrefixObject`
  - Model `PrefixListResource` moved instance variable `description`, `prefix_list`, `etag`, `audit_comment` and `provisioning_state` under property `properties` whose type is `PrefixObject`
  - Method `FirewallsOperations.get_support_info` changed its parameter `email` from `positional_or_keyword` to `keyword_only`
  - Method `GlobalRulestackOperations.list_advanced_security_objects` changed its parameter `type` from `positional_or_keyword` to `keyword_only`
  - Method `GlobalRulestackOperations.list_app_ids` changed its parameter `app_id_version`/`app_prefix` from `positional_or_keyword` to `keyword_only`
  - Method `GlobalRulestackOperations.list_security_services` changed its parameter `type` from `positional_or_keyword` to `keyword_only`
  - Method `LocalRulesOperations.get_counters` changed its parameter `firewall_name` from `positional_or_keyword` to `keyword_only`
  - Method `LocalRulesOperations.refresh_counters` changed its parameter `firewall_name` from `positional_or_keyword` to `keyword_only`
  - Method `LocalRulesOperations.reset_counters` changed its parameter `firewall_name` from `positional_or_keyword` to `keyword_only`
  - Method `LocalRulestacksOperations.get_support_info` changed its parameter `email` from `positional_or_keyword` to `keyword_only`
  - Method `LocalRulestacksOperations.list_advanced_security_objects` changed its parameter `type` from `positional_or_keyword` to `keyword_only`
  - Method `LocalRulestacksOperations.list_security_services` changed its parameter `type` from `positional_or_keyword` to `keyword_only`
  - Method `PostRulesOperations.get_counters` changed its parameter `firewall_name` from `positional_or_keyword` to `keyword_only`
  - Method `PostRulesOperations.refresh_counters` changed its parameter `firewall_name` from `positional_or_keyword` to `keyword_only`
  - Method `PostRulesOperations.reset_counters` changed its parameter `firewall_name` from `positional_or_keyword` to `keyword_only`
  - Method `PreRulesOperations.get_counters` changed its parameter `firewall_name` from `positional_or_keyword` to `keyword_only`
  - Method `PreRulesOperations.refresh_counters` changed its parameter `firewall_name` from `positional_or_keyword` to `keyword_only`
  - Method `PreRulesOperations.reset_counters` changed its parameter `firewall_name` from `positional_or_keyword` to `keyword_only`

### Other Changes

  - Deleted model `CertificateObjectGlobalRulestackResourceListResult`/`CertificateObjectLocalRulestackResourceListResult`/`FirewallResourceListResult`/`FirewallStatusResourceListResult`/`FqdnListGlobalRulestackResourceListResult`/`FqdnListLocalRulestackResourceListResult`/`GlobalRulestackResourceListResult`/`LocalRulesResourceListResult`/`LocalRulestackResourceListResult`/`OperationListResult`/`PostRulesResourceListResult`/`PreRulesResourceListResult`/`PrefixListGlobalRulestackResourceListResult`/`PrefixListResourceListResult` which actually were not used by SDK users

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
