# Release History

## 14.0.0 (2026-05-20)

### Features Added

  - Client `CdnManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `CdnManagementClient` added method `send_request`
  - Model `AFDDomain` added property `properties`
  - Model `AFDDomainHttpsParameters` added property `cipher_suite_set_type`
  - Model `AFDDomainHttpsParameters` added property `customized_cipher_suite_set`
  - Model `AFDEndpoint` added property `properties`
  - Model `AFDEndpointUpdateParameters` added property `properties`
  - Model `AFDOrigin` added property `properties`
  - Model `AFDOriginGroup` added property `properties`
  - Model `AFDOriginGroupProperties` added property `authentication`
  - Model `AFDOriginGroupUpdatePropertiesParameters` added property `authentication`
  - Enum `AfdMinimumTlsVersion` added member `TLS13`
  - Model `CanMigrateResult` added property `properties`
  - Model `Endpoint` added property `properties`
  - Model `EndpointUpdateParameters` added property `properties`
  - Enum `MatchProcessingBehavior` added member `CONTINUE`
  - Model `Operation` added property `operation_properties`
  - Model `Origin` added property `properties`
  - Model `OriginGroup` added property `properties`
  - Model `ProfileUpdateParameters` added property `properties`
  - Model `Route` added property `properties`
  - Model `Rule` added property `properties`
  - Model `RuleSet` added property `properties`
  - Model `RuleSetProperties` added property `batch_mode`
  - Model `RuleSetProperties` added property `rules`
  - Model `Secret` added property `properties`
  - Model `SecurityPolicy` added property `properties`
  - Added model `AFDDomainHttpsCustomizedCipherSuiteSet`
  - Added enum `AfdCipherSuiteSetType`
  - Added enum `AfdCustomizedCipherSuiteForTls12`
  - Added enum `AfdCustomizedCipherSuiteForTls13`
  - Added model `BatchRuleProperties`
  - Added model `CanMigrateProperties`
  - Added model `CdnMigrationToAfdParameters`
  - Added model `CertificateSourceParameters`
  - Added enum `CertificateSourceParametersType`
  - Added enum `CreatedByType`
  - Added model `CustomDomainPropertiesParameters`
  - Added enum `DeliveryRuleActionName`
  - Added model `DeliveryRuleActionParameters`
  - Added enum `DeliveryRuleActionParametersType`
  - Added model `DeliveryRuleConditionParameters`
  - Added enum `DeliveryRuleConditionParametersType`
  - Added enum `IsDeviceMatchValue`
  - Added enum `KeyVaultSigningKeyParametersType`
  - Added model `MigrationEndpointMapping`
  - Added model `OperationProperties`
  - Added model `OriginAuthenticationProperties`
  - Added enum `OriginAuthenticationType`
  - Added model `ProfilePropertiesUpdateParameters`
  - Added enum `RequestMethodMatchValue`
  - Added enum `RequestSchemeMatchValue`
  - Added model `SecurityPolicyUpdateProperties`
  - Model `ProfilesOperations` added method `begin_cdn_can_migrate_to_afd`
  - Model `ProfilesOperations` added method `begin_cdn_migrate_to_afd`
  - Model `ProfilesOperations` added method `begin_migration_abort`
  - Model `RuleSetsOperations` added method `begin_create`

### Breaking Changes

  - Model `AFDDomain` deleted or renamed its instance variable `profile_name`
  - Model `AFDDomain` deleted or renamed its instance variable `tls_settings`
  - Model `AFDDomain` deleted or renamed its instance variable `azure_dns_zone`
  - Model `AFDDomain` deleted or renamed its instance variable `pre_validated_custom_domain_resource_id`
  - Model `AFDDomain` deleted or renamed its instance variable `provisioning_state`
  - Model `AFDDomain` deleted or renamed its instance variable `deployment_status`
  - Model `AFDDomain` deleted or renamed its instance variable `domain_validation_state`
  - Model `AFDDomain` deleted or renamed its instance variable `host_name`
  - Model `AFDDomain` deleted or renamed its instance variable `extended_properties`
  - Model `AFDDomain` deleted or renamed its instance variable `validation_properties`
  - Model `AFDDomainUpdateParameters` deleted or renamed its instance variable `profile_name`
  - Model `AFDDomainUpdateParameters` deleted or renamed its instance variable `tls_settings`
  - Model `AFDDomainUpdateParameters` deleted or renamed its instance variable `azure_dns_zone`
  - Model `AFDDomainUpdateParameters` deleted or renamed its instance variable `pre_validated_custom_domain_resource_id`
  - Model `AFDEndpoint` deleted or renamed its instance variable `profile_name`
  - Model `AFDEndpoint` deleted or renamed its instance variable `enabled_state`
  - Model `AFDEndpoint` deleted or renamed its instance variable `provisioning_state`
  - Model `AFDEndpoint` deleted or renamed its instance variable `deployment_status`
  - Model `AFDEndpoint` deleted or renamed its instance variable `host_name`
  - Model `AFDEndpoint` deleted or renamed its instance variable `auto_generated_domain_name_label_scope`
  - Model `AFDEndpointUpdateParameters` deleted or renamed its instance variable `profile_name`
  - Model `AFDEndpointUpdateParameters` deleted or renamed its instance variable `enabled_state`
  - Model `AFDOrigin` deleted or renamed its instance variable `origin_group_name`
  - Model `AFDOrigin` deleted or renamed its instance variable `azure_origin`
  - Model `AFDOrigin` deleted or renamed its instance variable `host_name`
  - Model `AFDOrigin` deleted or renamed its instance variable `http_port`
  - Model `AFDOrigin` deleted or renamed its instance variable `https_port`
  - Model `AFDOrigin` deleted or renamed its instance variable `origin_host_header`
  - Model `AFDOrigin` deleted or renamed its instance variable `priority`
  - Model `AFDOrigin` deleted or renamed its instance variable `weight`
  - Model `AFDOrigin` deleted or renamed its instance variable `shared_private_link_resource`
  - Model `AFDOrigin` deleted or renamed its instance variable `enabled_state`
  - Model `AFDOrigin` deleted or renamed its instance variable `enforce_certificate_name_check`
  - Model `AFDOrigin` deleted or renamed its instance variable `provisioning_state`
  - Model `AFDOrigin` deleted or renamed its instance variable `deployment_status`
  - Model `AFDOriginGroup` deleted or renamed its instance variable `profile_name`
  - Model `AFDOriginGroup` deleted or renamed its instance variable `load_balancing_settings`
  - Model `AFDOriginGroup` deleted or renamed its instance variable `health_probe_settings`
  - Model `AFDOriginGroup` deleted or renamed its instance variable `traffic_restoration_time_to_healed_or_new_endpoints_in_minutes`
  - Model `AFDOriginGroup` deleted or renamed its instance variable `session_affinity_state`
  - Model `AFDOriginGroup` deleted or renamed its instance variable `provisioning_state`
  - Model `AFDOriginGroup` deleted or renamed its instance variable `deployment_status`
  - Model `AFDOriginGroupUpdateParameters` deleted or renamed its instance variable `profile_name`
  - Model `AFDOriginGroupUpdateParameters` deleted or renamed its instance variable `load_balancing_settings`
  - Model `AFDOriginGroupUpdateParameters` deleted or renamed its instance variable `health_probe_settings`
  - Model `AFDOriginGroupUpdateParameters` deleted or renamed its instance variable `traffic_restoration_time_to_healed_or_new_endpoints_in_minutes`
  - Model `AFDOriginGroupUpdateParameters` deleted or renamed its instance variable `session_affinity_state`
  - Model `AFDOriginUpdateParameters` deleted or renamed its instance variable `origin_group_name`
  - Model `AFDOriginUpdateParameters` deleted or renamed its instance variable `azure_origin`
  - Model `AFDOriginUpdateParameters` deleted or renamed its instance variable `host_name`
  - Model `AFDOriginUpdateParameters` deleted or renamed its instance variable `http_port`
  - Model `AFDOriginUpdateParameters` deleted or renamed its instance variable `https_port`
  - Model `AFDOriginUpdateParameters` deleted or renamed its instance variable `origin_host_header`
  - Model `AFDOriginUpdateParameters` deleted or renamed its instance variable `priority`
  - Model `AFDOriginUpdateParameters` deleted or renamed its instance variable `weight`
  - Model `AFDOriginUpdateParameters` deleted or renamed its instance variable `shared_private_link_resource`
  - Model `AFDOriginUpdateParameters` deleted or renamed its instance variable `enabled_state`
  - Model `AFDOriginUpdateParameters` deleted or renamed its instance variable `enforce_certificate_name_check`
  - Model `CanMigrateResult` deleted or renamed its instance variable `can_migrate`
  - Model `CanMigrateResult` deleted or renamed its instance variable `default_sku`
  - Model `CanMigrateResult` deleted or renamed its instance variable `errors`
  - Model `CustomDomainParameters` deleted or renamed its instance variable `host_name`
  - Model `Endpoint` deleted or renamed its instance variable `origin_path`
  - Model `Endpoint` deleted or renamed its instance variable `content_types_to_compress`
  - Model `Endpoint` deleted or renamed its instance variable `origin_host_header`
  - Model `Endpoint` deleted or renamed its instance variable `is_compression_enabled`
  - Model `Endpoint` deleted or renamed its instance variable `is_http_allowed`
  - Model `Endpoint` deleted or renamed its instance variable `is_https_allowed`
  - Model `Endpoint` deleted or renamed its instance variable `query_string_caching_behavior`
  - Model `Endpoint` deleted or renamed its instance variable `optimization_type`
  - Model `Endpoint` deleted or renamed its instance variable `probe_path`
  - Model `Endpoint` deleted or renamed its instance variable `geo_filters`
  - Model `Endpoint` deleted or renamed its instance variable `default_origin_group`
  - Model `Endpoint` deleted or renamed its instance variable `url_signing_keys`
  - Model `Endpoint` deleted or renamed its instance variable `delivery_policy`
  - Model `Endpoint` deleted or renamed its instance variable `web_application_firewall_policy_link`
  - Model `Endpoint` deleted or renamed its instance variable `host_name`
  - Model `Endpoint` deleted or renamed its instance variable `origins`
  - Model `Endpoint` deleted or renamed its instance variable `origin_groups`
  - Model `Endpoint` deleted or renamed its instance variable `custom_domains`
  - Model `Endpoint` deleted or renamed its instance variable `resource_state`
  - Model `Endpoint` deleted or renamed its instance variable `provisioning_state`
  - Model `EndpointUpdateParameters` deleted or renamed its instance variable `origin_path`
  - Model `EndpointUpdateParameters` deleted or renamed its instance variable `content_types_to_compress`
  - Model `EndpointUpdateParameters` deleted or renamed its instance variable `origin_host_header`
  - Model `EndpointUpdateParameters` deleted or renamed its instance variable `is_compression_enabled`
  - Model `EndpointUpdateParameters` deleted or renamed its instance variable `is_http_allowed`
  - Model `EndpointUpdateParameters` deleted or renamed its instance variable `is_https_allowed`
  - Model `EndpointUpdateParameters` deleted or renamed its instance variable `query_string_caching_behavior`
  - Model `EndpointUpdateParameters` deleted or renamed its instance variable `optimization_type`
  - Model `EndpointUpdateParameters` deleted or renamed its instance variable `probe_path`
  - Model `EndpointUpdateParameters` deleted or renamed its instance variable `geo_filters`
  - Model `EndpointUpdateParameters` deleted or renamed its instance variable `default_origin_group`
  - Model `EndpointUpdateParameters` deleted or renamed its instance variable `url_signing_keys`
  - Model `EndpointUpdateParameters` deleted or renamed its instance variable `delivery_policy`
  - Model `EndpointUpdateParameters` deleted or renamed its instance variable `web_application_firewall_policy_link`
  - Deleted or renamed enum value `MatchProcessingBehavior.CONTINUE_ENUM`
  - Model `Operation` deleted or renamed its instance variable `service_specification`
  - Model `Origin` deleted or renamed its instance variable `host_name`
  - Model `Origin` deleted or renamed its instance variable `http_port`
  - Model `Origin` deleted or renamed its instance variable `https_port`
  - Model `Origin` deleted or renamed its instance variable `origin_host_header`
  - Model `Origin` deleted or renamed its instance variable `priority`
  - Model `Origin` deleted or renamed its instance variable `weight`
  - Model `Origin` deleted or renamed its instance variable `enabled`
  - Model `Origin` deleted or renamed its instance variable `private_link_alias`
  - Model `Origin` deleted or renamed its instance variable `private_link_resource_id`
  - Model `Origin` deleted or renamed its instance variable `private_link_location`
  - Model `Origin` deleted or renamed its instance variable `private_link_approval_message`
  - Model `Origin` deleted or renamed its instance variable `resource_state`
  - Model `Origin` deleted or renamed its instance variable `provisioning_state`
  - Model `Origin` deleted or renamed its instance variable `private_endpoint_status`
  - Model `OriginGroup` deleted or renamed its instance variable `health_probe_settings`
  - Model `OriginGroup` deleted or renamed its instance variable `origins`
  - Model `OriginGroup` deleted or renamed its instance variable `traffic_restoration_time_to_healed_or_new_endpoints_in_minutes`
  - Model `OriginGroup` deleted or renamed its instance variable `response_based_origin_error_detection_settings`
  - Model `OriginGroup` deleted or renamed its instance variable `resource_state`
  - Model `OriginGroup` deleted or renamed its instance variable `provisioning_state`
  - Model `OriginGroupUpdateParameters` deleted or renamed its instance variable `health_probe_settings`
  - Model `OriginGroupUpdateParameters` deleted or renamed its instance variable `origins`
  - Model `OriginGroupUpdateParameters` deleted or renamed its instance variable `traffic_restoration_time_to_healed_or_new_endpoints_in_minutes`
  - Model `OriginGroupUpdateParameters` deleted or renamed its instance variable `response_based_origin_error_detection_settings`
  - Model `OriginUpdateParameters` deleted or renamed its instance variable `host_name`
  - Model `OriginUpdateParameters` deleted or renamed its instance variable `http_port`
  - Model `OriginUpdateParameters` deleted or renamed its instance variable `https_port`
  - Model `OriginUpdateParameters` deleted or renamed its instance variable `origin_host_header`
  - Model `OriginUpdateParameters` deleted or renamed its instance variable `priority`
  - Model `OriginUpdateParameters` deleted or renamed its instance variable `weight`
  - Model `OriginUpdateParameters` deleted or renamed its instance variable `enabled`
  - Model `OriginUpdateParameters` deleted or renamed its instance variable `private_link_alias`
  - Model `OriginUpdateParameters` deleted or renamed its instance variable `private_link_resource_id`
  - Model `OriginUpdateParameters` deleted or renamed its instance variable `private_link_location`
  - Model `OriginUpdateParameters` deleted or renamed its instance variable `private_link_approval_message`
  - Model `ProfileUpdateParameters` deleted or renamed its instance variable `origin_response_timeout_seconds`
  - Model `ProfileUpdateParameters` deleted or renamed its instance variable `log_scrubbing`
  - Model `Route` deleted or renamed its instance variable `endpoint_name`
  - Model `Route` deleted or renamed its instance variable `custom_domains`
  - Model `Route` deleted or renamed its instance variable `origin_group`
  - Model `Route` deleted or renamed its instance variable `origin_path`
  - Model `Route` deleted or renamed its instance variable `rule_sets`
  - Model `Route` deleted or renamed its instance variable `supported_protocols`
  - Model `Route` deleted or renamed its instance variable `patterns_to_match`
  - Model `Route` deleted or renamed its instance variable `cache_configuration`
  - Model `Route` deleted or renamed its instance variable `forwarding_protocol`
  - Model `Route` deleted or renamed its instance variable `link_to_default_domain`
  - Model `Route` deleted or renamed its instance variable `https_redirect`
  - Model `Route` deleted or renamed its instance variable `enabled_state`
  - Model `Route` deleted or renamed its instance variable `provisioning_state`
  - Model `Route` deleted or renamed its instance variable `deployment_status`
  - Model `RouteUpdateParameters` deleted or renamed its instance variable `endpoint_name`
  - Model `RouteUpdateParameters` deleted or renamed its instance variable `custom_domains`
  - Model `RouteUpdateParameters` deleted or renamed its instance variable `origin_group`
  - Model `RouteUpdateParameters` deleted or renamed its instance variable `origin_path`
  - Model `RouteUpdateParameters` deleted or renamed its instance variable `rule_sets`
  - Model `RouteUpdateParameters` deleted or renamed its instance variable `supported_protocols`
  - Model `RouteUpdateParameters` deleted or renamed its instance variable `patterns_to_match`
  - Model `RouteUpdateParameters` deleted or renamed its instance variable `cache_configuration`
  - Model `RouteUpdateParameters` deleted or renamed its instance variable `forwarding_protocol`
  - Model `RouteUpdateParameters` deleted or renamed its instance variable `link_to_default_domain`
  - Model `RouteUpdateParameters` deleted or renamed its instance variable `https_redirect`
  - Model `RouteUpdateParameters` deleted or renamed its instance variable `enabled_state`
  - Model `Rule` deleted or renamed its instance variable `rule_set_name`
  - Model `Rule` deleted or renamed its instance variable `order`
  - Model `Rule` deleted or renamed its instance variable `conditions`
  - Model `Rule` deleted or renamed its instance variable `actions`
  - Model `Rule` deleted or renamed its instance variable `match_processing_behavior`
  - Model `Rule` deleted or renamed its instance variable `provisioning_state`
  - Model `Rule` deleted or renamed its instance variable `deployment_status`
  - Model `RuleSet` deleted or renamed its instance variable `provisioning_state`
  - Model `RuleSet` deleted or renamed its instance variable `deployment_status`
  - Model `RuleSet` deleted or renamed its instance variable `profile_name`
  - Model `RuleUpdateParameters` deleted or renamed its instance variable `rule_set_name`
  - Model `RuleUpdateParameters` deleted or renamed its instance variable `order`
  - Model `RuleUpdateParameters` deleted or renamed its instance variable `conditions`
  - Model `RuleUpdateParameters` deleted or renamed its instance variable `actions`
  - Model `RuleUpdateParameters` deleted or renamed its instance variable `match_processing_behavior`
  - Model `Secret` deleted or renamed its instance variable `provisioning_state`
  - Model `Secret` deleted or renamed its instance variable `deployment_status`
  - Model `Secret` deleted or renamed its instance variable `profile_name`
  - Model `Secret` deleted or renamed its instance variable `parameters`
  - Model `SecurityPolicy` deleted or renamed its instance variable `provisioning_state`
  - Model `SecurityPolicy` deleted or renamed its instance variable `deployment_status`
  - Model `SecurityPolicy` deleted or renamed its instance variable `profile_name`
  - Model `SecurityPolicy` deleted or renamed its instance variable `parameters`
  - Model `SecurityPolicyUpdateParameters` deleted or renamed its instance variable `parameters`
  - Deleted or renamed model `AfdErrorResponse`
  - Deleted or renamed model `AzureFirstPartyManagedCertificate`
  - Deleted or renamed model `CacheExpirationActionParametersTypeName`
  - Deleted or renamed model `CacheKeyQueryStringActionParametersTypeName`
  - Deleted or renamed model `CdnCertificateSourceParametersTypeName`
  - Deleted or renamed model `CdnWebApplicationFirewallPolicyList`
  - Deleted or renamed model `Certificate`
  - Deleted or renamed model `ClientPortMatchConditionParametersTypeName`
  - Deleted or renamed model `CookiesMatchConditionParametersTypeName`
  - Deleted or renamed model `CustomerCertificate`
  - Deleted or renamed model `DeliveryRuleActionEnum`
  - Deleted or renamed model `EdgenodeResult`
  - Deleted or renamed model `HeaderActionParametersTypeName`
  - Deleted or renamed model `HostNameMatchConditionParametersTypeName`
  - Deleted or renamed model `HttpVersionMatchConditionParametersTypeName`
  - Deleted or renamed model `IdentityType`
  - Deleted or renamed model `IsDeviceMatchConditionParametersMatchValuesItem`
  - Deleted or renamed model `IsDeviceMatchConditionParametersTypeName`
  - Deleted or renamed model `KeyVaultCertificateSourceParametersTypeName`
  - Deleted or renamed model `KeyVaultSigningKeyParametersTypeName`
  - Deleted or renamed model `ManagedCertificate`
  - Deleted or renamed model `ManagedRuleSetDefinitionList`
  - Deleted or renamed model `OriginGroupOverrideActionParametersTypeName`
  - Deleted or renamed model `PostArgsMatchConditionParametersTypeName`
  - Deleted or renamed model `QueryStringMatchConditionParametersTypeName`
  - Deleted or renamed model `RemoteAddressMatchConditionParametersTypeName`
  - Deleted or renamed model `RequestBodyMatchConditionParametersTypeName`
  - Deleted or renamed model `RequestHeaderMatchConditionParametersTypeName`
  - Deleted or renamed model `RequestMethodMatchConditionParametersMatchValuesItem`
  - Deleted or renamed model `RequestMethodMatchConditionParametersTypeName`
  - Deleted or renamed model `RequestSchemeMatchConditionParametersMatchValuesItem`
  - Deleted or renamed model `RequestSchemeMatchConditionParametersTypeName`
  - Deleted or renamed model `RequestUriMatchConditionParametersTypeName`
  - Deleted or renamed model `RouteConfigurationOverrideActionParametersTypeName`
  - Deleted or renamed model `ServerPortMatchConditionParametersTypeName`
  - Deleted or renamed model `SocketAddrMatchConditionParametersTypeName`
  - Deleted or renamed model `SslProtocolMatchConditionParametersTypeName`
  - Deleted or renamed model `UrlFileExtensionMatchConditionParametersTypeName`
  - Deleted or renamed model `UrlFileNameMatchConditionParametersTypeName`
  - Deleted or renamed model `UrlPathMatchConditionParametersTypeName`
  - Deleted or renamed model `UrlRedirectActionParametersTypeName`
  - Deleted or renamed model `UrlRewriteActionParametersTypeName`
  - Deleted or renamed model `UrlSigningActionParametersTypeName`
  - Deleted or renamed model `ValidationToken`
  - Method `LogAnalyticsOperations.get_log_analytics_metrics` changed its parameter `metrics` from `positional_or_keyword` to `keyword_only`
  - Method `LogAnalyticsOperations.get_log_analytics_metrics` changed its parameter `date_time_begin` from `positional_or_keyword` to `keyword_only`
  - Method `LogAnalyticsOperations.get_log_analytics_metrics` changed its parameter `date_time_end` from `positional_or_keyword` to `keyword_only`
  - Method `LogAnalyticsOperations.get_log_analytics_metrics` changed its parameter `granularity` from `positional_or_keyword` to `keyword_only`
  - Method `LogAnalyticsOperations.get_log_analytics_metrics` changed its parameter `custom_domains` from `positional_or_keyword` to `keyword_only`
  - Method `LogAnalyticsOperations.get_log_analytics_metrics` changed its parameter `protocols` from `positional_or_keyword` to `keyword_only`
  - Method `LogAnalyticsOperations.get_log_analytics_metrics` changed its parameter `group_by` from `positional_or_keyword` to `keyword_only`
  - Method `LogAnalyticsOperations.get_log_analytics_metrics` changed its parameter `continents` from `positional_or_keyword` to `keyword_only`
  - Method `LogAnalyticsOperations.get_log_analytics_metrics` changed its parameter `country_or_regions` from `positional_or_keyword` to `keyword_only`
  - Method `LogAnalyticsOperations.get_log_analytics_rankings` changed its parameter `rankings` from `positional_or_keyword` to `keyword_only`
  - Method `LogAnalyticsOperations.get_log_analytics_rankings` changed its parameter `metrics` from `positional_or_keyword` to `keyword_only`
  - Method `LogAnalyticsOperations.get_log_analytics_rankings` changed its parameter `max_ranking` from `positional_or_keyword` to `keyword_only`
  - Method `LogAnalyticsOperations.get_log_analytics_rankings` changed its parameter `date_time_begin` from `positional_or_keyword` to `keyword_only`
  - Method `LogAnalyticsOperations.get_log_analytics_rankings` changed its parameter `date_time_end` from `positional_or_keyword` to `keyword_only`
  - Method `LogAnalyticsOperations.get_log_analytics_rankings` changed its parameter `custom_domains` from `positional_or_keyword` to `keyword_only`
  - Method `LogAnalyticsOperations.get_waf_log_analytics_metrics` changed its parameter `metrics` from `positional_or_keyword` to `keyword_only`
  - Method `LogAnalyticsOperations.get_waf_log_analytics_metrics` changed its parameter `date_time_begin` from `positional_or_keyword` to `keyword_only`
  - Method `LogAnalyticsOperations.get_waf_log_analytics_metrics` changed its parameter `date_time_end` from `positional_or_keyword` to `keyword_only`
  - Method `LogAnalyticsOperations.get_waf_log_analytics_metrics` changed its parameter `granularity` from `positional_or_keyword` to `keyword_only`
  - Method `LogAnalyticsOperations.get_waf_log_analytics_metrics` changed its parameter `actions` from `positional_or_keyword` to `keyword_only`
  - Method `LogAnalyticsOperations.get_waf_log_analytics_metrics` changed its parameter `group_by` from `positional_or_keyword` to `keyword_only`
  - Method `LogAnalyticsOperations.get_waf_log_analytics_metrics` changed its parameter `rule_types` from `positional_or_keyword` to `keyword_only`
  - Method `LogAnalyticsOperations.get_waf_log_analytics_rankings` changed its parameter `metrics` from `positional_or_keyword` to `keyword_only`
  - Method `LogAnalyticsOperations.get_waf_log_analytics_rankings` changed its parameter `date_time_begin` from `positional_or_keyword` to `keyword_only`
  - Method `LogAnalyticsOperations.get_waf_log_analytics_rankings` changed its parameter `date_time_end` from `positional_or_keyword` to `keyword_only`
  - Method `LogAnalyticsOperations.get_waf_log_analytics_rankings` changed its parameter `max_ranking` from `positional_or_keyword` to `keyword_only`
  - Method `LogAnalyticsOperations.get_waf_log_analytics_rankings` changed its parameter `rankings` from `positional_or_keyword` to `keyword_only`
  - Method `LogAnalyticsOperations.get_waf_log_analytics_rankings` changed its parameter `actions` from `positional_or_keyword` to `keyword_only`
  - Method `LogAnalyticsOperations.get_waf_log_analytics_rankings` changed its parameter `rule_types` from `positional_or_keyword` to `keyword_only`
  - Deleted or renamed method `RuleSetsOperations.create`
  - Deleted or renamed model `CdnManagementClientOperationsMixin`

## 13.1.1 (2024-06-12)

### Bugs Fixed

  - Fix serialization error when setting model property with `azure.core.serialization.NULL`

## 13.1.0 (2024-04-15)

### Features Added

  - Model Profile has a new parameter log_scrubbing
  - Model ProfileUpdateParameters has a new parameter log_scrubbing

## 13.0.0 (2023-10-23)

### Features Added

  - Added operation AFDProfilesOperations.begin_upgrade
  - Added operation AFDProfilesOperations.check_endpoint_name_availability
  - Added operation AFDProfilesOperations.validate_secret
  - Added operation ProfilesOperations.begin_can_migrate
  - Added operation ProfilesOperations.begin_migrate
  - Added operation ProfilesOperations.begin_migration_commit
  - Model AFDDomain has a new parameter extended_properties
  - Model AFDDomainProperties has a new parameter extended_properties
  - Model AzureFirstPartyManagedCertificateParameters has a new parameter certificate_authority
  - Model AzureFirstPartyManagedCertificateParameters has a new parameter expiration_date
  - Model AzureFirstPartyManagedCertificateParameters has a new parameter secret_source
  - Model AzureFirstPartyManagedCertificateParameters has a new parameter subject
  - Model AzureFirstPartyManagedCertificateParameters has a new parameter subject_alternative_names
  - Model AzureFirstPartyManagedCertificateParameters has a new parameter thumbprint
  - Model CdnWebApplicationFirewallPolicy has a new parameter extended_properties
  - Model Profile has a new parameter extended_properties
  - Model Profile has a new parameter identity
  - Model ProfileUpdateParameters has a new parameter identity

### Breaking Changes

  - Removed operation group ValidateOperations
  - Renamed operation CustomDomainsOperations.disable_custom_https to CustomDomainsOperations.begin_disable_custom_https
  - Renamed operation CustomDomainsOperations.enable_custom_https to CustomDomainsOperations.begin_enable_custom_https

## 12.1.0b1 (2022-10-21)

### Breaking Changes

  - Renamed operation CustomDomainsOperations.disable_custom_https to CustomDomainsOperations.begin_disable_custom_https
  - Renamed operation CustomDomainsOperations.enable_custom_https to CustomDomainsOperations.begin_enable_custom_https

## 12.0.0 (2022-03-22)

**Features**

  - Added operation CdnManagementClientOperationsMixin.check_endpoint_name_availability
  - Added operation RuleSetsOperations.create
  - Model AFDDomain has a new parameter pre_validated_custom_domain_resource_id
  - Model AFDDomain has a new parameter profile_name
  - Model AFDDomainProperties has a new parameter pre_validated_custom_domain_resource_id
  - Model AFDDomainProperties has a new parameter profile_name
  - Model AFDDomainUpdateParameters has a new parameter pre_validated_custom_domain_resource_id
  - Model AFDDomainUpdateParameters has a new parameter profile_name
  - Model AFDDomainUpdatePropertiesParameters has a new parameter pre_validated_custom_domain_resource_id
  - Model AFDDomainUpdatePropertiesParameters has a new parameter profile_name
  - Model AFDEndpoint has a new parameter auto_generated_domain_name_label_scope
  - Model AFDEndpoint has a new parameter profile_name
  - Model AFDEndpointProperties has a new parameter auto_generated_domain_name_label_scope
  - Model AFDEndpointProperties has a new parameter profile_name
  - Model AFDEndpointPropertiesUpdateParameters has a new parameter profile_name
  - Model AFDEndpointUpdateParameters has a new parameter profile_name
  - Model AFDOrigin has a new parameter enforce_certificate_name_check
  - Model AFDOrigin has a new parameter origin_group_name
  - Model AFDOriginGroup has a new parameter profile_name
  - Model AFDOriginGroupProperties has a new parameter profile_name
  - Model AFDOriginGroupUpdateParameters has a new parameter profile_name
  - Model AFDOriginGroupUpdatePropertiesParameters has a new parameter profile_name
  - Model AFDOriginProperties has a new parameter enforce_certificate_name_check
  - Model AFDOriginProperties has a new parameter origin_group_name
  - Model AFDOriginUpdateParameters has a new parameter enforce_certificate_name_check
  - Model AFDOriginUpdateParameters has a new parameter origin_group_name
  - Model AFDOriginUpdatePropertiesParameters has a new parameter enforce_certificate_name_check
  - Model AFDOriginUpdatePropertiesParameters has a new parameter origin_group_name
  - Model Certificate has a new parameter type
  - Model CustomDomain has a new parameter custom_https_parameters
  - Model CustomerCertificate has a new parameter secret_source
  - Model CustomerCertificate has a new parameter secret_version
  - Model CustomerCertificate has a new parameter type
  - Model CustomerCertificateParameters has a new parameter expiration_date
  - Model CustomerCertificateParameters has a new parameter subject
  - Model CustomerCertificateParameters has a new parameter thumbprint
  - Model DeepCreatedOrigin has a new parameter private_endpoint_status
  - Model Endpoint has a new parameter custom_domains
  - Model EndpointProperties has a new parameter custom_domains
  - Model ErrorResponse has a new parameter error
  - Model HttpVersionMatchConditionParameters has a new parameter transforms
  - Model ManagedCertificate has a new parameter type
  - Model ManagedCertificateParameters has a new parameter expiration_date
  - Model ManagedCertificateParameters has a new parameter subject
  - Model Operation has a new parameter is_data_action
  - Model Operation has a new parameter origin
  - Model Operation has a new parameter service_specification
  - Model OperationDisplay has a new parameter description
  - Model Profile has a new parameter front_door_id
  - Model Profile has a new parameter kind
  - Model Profile has a new parameter origin_response_timeout_seconds
  - Model ProfileUpdateParameters has a new parameter origin_response_timeout_seconds
  - Model RequestMethodMatchConditionParameters has a new parameter transforms
  - Model RequestSchemeMatchConditionParameters has a new parameter transforms
  - Model Route has a new parameter cache_configuration
  - Model Route has a new parameter endpoint_name
  - Model RouteProperties has a new parameter cache_configuration
  - Model RouteProperties has a new parameter endpoint_name
  - Model RouteUpdateParameters has a new parameter cache_configuration
  - Model RouteUpdateParameters has a new parameter endpoint_name
  - Model RouteUpdatePropertiesParameters has a new parameter cache_configuration
  - Model RouteUpdatePropertiesParameters has a new parameter endpoint_name
  - Model Rule has a new parameter rule_set_name
  - Model RuleProperties has a new parameter rule_set_name
  - Model RuleSet has a new parameter profile_name
  - Model RuleSetProperties has a new parameter profile_name
  - Model RuleUpdateParameters has a new parameter rule_set_name
  - Model RuleUpdatePropertiesParameters has a new parameter rule_set_name
  - Model Secret has a new parameter profile_name
  - Model SecretProperties has a new parameter profile_name
  - Model SecurityPolicy has a new parameter profile_name
  - Model SecurityPolicyProperties has a new parameter profile_name
  - Model ValidateSecretInput has a new parameter secret_version

**Breaking changes**

  - Model AFDEndpoint no longer has parameter origin_response_timeout_seconds
  - Model AFDEndpointProperties no longer has parameter origin_response_timeout_seconds
  - Model AFDEndpointPropertiesUpdateParameters no longer has parameter origin_response_timeout_seconds
  - Model AFDEndpointUpdateParameters no longer has parameter origin_response_timeout_seconds
  - Model AFDOriginGroup no longer has parameter response_based_afd_origin_error_detection_settings
  - Model AFDOriginGroupProperties no longer has parameter response_based_afd_origin_error_detection_settings
  - Model AFDOriginGroupUpdateParameters no longer has parameter response_based_afd_origin_error_detection_settings
  - Model AFDOriginGroupUpdatePropertiesParameters no longer has parameter response_based_afd_origin_error_detection_settings
  - Model CacheExpirationActionParameters has a new required parameter type_name
  - Model CacheExpirationActionParameters no longer has parameter odata_type
  - Model CacheKeyQueryStringActionParameters has a new required parameter type_name
  - Model CacheKeyQueryStringActionParameters no longer has parameter odata_type
  - Model CdnCertificateSourceParameters has a new required parameter type_name
  - Model CdnCertificateSourceParameters no longer has parameter odata_type
  - Model Certificate no longer has parameter thumbprint
  - Model CookiesMatchConditionParameters has a new required parameter type_name
  - Model CookiesMatchConditionParameters no longer has parameter odata_type
  - Model CustomerCertificate no longer has parameter certificate_url
  - Model CustomerCertificate no longer has parameter version
  - Model ErrorResponse no longer has parameter code
  - Model ErrorResponse no longer has parameter message
  - Model HeaderActionParameters has a new required parameter type_name
  - Model HeaderActionParameters no longer has parameter odata_type
  - Model HttpVersionMatchConditionParameters has a new required parameter type_name
  - Model HttpVersionMatchConditionParameters no longer has parameter odata_type
  - Model IsDeviceMatchConditionParameters has a new required parameter type_name
  - Model IsDeviceMatchConditionParameters no longer has parameter odata_type
  - Model KeyVaultCertificateSourceParameters has a new required parameter type_name
  - Model KeyVaultCertificateSourceParameters no longer has parameter odata_type
  - Model KeyVaultSigningKeyParameters has a new required parameter type_name
  - Model KeyVaultSigningKeyParameters no longer has parameter odata_type
  - Model ManagedCertificate no longer has parameter thumbprint
  - Model OriginGroupOverrideActionParameters has a new required parameter type_name
  - Model OriginGroupOverrideActionParameters no longer has parameter odata_type
  - Model PostArgsMatchConditionParameters has a new required parameter type_name
  - Model PostArgsMatchConditionParameters no longer has parameter odata_type
  - Model Profile no longer has parameter frontdoor_id
  - Model QueryStringMatchConditionParameters has a new required parameter type_name
  - Model QueryStringMatchConditionParameters no longer has parameter odata_type
  - Model RemoteAddressMatchConditionParameters has a new required parameter type_name
  - Model RemoteAddressMatchConditionParameters no longer has parameter odata_type
  - Model RequestBodyMatchConditionParameters has a new required parameter type_name
  - Model RequestBodyMatchConditionParameters no longer has parameter odata_type
  - Model RequestHeaderMatchConditionParameters has a new required parameter type_name
  - Model RequestHeaderMatchConditionParameters no longer has parameter odata_type
  - Model RequestMethodMatchConditionParameters has a new required parameter type_name
  - Model RequestMethodMatchConditionParameters no longer has parameter odata_type
  - Model RequestSchemeMatchConditionParameters has a new required parameter type_name
  - Model RequestSchemeMatchConditionParameters no longer has parameter odata_type
  - Model RequestUriMatchConditionParameters has a new required parameter type_name
  - Model RequestUriMatchConditionParameters no longer has parameter odata_type
  - Model Route no longer has parameter compression_settings
  - Model Route no longer has parameter query_string_caching_behavior
  - Model RouteProperties no longer has parameter compression_settings
  - Model RouteProperties no longer has parameter query_string_caching_behavior
  - Model RouteUpdateParameters no longer has parameter compression_settings
  - Model RouteUpdateParameters no longer has parameter query_string_caching_behavior
  - Model RouteUpdatePropertiesParameters no longer has parameter compression_settings
  - Model RouteUpdatePropertiesParameters no longer has parameter query_string_caching_behavior
  - Model UrlFileExtensionMatchConditionParameters has a new required parameter type_name
  - Model UrlFileExtensionMatchConditionParameters no longer has parameter odata_type
  - Model UrlFileNameMatchConditionParameters has a new required parameter type_name
  - Model UrlFileNameMatchConditionParameters no longer has parameter odata_type
  - Model UrlPathMatchConditionParameters has a new required parameter type_name
  - Model UrlPathMatchConditionParameters no longer has parameter odata_type
  - Model UrlRedirectActionParameters has a new required parameter type_name
  - Model UrlRedirectActionParameters no longer has parameter odata_type
  - Model UrlRewriteActionParameters has a new required parameter type_name
  - Model UrlRewriteActionParameters no longer has parameter odata_type
  - Model UrlSigningActionParameters has a new required parameter type_name
  - Model UrlSigningActionParameters no longer has parameter odata_type
  - Operation SecurityPoliciesOperations.begin_patch has a new signature
  - Removed operation RuleSetsOperations.begin_create
  - Removed operation SecretsOperations.begin_update

## 11.0.0 (2021-03-29)

**Features**

  - Model ManagedRuleSetDefinition has a new parameter system_data
  - Model Resource has a new parameter system_data

**Breaking changes**

  - Operation SecurityPoliciesOperations.begin_patch has a new signature
  - Operation RuleSetsOperations.begin_create has a new signature
  - Model RouteUpdatePropertiesParameters no longer has parameter optimization_type
  - Model CustomerCertificateParameters no longer has parameter thumbprint
  - Model CustomerCertificateParameters no longer has parameter subject
  - Model CustomerCertificateParameters no longer has parameter expiration_date
  - Model RouteProperties no longer has parameter optimization_type
  - Model Route no longer has parameter optimization_type
  - Model RouteUpdateParameters no longer has parameter optimization_type
  - Operation LogAnalyticsOperations.get_log_analytics_metrics has a new signature
  - Model ManagedCertificateParameters has a new signature

## 10.0.0 (2021-01-19)

**Features**

  - Model ProxyResource has a new parameter system_data
  - Model OriginGroup has a new parameter system_data
  - Model Endpoint has a new parameter system_data
  - Model EdgeNode has a new parameter system_data
  - Model Origin has a new parameter system_data
  - Model TrackedResource has a new parameter system_data
  - Model Profile has a new parameter system_data
  - Model Profile has a new parameter frontdoor_id
  - Model CdnWebApplicationFirewallPolicy has a new parameter system_data
  - Model CustomDomain has a new parameter system_data
  - Added operation group AFDOriginsOperations
  - Added operation group AFDProfilesOperations
  - Added operation group AFDEndpointsOperations
  - Added operation group RoutesOperations
  - Added operation group LogAnalyticsOperations
  - Added operation group RulesOperations
  - Added operation group ValidateOperations
  - Added operation group AFDOriginGroupsOperations
  - Added operation group SecretsOperations
  - Added operation group SecurityPoliciesOperations
  - Added operation group AFDCustomDomainsOperations
  - Added operation group RuleSetsOperations

**Breaking changes**

  - Parameter odata_type of model UrlSigningActionParameters is now required
  - Operation PoliciesOperations.begin_update has a new signature
  - Operation EndpointsOperations.validate_custom_domain has a new signature
  - Operation EndpointsOperations.begin_load_content has a new signature
  - Operation EndpointsOperations.begin_purge_content has a new signature
  - Operation ProfilesOperations.begin_update has a new signature
  - Operation CdnManagementClientOperationsMixin.check_name_availability has a new signature
  - Operation CdnManagementClientOperationsMixin.check_name_availability_with_subscription has a new signature
  - Operation CdnManagementClientOperationsMixin.validate_probe has a new signature
  - Operation CustomDomainsOperations.begin_create has a new signature
  - Model UrlSigningActionParameters no longer has parameter ip_subnets
  - Model UrlSigningActionParameters no longer has parameter key_id

## 10.0.0b1 (2020-10-31)
This is beta preview version.
For detailed changelog please refer to equivalent stable version 5.1.0 (https://pypi.org/project/azure-mgmt-cdn/5.1.0/)

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
  - For a complete set of supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core-tracing-opentelemetry) for an overview.

## 5.1.0 (2020-08-10)

**Features**
  - Add UrlSigningAction

## 5.0.0 (2020-07-21)

**Features**

  - Model Origin has a new parameter private_link_approval_message
  - Model Origin has a new parameter enabled
  - Model Origin has a new parameter weight
  - Model Origin has a new parameter origin_host_header
  - Model Origin has a new parameter private_link_resource_id
  - Model Origin has a new parameter private_link_location
  - Model Origin has a new parameter private_link_alias
  - Model Origin has a new parameter priority
  - Model Origin has a new parameter private_endpoint_status
  - Model EndpointUpdateParameters has a new parameter url_signing_keys
  - Model EndpointUpdateParameters has a new parameter default_origin_group
  - Model Endpoint has a new parameter url_signing_keys
  - Model Endpoint has a new parameter origin_groups
  - Model Endpoint has a new parameter default_origin_group
  - Added operation OriginsOperations.create
  - Added operation OriginsOperations.delete
  - Added operation group OriginGroupsOperations

**Breaking changes**

  - Model Origin no longer has parameter location
  - Model Origin no longer has parameter tags
  - Model CustomDomain no longer has parameter custom_https_parameters
  - Model DeepCreatedOrigin has a new signature
  - Model OriginUpdateParameters has a new signature

## 4.1.0rc1 (2020-01-18)

**Features**

  - Model Endpoint has a new parameter
    web_application_firewall_policy_link
  - Model EndpointUpdateParameters has a new parameter
    web_application_firewall_policy_link
  - Added operation group PoliciesOperations
  - Added operation group ManagedRuleSetsOperations

## 4.0.0 (2019-11-25)

**Features**

  - Model DeliveryRule has a new parameter name
  - Model CdnManagedHttpsParameters has a new parameter
    minimum_tls_version
  - Model UserManagedHttpsParameters has a new parameter
    minimum_tls_version
  - Model CustomDomainHttpsParameters has a new parameter
    minimum_tls_version
  - Model CustomDomain has a new parameter custom_https_parameters
  - Added operation group CdnManagementClientOperationsMixin

**General Breaking Changes**

This version uses a next-generation code generator that *might*
introduce breaking changes. In summary, some modules were incorrectly
visible/importable and have been renamed. This fixed several issues
caused by usage of classes that were not supposed to be used in the
first place.

  - CdnManagementClient cannot be imported from
    `azure.mgmt.cdn.cdn_management_client` anymore (import from
    `azure.mgmt.cdn` works like before)
  - CdnManagementClientConfiguration import has been moved from
    `azure.mgmt.cdn.cdn_management_client` to `azure.mgmt.cdn`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.cdn.models.my_class` (import from
    `azure.mgmt.cdn.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.cdn.operations.my_class_operations` (import from
    `azure.mgmt.cdn.operations` works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 3.1.0 (2019-03-05)

**Features**

  - Add custom_domain_https_parameters support

## 3.0.0 (2018-05-25)

**Features**

  - Add client method check_name_availability_with_subscription
  - Model EndpointUpdateParameters has a new parameter delivery_policy
  - Model Endpoint has a new parameter delivery_policy
  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes.

  - Model signatures now use only keyword-argument syntax. All
    positional arguments must be re-written as keyword-arguments. To
    keep auto-completion in most cases, models are now generated for
    Python 2 and Python 3. Python 3 uses the "*" syntax for
    keyword-only arguments.
  - Enum types now use the "str" mixin (class AzureEnum(str, Enum)) to
    improve the behavior when unrecognized enum values are encountered.
    While this is not a breaking change, the distinctions are important,
    and are documented here:
    <https://docs.python.org/3/library/enum.html#others> At a glance:
      - "is" should not be used at all.
      - "format" will return the string value, where "%s" string
        formatting will return `NameOfEnum.stringvalue`. Format syntax
        should be prefered.
  - New Long Running Operation:
      - Return type changes from
        `msrestazure.azure_operation.AzureOperationPoller` to
        `msrest.polling.LROPoller`. External API is the same.
      - Return type is now **always** a `msrest.polling.LROPoller`,
        regardless of the optional parameters used.
      - The behavior has changed when using `raw=True`. Instead of
        returning the initial call result as `ClientRawResponse`,
        without polling, now this returns an LROPoller. After polling,
        the final resource will be returned as a `ClientRawResponse`.
      - New `polling` parameter. The default behavior is
        `Polling=True` which will poll using ARM algorithm. When
        `Polling=False`, the response of the initial call will be
        returned without polling.
      - `polling` parameter accepts instances of subclasses of
        `msrest.polling.PollingMethod`.
      - `add_done_callback` will no longer raise if called after
        polling is finished, but will instead execute the callback right
        away.

**Bugfixes**

  - Compatibility of the sdist with wheel 0.31.0

## 2.0.0 (2017-10-26)

**Features**

  - Add probe operations and in some models
  - Add list_supported_optimization_types

**Breaking changes**

  - move resource_usage into its own operation group
  - move operations list into its own operation group

Api version changed from 2016-10-02 to 2017-04-02

## 1.0.0 (2017-06-30)

**Features**

  - Add disable_custom_https and enable_custom_https

**Breaking changes**

  - Rename check_resource_usage to list_resource_usage
  - list EdgeNode now returns an iterator of EdgeNode, not a
    EdgenodeResult instance with an attribute "value" being a list of
    EdgeNode

## 0.30.3 (2017-05-15)

  - This wheel package is now built with the azure wheel extension

## 0.30.2 (2016-12-22)

  - Fix EdgeNode attributes content

## 0.30.1 (2016-12-15)

  - Fix list EdgeNodes method return type

## 0.30.0 (2016-12-14)

  - Initial preview release (API Version 2016-10-02)
  - Major breaking changes from 0.30.0rc6

## 0.30.0rc6 (2016-09-02)

  - Initial alpha release (API Version 2016-04-02)
