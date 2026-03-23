# Release History

## 1.3.0b1 (2026-03-23)

skip changelog generation

## 1.3.0 (2026-03-23)

skip changelog generation

## 1.3.0b1 (2026-03-20)

### Features Added

  - Client `FrontDoorManagementClient` added method `send_request`
  - Model `BackendPool` added property `properties`
  - Model `CustomHttpsConfiguration` added property `key_vault_certificate_source_parameters`
  - Model `CustomHttpsConfiguration` added property `front_door_certificate_source_parameters`
  - Model `ExperimentUpdateModel` added property `properties`
  - Model `FrontDoor` added property `properties`
  - Model `FrontendEndpoint` added property `properties`
  - Model `HealthProbeSettingsModel` added property `properties`
  - Model `LoadBalancingSettingsModel` added property `properties`
  - Model `PolicySettings` added property `log_scrubbing`
  - Model `ProfileUpdateModel` added property `properties`
  - Model `RoutingRule` added property `properties`
  - Model `RulesEngine` added property `properties`
  - Added model `ExperimentUpdateProperties`
  - Added model `FrontDoorCertificateSourceParameters`
  - Added model `KeyVaultCertificateSourceParameters`
  - Added model `PolicySettingsLogScrubbing`
  - Added model `ProfileUpdateProperties`

