# Release History

## 8.0.0 (2023-04-20)

### Features Added

  - Added operation BuildServiceBuilderOperations.list_deployments
  - Added operation BuildpackBindingOperations.list_for_cluster
  - Added operation DeploymentsOperations.begin_disable_remote_debugging
  - Added operation DeploymentsOperations.begin_enable_remote_debugging
  - Added operation DeploymentsOperations.get_remote_debugging_config
  - Added operation GatewaysOperations.begin_update_capacity
  - Added operation GatewaysOperations.list_env_secrets
  - Added operation group ApplicationAcceleratorsOperations
  - Added operation group ApplicationLiveViewsOperations
  - Added operation group CustomizedAcceleratorsOperations
  - Added operation group DevToolPortalsOperations
  - Added operation group PredefinedAcceleratorsOperations
  - Model AppResourceProperties has a new parameter ingress_settings
  - Model AppResourceProperties has a new parameter secrets
  - Model AzureFileVolume has a new parameter enable_sub_path
  - Model BuildResultProperties has a new parameter error
  - Model BuildStageProperties has a new parameter exit_code
  - Model BuildStageProperties has a new parameter reason
  - Model ClusterResourceProperties has a new parameter infra_resource_group
  - Model ClusterResourceProperties has a new parameter managed_environment_id
  - Model CustomPersistentDiskProperties has a new parameter enable_sub_path
  - Model DeploymentSettings has a new parameter scale
  - Model GatewayProperties has a new parameter apm_types
  - Model GatewayProperties has a new parameter environment_variables
  - Model GatewayRouteConfigProperties has a new parameter filters
  - Model GatewayRouteConfigProperties has a new parameter predicates
  - Model GatewayRouteConfigProperties has a new parameter protocol
  - Model GatewayRouteConfigProperties has a new parameter sso_enabled
  - Model NetworkProfile has a new parameter outbound_type

## 8.0.0b1 (2023-02-13)

### Features Added

  - Added operation BuildServiceBuilderOperations.list_deployments
  - Added operation DeploymentsOperations.begin_disable_remote_debugging
  - Added operation DeploymentsOperations.begin_enable_remote_debugging
  - Added operation DeploymentsOperations.get_remote_debugging_config
  - Added operation group ApplicationAcceleratorsOperations
  - Added operation group ApplicationLiveViewsOperations
  - Added operation group CustomizedAcceleratorsOperations
  - Added operation group DevToolPortalsOperations
  - Added operation group PredefinedAcceleratorsOperations
  - Model AppResourceProperties has a new parameter ingress_settings
  - Model GatewayRouteConfigProperties has a new parameter protocol
  - Model NetworkProfile has a new parameter outbound_type

### Breaking Changes

  - Model ClusterResourceProperties no longer has parameter marketplace_resource

## 7.1.0 (2022-05-16)

**Features**

  - Model AppResourceProperties has a new parameter vnet_addons
  - Model BuildProperties has a new parameter resource_requests
  - Model CertificateProperties has a new parameter provisioning_state
  - Model ClusterResourceProperties has a new parameter marketplace_resource
  - Model ClusterResourceProperties has a new parameter vnet_addons
  - Model ContentCertificateProperties has a new parameter provisioning_state
  - Model CustomContainer has a new parameter language_framework
  - Model CustomDomainProperties has a new parameter provisioning_state
  - Model DeploymentSettings has a new parameter liveness_probe
  - Model DeploymentSettings has a new parameter readiness_probe
  - Model DeploymentSettings has a new parameter startup_probe
  - Model DeploymentSettings has a new parameter termination_grace_period_seconds
  - Model GatewayRouteConfigProperties has a new parameter open_api
  - Model KeyVaultCertificateProperties has a new parameter provisioning_state
  - Model ManagedIdentityProperties has a new parameter user_assigned_identities
  - Model NetworkProfile has a new parameter ingress_config

## 7.0.0 (2022-02-22)

