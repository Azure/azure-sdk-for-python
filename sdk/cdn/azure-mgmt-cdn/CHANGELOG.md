# Release History

## 14.0.0b1 (2026-05-20)

### Features Added

  - Client `CdnManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `CdnManagementClient` added method `send_request`
  - Model `AFDDomainHttpsParameters` added property `cipher_suite_set_type`
  - Model `AFDDomainHttpsParameters` added property `customized_cipher_suite_set`
  - Model `AFDOriginGroupProperties` added property `authentication`
  - Model `AFDOriginGroupUpdatePropertiesParameters` added property `authentication`
  - Enum `AfdMinimumTlsVersion` added member `TLS13`
  - Model `RuleSetProperties` added property `batch_mode`
  - Model `RuleSetProperties` added property `rules`
  - Added model `AFDDomainHttpsCustomizedCipherSuiteSet`
  - Added enum `AfdCipherSuiteSetType`
  - Added enum `AfdCustomizedCipherSuiteForTls12`
  - Added enum `AfdCustomizedCipherSuiteForTls13`
  - Added model `BatchRuleProperties`
  - Added model `CdnMigrationToAfdParameters`
  - Added model `CertificateSourceParameters`
  - Added enum `CertificateSourceParametersType`
  - Added enum `CreatedByType`
  - Added enum `DeliveryRuleActionName`
  - Added model `DeliveryRuleActionParameters`
  - Added enum `DeliveryRuleActionParametersType`
  - Added model `DeliveryRuleConditionParameters`
  - Added enum `DeliveryRuleConditionParametersType`
  - Added enum `IsDeviceMatchValue`
  - Added enum `KeyVaultSigningKeyParametersType`
  - Added model `MigrationEndpointMapping`
  - Added model `OriginAuthenticationProperties`
  - Added enum `OriginAuthenticationType`
  - Added enum `RequestMethodMatchValue`
  - Added enum `RequestSchemeMatchValue`
  - Operation group `ProfilesOperations` added method `begin_cdn_can_migrate_to_afd`
  - Operation group `ProfilesOperations` added method `begin_cdn_migrate_to_afd`
  - Operation group `ProfilesOperations` added method `begin_migration_abort`
  - Operation group `RuleSetsOperations` added method `begin_create`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Model `AFDDomain` moved instance variable `profile_name`, `tls_settings`, `azure_dns_zone`, `pre_validated_custom_domain_resource_id`, `provisioning_state`, `deployment_status`, `domain_validation_state`, `host_name`, `extended_properties` and `validation_properties` under property `properties` whose type is `AFDDomainProperties`
  - Model `AFDDomainUpdateParameters` moved instance variable `profile_name`, `tls_settings`, `azure_dns_zone` and `pre_validated_custom_domain_resource_id` under property `properties` whose type is `AFDDomainUpdatePropertiesParameters`
  - Model `AFDEndpoint` moved instance variable `profile_name`, `enabled_state`, `provisioning_state`, `deployment_status`, `host_name` and `auto_generated_domain_name_label_scope` under property `properties` whose type is `AFDEndpointProperties`
  - Model `AFDEndpointUpdateParameters` moved instance variable `profile_name` and `enabled_state` under property `properties` whose type is `AFDEndpointPropertiesUpdateParameters`
  - Model `AFDOrigin` moved instance variable `origin_group_name`, `azure_origin`, `host_name`, `http_port`, `https_port`, `origin_host_header`, `priority`, `weight`, `shared_private_link_resource`, `enabled_state`, `enforce_certificate_name_check`, `provisioning_state` and `deployment_status` under property `properties` whose type is `AFDOriginProperties`
  - Model `AFDOriginGroup` moved instance variable `profile_name`, `load_balancing_settings`, `health_probe_settings`, `traffic_restoration_time_to_healed_or_new_endpoints_in_minutes`, `session_affinity_state`, `provisioning_state` and `deployment_status` under property `properties` whose type is `AFDOriginGroupProperties`
  - Model `AFDOriginGroupUpdateParameters` moved instance variable `profile_name`, `load_balancing_settings`, `health_probe_settings`, `traffic_restoration_time_to_healed_or_new_endpoints_in_minutes` and `session_affinity_state` under property `properties` whose type is `AFDOriginGroupUpdatePropertiesParameters`
  - Model `AFDOriginUpdateParameters` moved instance variable `origin_group_name`, `azure_origin`, `host_name`, `http_port`, `https_port`, `origin_host_header`, `priority`, `weight`, `shared_private_link_resource`, `enabled_state` and `enforce_certificate_name_check` under property `properties` whose type is `AFDOriginUpdatePropertiesParameters`
  - Model `CanMigrateResult` moved instance variable `can_migrate`, `default_sku` and `errors` under property `properties` whose type is `CanMigrateProperties`
  - Model `CustomDomainParameters` moved instance variable `host_name` under property `properties` whose type is `CustomDomainPropertiesParameters`
  - Model `Endpoint` moved instance variable `origin_path`, `content_types_to_compress`, `origin_host_header`, `is_compression_enabled`, `is_http_allowed`, `is_https_allowed`, `query_string_caching_behavior`, `optimization_type`, `probe_path`, `geo_filters`, `default_origin_group`, `url_signing_keys`, `delivery_policy`, `web_application_firewall_policy_link`, `host_name`, `origins`, `origin_groups`, `custom_domains`, `resource_state` and `provisioning_state` under property `properties` whose type is `EndpointProperties`
  - Model `EndpointUpdateParameters` moved instance variable `origin_path`, `content_types_to_compress`, `origin_host_header`, `is_compression_enabled`, `is_http_allowed`, `is_https_allowed`, `query_string_caching_behavior`, `optimization_type`, `probe_path`, `geo_filters`, `default_origin_group`, `url_signing_keys`, `delivery_policy` and `web_application_firewall_policy_link` under property `properties` whose type is `EndpointPropertiesUpdateParameters`
  - Enum value `MatchProcessingBehavior.CONTINUE_ENUM` was renamed to `CONTINUE`
  - Model `Operation` moved instance variable `service_specification` under property `operation_properties` whose type is `OperationProperties`
  - Model `Origin` moved instance variable `host_name`, `http_port`, `https_port`, `origin_host_header`, `priority`, `weight`, `enabled`, `private_link_alias`, `private_link_resource_id`, `private_link_location`, `private_link_approval_message`, `resource_state`, `provisioning_state` and `private_endpoint_status` under property `properties` whose type is `OriginProperties`
  - Model `OriginGroup` moved instance variable `health_probe_settings`, `origins`, `traffic_restoration_time_to_healed_or_new_endpoints_in_minutes`, `response_based_origin_error_detection_settings`, `resource_state` and `provisioning_state` under property `properties` whose type is `OriginGroupProperties`
  - Model `OriginGroupUpdateParameters` moved instance variable `health_probe_settings`, `origins`, `traffic_restoration_time_to_healed_or_new_endpoints_in_minutes` and `response_based_origin_error_detection_settings` under property `properties` whose type is `OriginGroupUpdatePropertiesParameters`
  - Model `OriginUpdateParameters` moved instance variable `host_name`, `http_port`, `https_port`, `origin_host_header`, `priority`, `weight`, `enabled`, `private_link_alias`, `private_link_resource_id`, `private_link_location` and `private_link_approval_message` under property `properties` whose type is `OriginUpdatePropertiesParameters`
  - Model `ProfileUpdateParameters` moved instance variable `origin_response_timeout_seconds` and `log_scrubbing` under property `properties` whose type is `ProfilePropertiesUpdateParameters`
  - Model `Route` moved instance variable `endpoint_name`, `custom_domains`, `origin_group`, `origin_path`, `rule_sets`, `supported_protocols`, `patterns_to_match`, `cache_configuration`, `forwarding_protocol`, `link_to_default_domain`, `https_redirect`, `enabled_state`, `provisioning_state` and `deployment_status` under property `properties` whose type is `RouteProperties`
  - Model `RouteUpdateParameters` moved instance variable `endpoint_name`, `custom_domains`, `origin_group`, `origin_path`, `rule_sets`, `supported_protocols`, `patterns_to_match`, `cache_configuration`, `forwarding_protocol`, `link_to_default_domain`, `https_redirect` and `enabled_state` under property `properties` whose type is `RouteUpdatePropertiesParameters`
  - Model `Rule` moved instance variable `rule_set_name`, `order`, `conditions`, `actions`, `match_processing_behavior`, `provisioning_state` and `deployment_status` under property `properties` whose type is `RuleProperties`
  - Model `RuleSet` moved instance variable `provisioning_state`, `deployment_status` and `profile_name` under property `properties` whose type is `RuleSetProperties`
  - Model `RuleUpdateParameters` moved instance variable `rule_set_name`, `order`, `conditions`, `actions` and `match_processing_behavior` under property `properties` whose type is `RuleUpdatePropertiesParameters`
  - Model `Secret` moved instance variable `provisioning_state`, `deployment_status`, `profile_name` and `parameters` under property `properties` whose type is `SecretProperties`
  - Model `SecurityPolicy` moved instance variable `provisioning_state`, `deployment_status`, `profile_name` and `parameters` under property `properties` whose type is `SecurityPolicyProperties`
  - Model `SecurityPolicyUpdateParameters` moved instance variable `parameters` under property `properties` whose type is `SecurityPolicyUpdateProperties`
  - Deleted or renamed model `AfdErrorResponse`
  - Deleted or renamed model `AzureFirstPartyManagedCertificate`
  - Deleted or renamed model `CacheExpirationActionParametersTypeName`
  - Deleted or renamed model `CacheKeyQueryStringActionParametersTypeName`
  - Deleted or renamed model `CdnCertificateSourceParametersTypeName`
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
  - Method `LogAnalyticsOperations.get_log_analytics_metrics` changed its parameter `metrics`/`date_time_begin`/`date_time_end`/`granularity`/`custom_domains`/`protocols`/`group_by`/`continents`/`country_or_regions` from `positional_or_keyword` to `keyword_only`
  - Method `LogAnalyticsOperations.get_log_analytics_rankings` changed its parameter `rankings`/`metrics`/`max_ranking`/`date_time_begin`/`date_time_end`/`custom_domains` from `positional_or_keyword` to `keyword_only`
  - Method `LogAnalyticsOperations.get_waf_log_analytics_metrics` changed its parameter `metrics`/`date_time_begin`/`date_time_end`/`granularity`/`actions`/`group_by`/`rule_types` from `positional_or_keyword` to `keyword_only`
  - Method `LogAnalyticsOperations.get_waf_log_analytics_rankings` changed its parameter `metrics`/`date_time_begin`/`date_time_end`/`max_ranking`/`rankings`/`actions`/`rule_types` from `positional_or_keyword` to `keyword_only`
  - Deleted or renamed method `RuleSetsOperations.create`
  - Deleted or renamed model `CdnManagementClientOperationsMixin`

### Other Changes

  - Deleted model `CdnWebApplicationFirewallPolicyList`/`ManagedRuleSetDefinitionList` which actually were not used by SDK users

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
