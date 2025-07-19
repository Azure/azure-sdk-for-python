# Release History

## 3.1.0b3 (2025-08-17)

### Features Added

  - Client `NginxManagementClient` added operation group `nginx_deployments`
  - Client `NginxManagementClient` added operation group `waf_policies`
  - Enum `IdentityType` added member `SYSTEM_AND_USER_ASSIGNED`
  - Model `NginxDeploymentScalingProperties` added property `auto_scale_settings`
  - Model `NginxDeploymentUpdateProperties` added property `nginx_version`
  - Model `NginxDeploymentUpdateProperties` added property `ip_address`
  - Model `NginxDeploymentUpdateProperties` added property `dataplane_api_endpoint`
  - Model `WebApplicationFirewallStatus` added property `waf_release`
  - Added enum `ActionType`
  - Added model `AnalysisConfig`
  - Added model `AnalysisResultContent`
  - Added model `ApiKey`
  - Added model `ApiKeyListResult`
  - Added model `ApiKeyRequest`
  - Added model `ApiKeyRequestProperties`
  - Added model `ApiKeyResponseProperties`
  - Added model `AutoScaleSettings`
  - Added model `AutoScaleSettingsUpdate`
  - Added model `AutoUpgradeProfileUpdate`
  - Added model `AzureResourceManagerCommonTypesManagedServiceIdentityUpdate`
  - Added model `AzureResourceManagerCommonTypesSkuUpdate`
  - Added model `AzureResourceManagerResourceSkuProperty`
  - Added model `Certificate`
  - Added model `CertificateListResult`
  - Added model `CertificateUpdate`
  - Added model `CertificateUpdateProperties`
  - Added model `Configuration`
  - Added model `ConfigurationListResult`
  - Added model `ConfigurationUpdate`
  - Added model `ConfigurationUpdateProperties`
  - Added model `DeploymentWafPolicyApplyingStatus`
  - Added model `DeploymentWafPolicyCompilingStatus`
  - Added enum `DiagnosticLevel`
  - Added model `ManagedServiceIdentity`
  - Added enum `ManagedServiceIdentityType`
  - Added model `NginxAppProtect`
  - Added model `NginxAppProtectUpdate`
  - Added model `NginxConfigurationProtectedFileContent`
  - Added model `NginxConfigurationProtectedFileResult`
  - Added model `NginxDeploymentDefaultWafPolicy`
  - Added model `NginxDeploymentDefaultWafPolicyListResponse`
  - Added model `NginxDeploymentListResult`
  - Added model `NginxDeploymentPatchProperties`
  - Added model `NginxDeploymentScalingPropertiesUpdate`
  - Added model `NginxDeploymentTag`
  - Added model `NginxDeploymentUpdate`
  - Added model `NginxDeploymentUserProfileUpdate`
  - Added model `NginxDeploymentWafPolicyMetadata`
  - Added model `NginxDeploymentWafPolicyMetadataListResult`
  - Added model `NginxDeploymentWafPolicyMetadataProperties`
  - Added model `NginxDeploymentWafPolicyProperties`
  - Added model `NginxFrontendIPConfigurationUpdate`
  - Added model `NginxLoggingUpdate`
  - Added model `NginxNetworkInterfaceConfigurationUpdate`
  - Added model `NginxNetworkProfileUpdate`
  - Added model `NginxStorageAccountUpdate`
  - Added model `Operation`
  - Added enum `Origin`
  - Added model `ProxyResource`
  - Added model `Resource`
  - Added model `Sku`
  - Added enum `SkuTier`
  - Added model `TrackedResource`
  - Added model `UserAssignedIdentity`
  - Added model `WafPolicy`
  - Added model `WebApplicationFirewallComponentVersionsUpdate`
  - Added model `WebApplicationFirewallPackageUpdate`
  - Added model `WebApplicationFirewallSettingsUpdate`
  - Added model `WebApplicationFirewallStatusUpdate`
  - Model `ApiKeysOperations` added method `begin_delete`
  - Model `ApiKeysOperations` added method `list_by_deployment`
  - Model `CertificatesOperations` added method `list_by_deployment`
  - Model `ConfigurationsOperations` added method `analyze`
  - Model `ConfigurationsOperations` added method `create_or_update`
  - Model `ConfigurationsOperations` added method `list_by_deployment`
  - Added model `NginxDeploymentsOperations`
  - Added model `WafPoliciesOperations`