### Breaking Changes

  - Model `BackendPool` deleted or renamed its instance variable `backends`
  - Model `BackendPool` deleted or renamed its instance variable `load_balancing_settings`
  - Model `BackendPool` deleted or renamed its instance variable `health_probe_settings`
  - Model `BackendPool` deleted or renamed its instance variable `resource_state`
  - Model `CustomHttpsConfiguration` deleted or renamed its instance variable `certificate_type`
  - Model `CustomHttpsConfiguration` deleted or renamed its instance variable `vault`
  - Model `CustomHttpsConfiguration` deleted or renamed its instance variable `secret_name`
  - Model `CustomHttpsConfiguration` deleted or renamed its instance variable `secret_version`
  - Model `ExperimentUpdateModel` deleted or renamed its instance variable `description`
  - Model `ExperimentUpdateModel` deleted or renamed its instance variable `enabled_state`
  - Model `FrontDoor` deleted or renamed its instance variable `friendly_name`
  - Model `FrontDoor` deleted or renamed its instance variable `routing_rules`
  - Model `FrontDoor` deleted or renamed its instance variable `load_balancing_settings`
  - Model `FrontDoor` deleted or renamed its instance variable `health_probe_settings`
  - Model `FrontDoor` deleted or renamed its instance variable `backend_pools`
  - Model `FrontDoor` deleted or renamed its instance variable `frontend_endpoints`
  - Model `FrontDoor` deleted or renamed its instance variable `backend_pools_settings`
  - Model `FrontDoor` deleted or renamed its instance variable `enabled_state`
  - Model `FrontDoor` deleted or renamed its instance variable `resource_state`
  - Model `FrontDoor` deleted or renamed its instance variable `provisioning_state`
  - Model `FrontDoor` deleted or renamed its instance variable `cname`
  - Model `FrontDoor` deleted or renamed its instance variable `frontdoor_id`
  - Model `FrontDoor` deleted or renamed its instance variable `rules_engines`
  - Model `FrontDoor` deleted or renamed its instance variable `extended_properties`
  - Model `FrontendEndpoint` deleted or renamed its instance variable `host_name`
  - Model `FrontendEndpoint` deleted or renamed its instance variable `session_affinity_enabled_state`
  - Model `FrontendEndpoint` deleted or renamed its instance variable `session_affinity_ttl_seconds`
  - Model `FrontendEndpoint` deleted or renamed its instance variable `web_application_firewall_policy_link`
  - Model `FrontendEndpoint` deleted or renamed its instance variable `resource_state`
  - Model `FrontendEndpoint` deleted or renamed its instance variable `custom_https_provisioning_state`
  - Model `FrontendEndpoint` deleted or renamed its instance variable `custom_https_provisioning_substate`
  - Model `FrontendEndpoint` deleted or renamed its instance variable `custom_https_configuration`
  - Model `HealthProbeSettingsModel` deleted or renamed its instance variable `path`
  - Model `HealthProbeSettingsModel` deleted or renamed its instance variable `protocol`
  - Model `HealthProbeSettingsModel` deleted or renamed its instance variable `interval_in_seconds`
  - Model `HealthProbeSettingsModel` deleted or renamed its instance variable `health_probe_method`
  - Model `HealthProbeSettingsModel` deleted or renamed its instance variable `enabled_state`
  - Model `HealthProbeSettingsModel` deleted or renamed its instance variable `resource_state`
  - Model `LoadBalancingSettingsModel` deleted or renamed its instance variable `sample_size`
  - Model `LoadBalancingSettingsModel` deleted or renamed its instance variable `successful_samples_required`
  - Model `LoadBalancingSettingsModel` deleted or renamed its instance variable `additional_latency_milliseconds`
  - Model `LoadBalancingSettingsModel` deleted or renamed its instance variable `resource_state`
  - Model `PolicySettings` deleted or renamed its instance variable `state`
  - Model `PolicySettings` deleted or renamed its instance variable `scrubbing_rules`
  - Model `ProfileUpdateModel` deleted or renamed its instance variable `enabled_state`
  - Model `RoutingRule` deleted or renamed its instance variable `frontend_endpoints`
  - Model `RoutingRule` deleted or renamed its instance variable `accepted_protocols`
  - Model `RoutingRule` deleted or renamed its instance variable `patterns_to_match`
  - Model `RoutingRule` deleted or renamed its instance variable `enabled_state`
  - Model `RoutingRule` deleted or renamed its instance variable `route_configuration`
  - Model `RoutingRule` deleted or renamed its instance variable `rules_engine`
  - Model `RoutingRule` deleted or renamed its instance variable `web_application_firewall_policy_link`
  - Model `RoutingRule` deleted or renamed its instance variable `resource_state`
  - Model `RulesEngine` deleted or renamed its instance variable `rules`
  - Model `RulesEngine` deleted or renamed its instance variable `resource_state`
  - Deleted or renamed model `ExperimentList`
  - Deleted or renamed model `ManagedRuleSetDefinitionList`
  - Deleted or renamed model `PreconfiguredEndpointList`
  - Deleted or renamed model `ProfileList`
  - Deleted or renamed model `WebApplicationFirewallPolicyList`
  - Method `ReportsOperations.get_latency_scorecards` changed its parameter `aggregation_interval` from `positional_or_keyword` to `keyword_only`
  - Method `ReportsOperations.get_latency_scorecards` changed its parameter `end_date_time_utc` from `positional_or_keyword` to `keyword_only`
  - Method `ReportsOperations.get_latency_scorecards` changed its parameter `country` from `positional_or_keyword` to `keyword_only`
  - Method `ReportsOperations.get_timeseries` changed its parameter `start_date_time_utc` from `positional_or_keyword` to `keyword_only`
  - Method `ReportsOperations.get_timeseries` changed its parameter `end_date_time_utc` from `positional_or_keyword` to `keyword_only`
  - Method `ReportsOperations.get_timeseries` changed its parameter `aggregation_interval` from `positional_or_keyword` to `keyword_only`
  - Method `ReportsOperations.get_timeseries` changed its parameter `timeseries_type` from `positional_or_keyword` to `keyword_only`
  - Method `ReportsOperations.get_timeseries` changed its parameter `endpoint` from `positional_or_keyword` to `keyword_only`
  - Method `ReportsOperations.get_timeseries` changed its parameter `country` from `positional_or_keyword` to `keyword_only`

## 1.3.0 (2026-03-20)

