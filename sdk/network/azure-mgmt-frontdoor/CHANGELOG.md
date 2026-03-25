# Release History

## 2.0.0b1 (2026-03-24)

### Features Added

  - Model `FrontDoorManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `FrontDoorManagementClient` added method `send_request`
  - Enum `ActionType` added member `CAPTCHA`
  - Model `CustomHttpsConfiguration` added property `key_vault_certificate_source_parameters`
  - Model `CustomHttpsConfiguration` added property `front_door_certificate_source_parameters`
  - Model `ManagedRuleDefinition` added property `default_sensitivity`
  - Model `ManagedRuleOverride` added property `sensitivity`
  - Enum `Operator` added member `SERVICE_TAG_MATCH`
  - Model `PolicySettings` added property `captcha_expiration_in_minutes`
  - Model `PolicySettings` added property `log_scrubbing`
  - Added model `BasicResource`
  - Added model `BasicResourceWithSettableIDName`
  - Added model `ExperimentUpdateProperties`
  - Added model `FrontDoorCertificateSourceParameters`
  - Added model `KeyVaultCertificateSourceParameters`
  - Added model `PolicySettingsLogScrubbing`
  - Added model `ProfileUpdateProperties`
  - Added model `ResourcewithSettableName`
  - Added enum `SensitivityType`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Model `BackendPool` moved instance variable `backends`, `load_balancing_settings`, `health_probe_settings` and `resource_state` under property `properties`
  - Model `CustomHttpsConfiguration` moved instance variable `certificate_type` under property `front_door_certificate_source_parameters`
  - Model `CustomHttpsConfiguration` moved instance variable `vault`,  `secret_name` and `secret_version` under property `key_vault_certificate_source_parameters`
  - Model `ExperimentUpdateModel` moved instance variable `description` and `enabled_state` under property `properties`
  - Model `FrontDoor` moved instance variable `friendly_name`, `routing_rules`, `load_balancing_settings`, `health_probe_settings`, `backend_pools`, `frontend_endpoints`, `backend_pools_settings`, `enabled_state`, `resource_state`, `provisioning_state`, `cname`, `frontdoor_id`, `rules_engines` and `extended_properties` under property `properties`
  - Model `FrontendEndpoint` moved instance variable `host_name`, `session_affinity_enabled_state`, `session_affinity_ttl_seconds`, `web_application_firewall_policy_link`, `resource_state`, `custom_https_provisioning_state`, `custom_https_provisioning_substate` and `custom_https_configuration` under property `properties`
  - Model `HealthProbeSettingsModel` moved instance variable `path`, `protocol`, `interval_in_seconds`, `health_probe_method`, `enabled_state` and `resource_state` under property `properties`
  - Model `LoadBalancingSettingsModel` moved instance variable `sample_size`, `successful_samples_required`, `additional_latency_milliseconds` and `resource_state` under property `properties`
  - Model `PolicySettings` moved instance variable `state` and `scrubbing_rules` under property `log_scrubbing`
  - Model `ProfileUpdateModel` moved instance variable `enabled_state` under property `properties`
  - Model `RoutingRule` moved instance variable `frontend_endpoints`, `accepted_protocols`, `patterns_to_match`, `enabled_state`, `route_configuration`, `rules_engine`, `web_application_firewall_policy_link` and `resource_state` under property `properties`
  - Model `RulesEngine` moved instance variable `rules` and `resource_state` under property `properties`
  - Deleted or renamed model `AzureAsyncOperationResult`
  - Deleted or renamed model `Error`
  - Deleted or renamed model `ErrorDetails`
  - Deleted or renamed model `NetworkOperationStatus`
  - Method `ReportsOperations.get_latency_scorecards` changed its parameter `aggregation_interval`/`end_date_time_utc`/`country` from `positional_or_keyword` to `keyword_only`
  - Method `ReportsOperations.get_timeseries` changed its parameter `start_date_time_utc`/`end_date_time_utc`/`aggregation_interval`/`timeseries_type`/`endpoint`/`country` from `positional_or_keyword` to `keyword_only`

### Other Changes

  - Deleted model `ExperimentList`/`ManagedRuleSetDefinitionList`/`PreconfiguredEndpointList`/`ProfileList`/`WebApplicationFirewallPolicyList` which actually were not used by SDK users

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