### Breaking Changes

  - Deleted or renamed client operation group `NginxManagementClient.deployments`
  - Method `IdentityProperties.__init__` removed default value `None` from its parameter `type`
  - Method `IdentityProperties.__init__` removed default value `None` from its parameter `user_assigned_identities`
  - Deleted or renamed enum value `IdentityType.SYSTEM_ASSIGNED_USER_ASSIGNED`
  - Method `NginxDeployment.__init__` removed default value `None` from its parameter `location`
  - Method `NginxDeploymentListResponse.__init__` removed default value `None` from its parameter `value`
  - Method `NginxDeploymentProperties.__init__` removed default value `None` from its parameter `network_profile`
  - Method `NginxDeploymentProperties.__init__` removed default value `None` from its parameter `enable_diagnostics_support`
  - Method `NginxDeploymentProperties.__init__` removed default value `None` from its parameter `logging`
  - Method `NginxDeploymentProperties.__init__` removed default value `None` from its parameter `scaling_properties`
  - Method `NginxDeploymentProperties.__init__` removed default value `None` from its parameter `auto_upgrade_profile`
  - Method `NginxDeploymentProperties.__init__` removed default value `None` from its parameter `user_profile`
  - Method `NginxDeploymentProperties.__init__` removed default value `None` from its parameter `nginx_app_protect`
  - Model `NginxDeploymentScalingProperties` deleted or renamed its instance variable `profiles`
  - Method `NginxDeploymentScalingProperties.__init__` removed default value `None` from its parameter `capacity`
  - Method `NginxDeploymentUpdateParameters.__init__` removed default value `None` from its parameter `identity`
  - Method `NginxDeploymentUpdateParameters.__init__` removed default value `None` from its parameter `tags`
  - Method `NginxDeploymentUpdateParameters.__init__` removed default value `None` from its parameter `sku`
  - Method `NginxDeploymentUpdateParameters.__init__` removed default value `None` from its parameter `location`
  - Method `NginxDeploymentUpdateParameters.__init__` removed default value `None` from its parameter `properties`
  - Method `NginxDeploymentUserProfile.__init__` removed default value `None` from its parameter `preferred_email`
  - Method `NginxFrontendIPConfiguration.__init__` removed default value `None` from its parameter `public_ip_addresses`
  - Method `NginxFrontendIPConfiguration.__init__` removed default value `None` from its parameter `private_ip_addresses`
  - Method `NginxLogging.__init__` removed default value `None` from its parameter `storage_account`
  - Method `NginxNetworkInterfaceConfiguration.__init__` removed default value `None` from its parameter `subnet_id`
  - Method `NginxNetworkProfile.__init__` removed default value `None` from its parameter `front_end_ip_configuration`
  - Method `NginxNetworkProfile.__init__` removed default value `None` from its parameter `network_interface_configuration`
  - Method `NginxPrivateIPAddress.__init__` removed default value `None` from its parameter `private_ip_address`
  - Method `NginxPrivateIPAddress.__init__` removed default value `None` from its parameter `private_ip_allocation_method`
  - Method `NginxPrivateIPAddress.__init__` removed default value `None` from its parameter `subnet_id`
  - Method `NginxPublicIPAddress.__init__` removed default value `None` from its parameter `id`
  - Method `NginxStorageAccount.__init__` removed default value `None` from its parameter `account_name`
  - Method `NginxStorageAccount.__init__` removed default value `None` from its parameter `container_name`
  - Method `WebApplicationFirewallSettings.__init__` removed default value `None` from its parameter `activation_state`
  - Deleted or renamed model `AnalysisCreateConfig`
  - Deleted or renamed model `AnalysisResultData`
  - Deleted or renamed model `Level`
  - Deleted or renamed model `NginxCertificate`
  - Deleted or renamed model `NginxCertificateListResponse`
  - Deleted or renamed model `NginxConfigurationListResponse`
  - Deleted or renamed model `NginxConfigurationProtectedFileRequest`
  - Deleted or renamed model `NginxConfigurationProtectedFileResponse`
  - Deleted or renamed model `NginxConfigurationResponse`
  - Deleted or renamed model `NginxDeploymentApiKeyListResponse`
  - Deleted or renamed model `NginxDeploymentApiKeyRequest`
  - Deleted or renamed model `NginxDeploymentApiKeyRequestProperties`
  - Deleted or renamed model `NginxDeploymentApiKeyResponse`
  - Deleted or renamed model `NginxDeploymentApiKeyResponseProperties`
  - Deleted or renamed model `NginxDeploymentPropertiesNginxAppProtect`
  - Deleted or renamed model `NginxDeploymentUpdatePropertiesNginxAppProtect`
  - Deleted or renamed model `OperationResult`
  - Method `ApiKeysOperations.create_or_update` inserted a `positional_or_keyword` parameter `nginx_deployment_name`
  - Method `ApiKeysOperations.create_or_update` inserted a `positional_or_keyword` parameter `resource`
  - Method `ApiKeysOperations.create_or_update` deleted or renamed its parameter `deployment_name` of kind `positional_or_keyword`
  - Method `ApiKeysOperations.create_or_update` deleted or renamed its parameter `body` of kind `positional_or_keyword`
  - Method `ApiKeysOperations.get` inserted a `positional_or_keyword` parameter `nginx_deployment_name`
  - Method `ApiKeysOperations.get` deleted or renamed its parameter `deployment_name` of kind `positional_or_keyword`
  - Deleted or renamed method `ApiKeysOperations.delete`
  - Deleted or renamed method `ApiKeysOperations.list`
  - Method `CertificatesOperations.begin_create_or_update` inserted a `positional_or_keyword` parameter `nginx_deployment_name`
  - Method `CertificatesOperations.begin_create_or_update` inserted a `positional_or_keyword` parameter `resource`
  - Method `CertificatesOperations.begin_create_or_update` deleted or renamed its parameter `deployment_name` of kind `positional_or_keyword`
  - Method `CertificatesOperations.begin_create_or_update` deleted or renamed its parameter `body` of kind `positional_or_keyword`
  - Method `CertificatesOperations.begin_delete` inserted a `positional_or_keyword` parameter `nginx_deployment_name`
  - Method `CertificatesOperations.begin_delete` deleted or renamed its parameter `deployment_name` of kind `positional_or_keyword`
  - Method `CertificatesOperations.get` inserted a `positional_or_keyword` parameter `nginx_deployment_name`
  - Method `CertificatesOperations.get` deleted or renamed its parameter `deployment_name` of kind `positional_or_keyword`
  - Deleted or renamed method `CertificatesOperations.list`
  - Method `ConfigurationsOperations.begin_delete` inserted a `positional_or_keyword` parameter `nginx_deployment_name`
  - Method `ConfigurationsOperations.begin_delete` deleted or renamed its parameter `deployment_name` of kind `positional_or_keyword`
  - Method `ConfigurationsOperations.get` inserted a `positional_or_keyword` parameter `nginx_deployment_name`
  - Method `ConfigurationsOperations.get` deleted or renamed its parameter `deployment_name` of kind `positional_or_keyword`
  - Deleted or renamed method `ConfigurationsOperations.analysis`
  - Deleted or renamed method `ConfigurationsOperations.begin_create_or_update`
  - Deleted or renamed method `ConfigurationsOperations.list`
  - Deleted or renamed model `DeploymentsOperations`
  - Method `ApiKeysOperations.get` re-ordered its parameters from `['self', 'resource_group_name', 'deployment_name', 'api_key_name', 'kwargs']` to `['self', 'resource_group_name', 'nginx_deployment_name', 'api_key_name', 'kwargs']`
  - Method `ApiKeysOperations.create_or_update` re-ordered its parameters from `['self', 'resource_group_name', 'deployment_name', 'api_key_name', 'body', 'kwargs']` to `['self', 'resource_group_name', 'nginx_deployment_name', 'api_key_name', 'resource', 'kwargs']`
  - Method `ConfigurationsOperations.get` re-ordered its parameters from `['self', 'resource_group_name', 'deployment_name', 'configuration_name', 'kwargs']` to `['self', 'resource_group_name', 'nginx_deployment_name', 'configuration_name', 'kwargs']`
  - Method `ConfigurationsOperations.begin_delete` re-ordered its parameters from `['self', 'resource_group_name', 'deployment_name', 'configuration_name', 'kwargs']` to `['self', 'resource_group_name', 'nginx_deployment_name', 'configuration_name', 'kwargs']`
  - Method `CertificatesOperations.begin_create_or_update` re-ordered its parameters from `['self', 'resource_group_name', 'deployment_name', 'certificate_name', 'body', 'kwargs']` to `['self', 'resource_group_name', 'nginx_deployment_name', 'certificate_name', 'resource', 'kwargs']`
  - Method `CertificatesOperations.get` re-ordered its parameters from `['self', 'resource_group_name', 'deployment_name', 'certificate_name', 'kwargs']` to `['self', 'resource_group_name', 'nginx_deployment_name', 'certificate_name', 'kwargs']`
  - Method `CertificatesOperations.begin_delete` re-ordered its parameters from `['self', 'resource_group_name', 'deployment_name', 'certificate_name', 'kwargs']` to `['self', 'resource_group_name', 'nginx_deployment_name', 'certificate_name', 'kwargs']`

