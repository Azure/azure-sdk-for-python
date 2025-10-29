# Release History

## 2.0.0 (2025-10-29)

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
  - Added model `MetricsObjectFirewallOperations`
  - Added model `PaloAltoNetworksCloudngfwOperationsOperations`

### Breaking Changes

  - Method `LocalRulestacksOperations.list_app_ids` changed from `asynchronous` to `synchronous`
  - Method `LocalRulestacksOperations.list_countries` changed from `asynchronous` to `synchronous`
  - Method `LocalRulestacksOperations.list_predefined_url_categories` changed from `asynchronous` to `synchronous`
  - Model `CertificateObjectGlobalRulestackResource` deleted or renamed its instance variable `certificate_signer_resource_id`
  - Model `CertificateObjectGlobalRulestackResource` deleted or renamed its instance variable `certificate_self_signed`
  - Model `CertificateObjectGlobalRulestackResource` deleted or renamed its instance variable `audit_comment`
  - Model `CertificateObjectGlobalRulestackResource` deleted or renamed its instance variable `description`
  - Model `CertificateObjectGlobalRulestackResource` deleted or renamed its instance variable `etag`
  - Model `CertificateObjectGlobalRulestackResource` deleted or renamed its instance variable `provisioning_state`
  - Model `CertificateObjectLocalRulestackResource` deleted or renamed its instance variable `certificate_signer_resource_id`
  - Model `CertificateObjectLocalRulestackResource` deleted or renamed its instance variable `certificate_self_signed`
  - Model `CertificateObjectLocalRulestackResource` deleted or renamed its instance variable `audit_comment`
  - Model `CertificateObjectLocalRulestackResource` deleted or renamed its instance variable `description`
  - Model `CertificateObjectLocalRulestackResource` deleted or renamed its instance variable `etag`
  - Model `CertificateObjectLocalRulestackResource` deleted or renamed its instance variable `provisioning_state`
  - Model `FirewallResource` deleted or renamed its instance variable `pan_etag`
  - Model `FirewallResource` deleted or renamed its instance variable `network_profile`
  - Model `FirewallResource` deleted or renamed its instance variable `is_panorama_managed`
  - Model `FirewallResource` deleted or renamed its instance variable `panorama_config`
  - Model `FirewallResource` deleted or renamed its instance variable `associated_rulestack`
  - Model `FirewallResource` deleted or renamed its instance variable `dns_settings`
  - Model `FirewallResource` deleted or renamed its instance variable `front_end_settings`
  - Model `FirewallResource` deleted or renamed its instance variable `provisioning_state`
  - Model `FirewallResource` deleted or renamed its instance variable `plan_data`
  - Model `FirewallResource` deleted or renamed its instance variable `marketplace_details`
  - Model `FirewallStatusResource` deleted or renamed its instance variable `is_panorama_managed`
  - Model `FirewallStatusResource` deleted or renamed its instance variable `health_status`
  - Model `FirewallStatusResource` deleted or renamed its instance variable `health_reason`
  - Model `FirewallStatusResource` deleted or renamed its instance variable `panorama_status`
  - Model `FirewallStatusResource` deleted or renamed its instance variable `provisioning_state`
  - Model `FqdnListGlobalRulestackResource` deleted or renamed its instance variable `description`
  - Model `FqdnListGlobalRulestackResource` deleted or renamed its instance variable `fqdn_list`
  - Model `FqdnListGlobalRulestackResource` deleted or renamed its instance variable `etag`
  - Model `FqdnListGlobalRulestackResource` deleted or renamed its instance variable `audit_comment`
  - Model `FqdnListGlobalRulestackResource` deleted or renamed its instance variable `provisioning_state`
  - Model `FqdnListLocalRulestackResource` deleted or renamed its instance variable `description`
  - Model `FqdnListLocalRulestackResource` deleted or renamed its instance variable `fqdn_list`
  - Model `FqdnListLocalRulestackResource` deleted or renamed its instance variable `etag`
  - Model `FqdnListLocalRulestackResource` deleted or renamed its instance variable `audit_comment`
  - Model `FqdnListLocalRulestackResource` deleted or renamed its instance variable `provisioning_state`
  - Model `GlobalRulestackResource` deleted or renamed its instance variable `pan_etag`
  - Model `GlobalRulestackResource` deleted or renamed its instance variable `pan_location`
  - Model `GlobalRulestackResource` deleted or renamed its instance variable `scope`
  - Model `GlobalRulestackResource` deleted or renamed its instance variable `associated_subscriptions`
  - Model `GlobalRulestackResource` deleted or renamed its instance variable `description`
  - Model `GlobalRulestackResource` deleted or renamed its instance variable `default_mode`
  - Model `GlobalRulestackResource` deleted or renamed its instance variable `min_app_id_version`
  - Model `GlobalRulestackResource` deleted or renamed its instance variable `provisioning_state`
  - Model `GlobalRulestackResource` deleted or renamed its instance variable `security_services`
  - Model `LocalRulesResource` deleted or renamed its instance variable `etag`
  - Model `LocalRulesResource` deleted or renamed its instance variable `rule_name`
  - Model `LocalRulesResource` deleted or renamed its instance variable `priority`
  - Model `LocalRulesResource` deleted or renamed its instance variable `description`
  - Model `LocalRulesResource` deleted or renamed its instance variable `rule_state`
  - Model `LocalRulesResource` deleted or renamed its instance variable `source`
  - Model `LocalRulesResource` deleted or renamed its instance variable `negate_source`
  - Model `LocalRulesResource` deleted or renamed its instance variable `destination`
  - Model `LocalRulesResource` deleted or renamed its instance variable `negate_destination`
  - Model `LocalRulesResource` deleted or renamed its instance variable `applications`
  - Model `LocalRulesResource` deleted or renamed its instance variable `category`
  - Model `LocalRulesResource` deleted or renamed its instance variable `protocol`
  - Model `LocalRulesResource` deleted or renamed its instance variable `protocol_port_list`
  - Model `LocalRulesResource` deleted or renamed its instance variable `inbound_inspection_certificate`
  - Model `LocalRulesResource` deleted or renamed its instance variable `audit_comment`
  - Model `LocalRulesResource` deleted or renamed its instance variable `action_type`
  - Model `LocalRulesResource` deleted or renamed its instance variable `enable_logging`
  - Model `LocalRulesResource` deleted or renamed its instance variable `decryption_rule_type`
  - Model `LocalRulesResource` deleted or renamed its instance variable `tags`
  - Model `LocalRulesResource` deleted or renamed its instance variable `provisioning_state`
  - Model `LocalRulestackResource` deleted or renamed its instance variable `pan_etag`
  - Model `LocalRulestackResource` deleted or renamed its instance variable `pan_location`
  - Model `LocalRulestackResource` deleted or renamed its instance variable `scope`
  - Model `LocalRulestackResource` deleted or renamed its instance variable `associated_subscriptions`
  - Model `LocalRulestackResource` deleted or renamed its instance variable `description`
  - Model `LocalRulestackResource` deleted or renamed its instance variable `default_mode`
  - Model `LocalRulestackResource` deleted or renamed its instance variable `min_app_id_version`
  - Model `LocalRulestackResource` deleted or renamed its instance variable `provisioning_state`
  - Model `LocalRulestackResource` deleted or renamed its instance variable `security_services`
  - Model `PostRulesResource` deleted or renamed its instance variable `etag`
  - Model `PostRulesResource` deleted or renamed its instance variable `rule_name`
  - Model `PostRulesResource` deleted or renamed its instance variable `priority`
  - Model `PostRulesResource` deleted or renamed its instance variable `description`
  - Model `PostRulesResource` deleted or renamed its instance variable `rule_state`
  - Model `PostRulesResource` deleted or renamed its instance variable `source`
  - Model `PostRulesResource` deleted or renamed its instance variable `negate_source`
  - Model `PostRulesResource` deleted or renamed its instance variable `destination`
  - Model `PostRulesResource` deleted or renamed its instance variable `negate_destination`
  - Model `PostRulesResource` deleted or renamed its instance variable `applications`
  - Model `PostRulesResource` deleted or renamed its instance variable `category`
  - Model `PostRulesResource` deleted or renamed its instance variable `protocol`
  - Model `PostRulesResource` deleted or renamed its instance variable `protocol_port_list`
  - Model `PostRulesResource` deleted or renamed its instance variable `inbound_inspection_certificate`
  - Model `PostRulesResource` deleted or renamed its instance variable `audit_comment`
  - Model `PostRulesResource` deleted or renamed its instance variable `action_type`
  - Model `PostRulesResource` deleted or renamed its instance variable `enable_logging`
  - Model `PostRulesResource` deleted or renamed its instance variable `decryption_rule_type`
  - Model `PostRulesResource` deleted or renamed its instance variable `tags`
  - Model `PostRulesResource` deleted or renamed its instance variable `provisioning_state`
  - Model `PreRulesResource` deleted or renamed its instance variable `etag`
  - Model `PreRulesResource` deleted or renamed its instance variable `rule_name`
  - Model `PreRulesResource` deleted or renamed its instance variable `priority`
  - Model `PreRulesResource` deleted or renamed its instance variable `description`
  - Model `PreRulesResource` deleted or renamed its instance variable `rule_state`
  - Model `PreRulesResource` deleted or renamed its instance variable `source`
  - Model `PreRulesResource` deleted or renamed its instance variable `negate_source`
  - Model `PreRulesResource` deleted or renamed its instance variable `destination`
  - Model `PreRulesResource` deleted or renamed its instance variable `negate_destination`
  - Model `PreRulesResource` deleted or renamed its instance variable `applications`
  - Model `PreRulesResource` deleted or renamed its instance variable `category`
  - Model `PreRulesResource` deleted or renamed its instance variable `protocol`
  - Model `PreRulesResource` deleted or renamed its instance variable `protocol_port_list`
  - Model `PreRulesResource` deleted or renamed its instance variable `inbound_inspection_certificate`
  - Model `PreRulesResource` deleted or renamed its instance variable `audit_comment`
  - Model `PreRulesResource` deleted or renamed its instance variable `action_type`
  - Model `PreRulesResource` deleted or renamed its instance variable `enable_logging`
  - Model `PreRulesResource` deleted or renamed its instance variable `decryption_rule_type`
  - Model `PreRulesResource` deleted or renamed its instance variable `tags`
  - Model `PreRulesResource` deleted or renamed its instance variable `provisioning_state`
  - Model `PrefixListGlobalRulestackResource` deleted or renamed its instance variable `description`
  - Model `PrefixListGlobalRulestackResource` deleted or renamed its instance variable `prefix_list`
  - Model `PrefixListGlobalRulestackResource` deleted or renamed its instance variable `etag`
  - Model `PrefixListGlobalRulestackResource` deleted or renamed its instance variable `audit_comment`
  - Model `PrefixListGlobalRulestackResource` deleted or renamed its instance variable `provisioning_state`
  - Model `PrefixListResource` deleted or renamed its instance variable `description`
  - Model `PrefixListResource` deleted or renamed its instance variable `prefix_list`
  - Model `PrefixListResource` deleted or renamed its instance variable `etag`
  - Model `PrefixListResource` deleted or renamed its instance variable `audit_comment`
  - Model `PrefixListResource` deleted or renamed its instance variable `provisioning_state`
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
