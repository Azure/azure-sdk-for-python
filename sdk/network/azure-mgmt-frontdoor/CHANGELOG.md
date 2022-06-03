# Release History

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