## 3.1.0b2 (2025-02-23)

### Features Added

  - Client `NginxManagementClient` added operation group `api_keys`
  - Model `AnalysisResultData` added property `diagnostics`
  - Model `NginxDeploymentProperties` added property `nginx_app_protect`
  - Model `NginxDeploymentProperties` added property `dataplane_api_endpoint`
  - Model `NginxDeploymentUpdateProperties` added property `network_profile`
  - Model `NginxDeploymentUpdateProperties` added property `nginx_app_protect`
  - Added enum `ActivationState`
  - Added model `DiagnosticItem`
  - Added model `ErrorResponse`
  - Added enum `Level`
  - Added model `NginxConfigurationProtectedFileRequest`
  - Added model `NginxConfigurationProtectedFileResponse`
  - Added model `NginxConfigurationRequest`
  - Added model `NginxConfigurationRequestProperties`
  - Added model `NginxConfigurationResponse`
  - Added model `NginxConfigurationResponseProperties`
  - Added model `NginxDeploymentApiKeyListResponse`
  - Added model `NginxDeploymentApiKeyRequest`
  - Added model `NginxDeploymentApiKeyRequestProperties`
  - Added model `NginxDeploymentApiKeyResponse`
  - Added model `NginxDeploymentApiKeyResponseProperties`
  - Added model `NginxDeploymentPropertiesNginxAppProtect`
  - Added model `NginxDeploymentUpdatePropertiesNginxAppProtect`
  - Added model `WebApplicationFirewallComponentVersions`
  - Added model `WebApplicationFirewallPackage`
  - Added model `WebApplicationFirewallSettings`
  - Added model `WebApplicationFirewallStatus`
  - Added operation group `ApiKeysOperations`

