.. :changelog:

Release History
===============

0.3.0 (2019-10-11)
++++++++++++++++++

- Fixed new network experiment SDK structure

0.2.0 (2019-10-09)
++++++++++++++++++

**Features**

- Model RoutingRule has a new parameter route_configuration
- Model PolicySettings has a new parameter redirect_url
- Model PolicySettings has a new parameter custom_block_response_body
- Model PolicySettings has a new parameter custom_block_response_status_code
- Model HealthProbeSettingsModel has a new parameter enabled_state
- Model HealthProbeSettingsModel has a new parameter health_probe_method
- Model HealthProbeSettingsUpdateParameters has a new parameter enabled_state
- Model HealthProbeSettingsUpdateParameters has a new parameter health_probe_method
- Model FrontDoorUpdateParameters has a new parameter backend_pools_settings
- Model CustomRule has a new parameter enabled_state
- Model FrontDoor has a new parameter backend_pools_settings
- Model RoutingRuleUpdateParameters has a new parameter route_configuration
- Added operation group ProfilesOperations
- Added operation group ExperimentsOperations
- Added operation group PreconfiguredEndpointsOperations
- Added operation group ManagedRuleSetsOperations
- Added operation group FrontDoorManagementClientOperationsMixin

**Breaking changes**

- Parameter certificate_source of model CustomHttpsConfiguration is now required
- Parameter protocol_type of model CustomHttpsConfiguration is now required
- Model RoutingRule no longer has parameter custom_forwarding_path
- Model RoutingRule no longer has parameter forwarding_protocol
- Model RoutingRule no longer has parameter cache_configuration
- Model RoutingRule no longer has parameter backend_pool
- Model CustomRule no longer has parameter etag
- Model CustomRule no longer has parameter transforms
- Model CustomHttpsConfiguration has a new required parameter minimum_tls_version
- Model RoutingRuleUpdateParameters no longer has parameter custom_forwarding_path
- Model RoutingRuleUpdateParameters no longer has parameter forwarding_protocol
- Model RoutingRuleUpdateParameters no longer has parameter cache_configuration
- Model RoutingRuleUpdateParameters no longer has parameter backend_pool
- Removed operation FrontendEndpointsOperations.delete
- Removed operation FrontendEndpointsOperations.create_or_update
- Model ManagedRuleSet has a new signature
- Removed operation group LoadBalancingSettingsOperations
- Removed operation group RoutingRulesOperations
- Removed operation group HealthProbeSettingsOperations
- Removed operation group BackendPoolsOperations

0.1.0 (2019-03-11)
++++++++++++++++++

* Initial Release