**Features**

  - Added operation AppsOperations.begin_set_active_deployments
  - Added operation DeploymentsOperations.begin_generate_heap_dump
  - Added operation DeploymentsOperations.begin_generate_thread_dump
  - Added operation DeploymentsOperations.begin_start_jfr
  - Added operation ServicesOperations.begin_start
  - Added operation ServicesOperations.begin_stop
  - Added operation group ApiPortalCustomDomainsOperations
  - Added operation group ApiPortalsOperations
  - Added operation group BuildServiceAgentPoolOperations
  - Added operation group BuildServiceBuilderOperations
  - Added operation group BuildServiceOperations
  - Added operation group BuildpackBindingOperations
  - Added operation group ConfigurationServicesOperations
  - Added operation group GatewayCustomDomainsOperations
  - Added operation group GatewayRouteConfigsOperations
  - Added operation group GatewaysOperations
  - Added operation group ServiceRegistriesOperations
  - Added operation group StoragesOperations
  - Model AppResource has a new parameter system_data
  - Model AppResourceProperties has a new parameter addon_configs
  - Model AppResourceProperties has a new parameter custom_persistent_disks
  - Model AppResourceProperties has a new parameter loaded_certificates
  - Model BindingResource has a new parameter system_data
  - Model CertificateResource has a new parameter system_data
  - Model ClusterResourceProperties has a new parameter fqdn
  - Model ClusterResourceProperties has a new parameter power_state
  - Model ClusterResourceProperties has a new parameter zone_redundant
  - Model ConfigServerResource has a new parameter system_data
  - Model CustomDomainResource has a new parameter system_data
  - Model DeploymentInstance has a new parameter zone
  - Model DeploymentResource has a new parameter system_data
  - Model DeploymentSettings has a new parameter addon_configs
  - Model DeploymentSettings has a new parameter container_probe_settings
  - Model MetricSpecification has a new parameter source_mdm_namespace
  - Model MonitoringSettingResource has a new parameter system_data
  - Model OperationDetail has a new parameter action_type
  - Model ProxyResource has a new parameter system_data
  - Model Resource has a new parameter system_data
  - Model ServiceResource has a new parameter system_data
  - Model TrackedResource has a new parameter system_data

**Breaking changes**

  - Model AppResourceProperties no longer has parameter active_deployment_name
  - Model AppResourceProperties no longer has parameter created_time
  - Model CertificateProperties has a new required parameter type
  - Model CertificateProperties no longer has parameter cert_version
  - Model CertificateProperties no longer has parameter key_vault_cert_name
  - Model CertificateProperties no longer has parameter vault_uri
  - Model DeploymentResourceProperties no longer has parameter app_name
  - Model DeploymentResourceProperties no longer has parameter created_time
  - Model DeploymentSettings no longer has parameter cpu
  - Model DeploymentSettings no longer has parameter jvm_options
  - Model DeploymentSettings no longer has parameter memory_in_gb
  - Model DeploymentSettings no longer has parameter net_core_main_entry_path
  - Model DeploymentSettings no longer has parameter runtime_version
  - Model UserSourceInfo no longer has parameter artifact_selector
  - Model UserSourceInfo no longer has parameter custom_container
  - Model UserSourceInfo no longer has parameter relative_path
  - Parameter type of model UserSourceInfo is now required
  - Removed operation group SkuOperations

## 6.1.0 (2021-07-09)

**Features**

  - Model UserSourceInfo has a new parameter custom_container
  - Model MetricDimension has a new parameter to_be_exported_for_shoebox
  - Model DeploymentSettings has a new parameter resource_requests

## 6.0.0 (2021-04-08)

**Features**

  - Model MonitoringSettingProperties has a new parameter app_insights_agent_versions
  - Model MonitoringSettingProperties has a new parameter app_insights_sampling_rate
  - Model AppResourceProperties has a new parameter enable_end_to_end_tls
  - Model NetworkProfile has a new parameter required_traffics

## 6.0.0b1 (2020-12-03)

This is beta preview version.

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

## 1.0.0 (2020-08-25)

  - Initial API version Release

## 0.1.0 (2019-10-25)

  - Additional pre-release API changes

## 0.1.0rc1 (2019-10-24)

  - Initial Release