### Breaking Changes

  - Model `NginxDeploymentProperties` deleted or renamed its instance variable `managed_resource_group`
  - Deleted or renamed model `NginxConfiguration`
  - Deleted or renamed model `NginxConfigurationProperties`
  - Deleted or renamed model `ResourceProviderDefaultErrorResponse`

## 3.1.0b1 (2024-03-18)

### Features Added

  - Added operation ConfigurationsOperations.analysis
  - Model NginxCertificateProperties has a new parameter certificate_error
  - Model NginxCertificateProperties has a new parameter key_vault_secret_created
  - Model NginxCertificateProperties has a new parameter key_vault_secret_version
  - Model NginxCertificateProperties has a new parameter sha1_thumbprint
  - Model NginxDeploymentProperties has a new parameter auto_upgrade_profile
  - Model NginxDeploymentScalingProperties has a new parameter profiles
  - Model NginxDeploymentUpdateProperties has a new parameter auto_upgrade_profile

## 3.0.0 (2023-11-20)

### Features Added

  - Model NginxConfigurationPackage has a new parameter protected_files
  - Model NginxDeploymentProperties has a new parameter scaling_properties
  - Model NginxDeploymentProperties has a new parameter user_profile
  - Model NginxDeploymentUpdateProperties has a new parameter scaling_properties
  - Model NginxDeploymentUpdateProperties has a new parameter user_profile

### Breaking Changes

  - Model NginxCertificate no longer has parameter tags
  - Model NginxConfiguration no longer has parameter tags

## 2.1.0 (2023-03-14)

### Other Changes

  - Regular update

## 2.1.0b1 (2022-12-29)

### Other Changes

  - Added generated samples in github repo
  - Drop support for python<3.7.0

## 2.0.0 (2022-10-18)

### Features Added

  - Added operation CertificatesOperations.begin_create_or_update
  - Added operation DeploymentsOperations.begin_create_or_update

### Breaking Changes

  - Removed operation CertificatesOperations.begin_create
  - Removed operation DeploymentsOperations.begin_create

## 1.1.0 (2022-09-20)

### Features Added

  - Model NginxConfigurationProperties has a new parameter protected_files

## 1.0.0 (2022-08-26)

### Features Added

  - Model NginxDeploymentProperties has a new parameter logging
  - Model NginxDeploymentUpdateProperties has a new parameter logging

## 1.0.0b1 (2022-06-13)

* Initial Release
