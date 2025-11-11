# Release History

## 2.0.0 (2025-11-10)

### Features Added

  - Model `PaloAltoNetworksNgfwMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Client `PaloAltoNetworksNgfwMgmtClient` added method `send_request`
  - Client `PaloAltoNetworksNgfwMgmtClient` added operation group `metrics_object_firewall`
  - Client `PaloAltoNetworksNgfwMgmtClient` added operation group `palo_alto_networks_cloudngfw_operations`
  - Model `CertificateObjectGlobalRulestackResource` added property `properties`
  - Model `CertificateObjectLocalRulestackResource` added property `properties`
  - Model `FirewallResource` added property `properties`
  - Model `FirewallResourceUpdateProperties` added property `is_strata_cloud_managed`
  - Model `FirewallResourceUpdateProperties` added property `strata_cloud_manager_config`
  - Model `FirewallStatusResource` added property `properties`
  - Model `FqdnListGlobalRulestackResource` added property `properties`
  - Model `FqdnListLocalRulestackResource` added property `properties`
  - Model `GlobalRulestackResource` added property `properties`
  - Model `LocalRulesResource` added property `properties`
  - Model `LocalRulestackResource` added property `properties`
  - Model `NetworkProfile` added property `trusted_ranges`
  - Model `NetworkProfile` added property `private_source_nat_rules_destination`
  - Model `PostRulesResource` added property `properties`
  - Model `PreRulesResource` added property `properties`
  - Model `PrefixListGlobalRulestackResource` added property `properties`
  - Model `PrefixListResource` added property `properties`
  - Added model `CertificateObject`
  - Added model `CloudManagerTenantList`
  - Added enum `EnableStatus`
  - Added model `FirewallDeploymentProperties`
  - Added model `FirewallStatusProperty`
  - Added model `FqdnObject`
  - Added model `MetricsObject`
  - Added model `MetricsObjectFirewallResource`
  - Added model `PrefixObject`
  - Added model `ProductSerialNumberRequestStatus`
  - Added model `ProductSerialNumberStatus`
  - Added enum `ProductSerialStatusValues`
  - Added enum `RegistrationStatus`
  - Added model `RuleEntry`
  - Added model `RulestackProperties`
  - Added model `StrataCloudManagerConfig`
  - Added model `StrataCloudManagerInfo`
  - Added model `SupportInfoModel`
  - Added operation group `MetricsObjectFirewallOperations`
  - Added operation group `PaloAltoNetworksCloudngfwOperationsOperations`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. And please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Model `CertificateObjectGlobalRulestackResource` instance variables `certificate_signer_resource_id`, `certificate_self_signed`, `audit_comment`, `description`, `etag`, and `provisioning_state` have been moved under property `properties`
  - Model `CertificateObjectLocalRulestackResource` instance variables `certificate_signer_resource_id`, `certificate_self_signed`, `audit_comment`, `description`, `etag`, and `provisioning_state` have been moved under property `properties`
  - Model `FirewallResource` instance variables `pan_etag`, `network_profile`, `is_panorama_managed`, `panorama_config`, `associated_rulestack`, `dns_settings`, `front_end_settings`, `provisioning_state`, `plan_data`, and `marketplace_details` have been moved under property `properties`
  - Model `FirewallStatusResource` instance variables `is_panorama_managed`, `health_status`, `health_reason`, `panorama_status`, and `provisioning_state` have been moved under property `properties`
  - Model `FqdnListGlobalRulestackResource` instance variables `description`, `fqdn_list`, `etag`, `audit_comment`, and `provisioning_state` have been moved under property `properties`
  - Model `FqdnListLocalRulestackResource` instance variables `description`, `fqdn_list`, `etag`, `audit_comment`, and `provisioning_state` have been moved under property `properties`
  - Model `GlobalRulestackResource` instance variables `pan_etag`, `pan_location`, `scope`, `associated_subscriptions`, `description`, `default_mode`, `min_app_id_version`, `provisioning_state`, and `security_services` have been moved under property `properties`
  - Model `LocalRulesResource` instance variables `etag`, `rule_name`, `priority`, `description`, `rule_state`, `source`, `negate_source`, `destination`, `negate_destination`, `applications`, `category`, `protocol`, `protocol_port_list`, `inbound_inspection_certificate`, `audit_comment`, `action_type`, `enable_logging`, `decryption_rule_type`, `tags`, and `provisioning_state` have been moved under property `properties`
  - Model `LocalRulestackResource` instance variables `pan_etag`, `pan_location`, `scope`, `associated_subscriptions`, `description`, `default_mode`, `min_app_id_version`, `provisioning_state`, and `security_services` have been moved under property `properties`
  - Model `PostRulesResource` instance variables `etag`, `rule_name`, `priority`, `description`, `rule_state`, `source`, `negate_source`, `destination`, `negate_destination`, `applications`, `category`, `protocol`, `protocol_port_list`, `inbound_inspection_certificate`, `audit_comment`, `action_type`, `enable_logging`, `decryption_rule_type`, `tags`, and `provisioning_state` have been moved under property `properties`
  - Model `PreRulesResource` instance variables `etag`, `rule_name`, `priority`, `description`, `rule_state`, `source`, `negate_source`, `destination`, `negate_destination`, `applications`, `category`, `protocol`, `protocol_port_list`, `inbound_inspection_certificate`, `audit_comment`, `action_type`, `enable_logging`, `decryption_rule_type`, `tags`, and `provisioning_state` have been moved under property `properties`
  - Model `PrefixListGlobalRulestackResource` instance variables `description`, `prefix_list`, `etag`, `audit_comment`, and `provisioning_state` have been moved under property `properties`
  - Model `PrefixListResource` instance variables `description`, `prefix_list`, `etag`, `audit_comment`, and `provisioning_state` have been moved under property `properties`
  - Method `FirewallsOperations.get_support_info` changed its parameter `email` from `positional_or_keyword` to `keyword_only`
  - Method `GlobalRulestackOperations.list_advanced_security_objects` changed its parameter `type` from `positional_or_keyword` to `keyword_only`
  - Method `GlobalRulestackOperations.list_app_ids` changed its parameter `app_id_version` from `positional_or_keyword` to `keyword_only`
  - Method `GlobalRulestackOperations.list_app_ids` changed its parameter `app_prefix` from `positional_or_keyword` to `keyword_only`
  - Method `GlobalRulestackOperations.list_security_services` changed its parameter `type` from `positional_or_keyword` to `keyword_only`
  - Method `LocalRulesOperations.get_counters` changed its parameter `firewall_name` from `positional_or_keyword` to `keyword_only`
  - Method `LocalRulesOperations.refresh_counters` changed its parameter `firewall_name` from `positional_or_keyword` to `keyword_only`
  - Method `LocalRulesOperations.reset_counters` changed its parameter `firewall_name` from `positional_or_keyword` to `keyword_only`
  - Method `LocalRulestacksOperations.get_support_info` changed its parameter `email` from `positional_or_keyword` to `keyword_only`
  - Method `LocalRulestacksOperations.list_advanced_security_objects` changed its parameter `type` from `positional_or_keyword` to `keyword_only`
  - Method `LocalRulestacksOperations.list_app_ids` changed its parameter `app_id_version` from `positional_or_keyword` to `keyword_only`
  - Method `LocalRulestacksOperations.list_app_ids` changed its parameter `app_prefix` from `positional_or_keyword` to `keyword_only`
  - Method `LocalRulestacksOperations.list_security_services` changed its parameter `type` from `positional_or_keyword` to `keyword_only`
  - Method `PostRulesOperations.get_counters` changed its parameter `firewall_name` from `positional_or_keyword` to `keyword_only`
  - Method `PostRulesOperations.refresh_counters` changed its parameter `firewall_name` from `positional_or_keyword` to `keyword_only`
  - Method `PostRulesOperations.reset_counters` changed its parameter `firewall_name` from `positional_or_keyword` to `keyword_only`
  - Method `PreRulesOperations.get_counters` changed its parameter `firewall_name` from `positional_or_keyword` to `keyword_only`
  - Method `PreRulesOperations.refresh_counters` changed its parameter `firewall_name` from `positional_or_keyword` to `keyword_only`
  - Method `PreRulesOperations.reset_counters` changed its parameter `firewall_name` from `positional_or_keyword` to `keyword_only`

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