skip changelog generation

## 1.2.0 (2024-04-15)

### Features Added

  - Model CustomRule has a new parameter group_by
  - Model PolicySettings has a new parameter javascript_challenge_expiration_in_minutes
  - Model PolicySettings has a new parameter scrubbing_rules
  - Model PolicySettings has a new parameter state

## 1.1.0 (2023-05-19)

### Features Added

  - Added operation PoliciesOperations.begin_update
  - Added operation PoliciesOperations.list_by_subscription
  - Model FrontDoor has a new parameter extended_properties
  - Model FrontDoorProperties has a new parameter extended_properties

## 1.1.0b1 (2022-11-22)

### Features Added

  - Added operation PoliciesOperations.begin_update
  - Model FrontDoor has a new parameter extended_properties
  - Model FrontDoorProperties has a new parameter extended_properties

## 1.0.1 (2022-03-29)

**Fixes**

- Fix duplicated description in annotation

## 1.0.0 (2021-03-26)

 - GA release

## 1.0.0b1 (2021-02-09)

This is beta preview version.
For detailed changelog please refer to equivalent stable version 10.2.0 (https://pypi.org/project/azure-mgmt-network/10.2.0/)

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


## 0.3.0 (2019-10-11)

  - Fixed new network experiment SDK structure

## 0.2.0 (2019-10-09)

**Features**

  - Model RoutingRule has a new parameter route_configuration
  - Model PolicySettings has a new parameter redirect_url
  - Model PolicySettings has a new parameter
    custom_block_response_body
  - Model PolicySettings has a new parameter
    custom_block_response_status_code
  - Model HealthProbeSettingsModel has a new parameter enabled_state
  - Model HealthProbeSettingsModel has a new parameter
    health_probe_method
  - Model HealthProbeSettingsUpdateParameters has a new parameter
    enabled_state
  - Model HealthProbeSettingsUpdateParameters has a new parameter
    health_probe_method
  - Model FrontDoorUpdateParameters has a new parameter
    backend_pools_settings
  - Model CustomRule has a new parameter enabled_state
  - Model FrontDoor has a new parameter backend_pools_settings
  - Model RoutingRuleUpdateParameters has a new parameter
    route_configuration
  - Added operation group ProfilesOperations
  - Added operation group ExperimentsOperations
  - Added operation group PreconfiguredEndpointsOperations
  - Added operation group ManagedRuleSetsOperations
  - Added operation group FrontDoorManagementClientOperationsMixin

**Breaking changes**

  - Parameter certificate_source of model CustomHttpsConfiguration is
    now required
  - Parameter protocol_type of model CustomHttpsConfiguration is now
    required
  - Model RoutingRule no longer has parameter custom_forwarding_path
  - Model RoutingRule no longer has parameter forwarding_protocol
  - Model RoutingRule no longer has parameter cache_configuration
  - Model RoutingRule no longer has parameter backend_pool
  - Model CustomRule no longer has parameter etag
  - Model CustomRule no longer has parameter transforms
  - Model CustomHttpsConfiguration has a new required parameter
    minimum_tls_version
  - Model RoutingRuleUpdateParameters no longer has parameter
    custom_forwarding_path
  - Model RoutingRuleUpdateParameters no longer has parameter
    forwarding_protocol
  - Model RoutingRuleUpdateParameters no longer has parameter
    cache_configuration
  - Model RoutingRuleUpdateParameters no longer has parameter
    backend_pool
  - Removed operation FrontendEndpointsOperations.delete
  - Removed operation FrontendEndpointsOperations.create_or_update
  - Model ManagedRuleSet has a new signature
  - Removed operation group LoadBalancingSettingsOperations
  - Removed operation group RoutingRulesOperations
  - Removed operation group HealthProbeSettingsOperations
  - Removed operation group BackendPoolsOperations

## 0.1.0 (2019-03-11)

  - Initial Release
