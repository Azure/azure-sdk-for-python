# Release History

## 9.0.0 (2024-10-14)

### Features Added

  - Client `HybridComputeManagementClient` added operation group `licenses`
  - Client `HybridComputeManagementClient` added operation group `license_profiles`
  - Client `HybridComputeManagementClient` added operation group `extension_metadata`
  - Client `HybridComputeManagementClient` added operation group `network_profile`
  - Client `HybridComputeManagementClient` added operation group `network_security_perimeter_configurations`
  - Model `AgentConfiguration` added property `config_mode`
  - Model `Machine` added property `resources`
  - Model `Machine` added property `kind`
  - Model `Machine` added property `location_data`
  - Model `Machine` added property `agent_configuration`
  - Model `Machine` added property `service_statuses`
  - Model `Machine` added property `cloud_metadata`
  - Model `Machine` added property `agent_upgrade`
  - Model `Machine` added property `os_profile`
  - Model `Machine` added property `license_profile`
  - Model `Machine` added property `provisioning_state`
  - Model `Machine` added property `status`
  - Model `Machine` added property `last_status_change`
  - Model `Machine` added property `error_details`
  - Model `Machine` added property `agent_version`
  - Model `Machine` added property `vm_id`
  - Model `Machine` added property `display_name`
  - Model `Machine` added property `machine_fqdn`
  - Model `Machine` added property `client_public_key`
  - Model `Machine` added property `os_name`
  - Model `Machine` added property `os_version`
  - Model `Machine` added property `os_type`
  - Model `Machine` added property `vm_uuid`
  - Model `Machine` added property `extensions`
  - Model `Machine` added property `os_sku`
  - Model `Machine` added property `os_edition`
  - Model `Machine` added property `domain_name`
  - Model `Machine` added property `ad_fqdn`
  - Model `Machine` added property `dns_fqdn`
  - Model `Machine` added property `private_link_scope_resource_id`
  - Model `Machine` added property `parent_cluster_resource_id`
  - Model `Machine` added property `mssql_discovered`
  - Model `Machine` added property `detected_properties`
  - Model `Machine` added property `network_profile`
  - Model `MachineExtensionUpdate` added parameter `force_update_tag` in method `__init__`
  - Model `MachineExtensionUpdate` added parameter `publisher` in method `__init__`
  - Model `MachineExtensionUpdate` added parameter `type` in method `__init__`
  - Model `MachineExtensionUpdate` added parameter `type_handler_version` in method `__init__`
  - Model `MachineExtensionUpdate` added parameter `enable_automatic_upgrade` in method `__init__`
  - Model `MachineExtensionUpdate` added parameter `auto_upgrade_minor_version` in method `__init__`
  - Model `MachineExtensionUpdate` added parameter `settings` in method `__init__`
  - Model `MachineExtensionUpdate` added parameter `protected_settings` in method `__init__`
  - Model `MachineUpdate` added property `kind`
  - Model `MachineUpdate` added property `location_data`
  - Model `MachineUpdate` added property `os_profile`
  - Model `MachineUpdate` added property `cloud_metadata`
  - Model `MachineUpdate` added property `agent_upgrade`
  - Model `MachineUpdate` added property `parent_cluster_resource_id`
  - Model `MachineUpdate` added property `private_link_scope_resource_id`
  - Model `OSProfileLinuxConfiguration` added property `enable_hotpatching`
  - Model `OSProfileLinuxConfiguration` added property `status`
  - Model `OSProfileWindowsConfiguration` added property `enable_hotpatching`
  - Model `OSProfileWindowsConfiguration` added property `status`
  - Enum `PublicNetworkAccessType` added member `SECURED_BY_PERIMETER`
  - Model `Resource` added property `system_data`
  - Added enum `AccessMode`
  - Added model `AccessRule`
  - Added enum `AccessRuleDirection`
  - Added enum `AgentConfigurationMode`
  - Added model `AgentUpgrade`
  - Added enum `ArcKindEnum`
  - Added model `AvailablePatchCountByClassification`
  - Added enum `EsuEligibility`
  - Added model `EsuKey`
  - Added enum `EsuKeyState`
  - Added enum `EsuServerType`
  - Added model `ExtensionValue`
  - Added model `ExtensionValueListResult`
  - Added model `ExtensionsResourceStatus`
  - Added enum `ExtensionsStatusLevelTypes`
  - Added enum `HotpatchEnablementStatus`
  - Added model `IpAddress`
  - Added model `KeyDetails`
  - Added model `KeyProperties`
  - Added enum `LastAttemptStatusEnum`
  - Added model `License`
  - Added enum `LicenseAssignmentState`
  - Added enum `LicenseCoreType`
  - Added model `LicenseDetails`
  - Added enum `LicenseEdition`
  - Added model `LicenseProfile`
  - Added model `LicenseProfileArmEsuProperties`
  - Added model `LicenseProfileArmEsuPropertiesWithoutAssignedLicense`
  - Added model `LicenseProfileMachineInstanceView`
  - Added model `LicenseProfileMachineInstanceViewEsuProperties`
  - Added enum `LicenseProfileProductType`
  - Added model `LicenseProfileStorageModelEsuProperties`
  - Added enum `LicenseProfileSubscriptionStatus`
  - Added enum `LicenseProfileSubscriptionStatusUpdate`
  - Added model `LicenseProfileUpdate`
  - Added model `LicenseProfilesListResult`
  - Added enum `LicenseState`
  - Added enum `LicenseStatus`
  - Added enum `LicenseTarget`
  - Added enum `LicenseType`
  - Added model `LicenseUpdate`
  - Added model `LicensesListResult`
  - Added model `LinuxParameters`
  - Added model `MachineAssessPatchesResult`
  - Added model `MachineInstallPatchesParameters`
  - Added model `MachineInstallPatchesResult`
  - Added model `NetworkInterface`
  - Added model `NetworkProfile`
  - Added model `NetworkSecurityPerimeter`
  - Added model `NetworkSecurityPerimeterConfiguration`
  - Added model `NetworkSecurityPerimeterConfigurationListResult`
  - Added model `NetworkSecurityPerimeterConfigurationReconcileResult`
  - Added model `NetworkSecurityPerimeterProfile`
  - Added enum `OsType`
  - Added enum `PatchOperationStartedBy`
  - Added enum `PatchOperationStatus`
  - Added enum `PatchServiceUsed`
  - Added model `PatchSettingsStatus`
  - Added model `ProductFeature`
  - Added model `ProductFeatureUpdate`
  - Added enum `ProgramYear`
  - Added model `ProvisioningIssue`
  - Added enum `ProvisioningIssueSeverity`
  - Added enum `ProvisioningIssueType`
  - Added enum `ProvisioningState`
  - Added model `ProxyResourceAutoGenerated`
  - Added model `ResourceAssociation`
  - Added model `ResourceAutoGenerated`
  - Added model `Subnet`
  - Added enum `VMGuestPatchClassificationLinux`
  - Added enum `VMGuestPatchClassificationWindows`
  - Added enum `VMGuestPatchRebootSetting`
  - Added enum `VMGuestPatchRebootStatus`
  - Added model `VolumeLicenseDetails`
  - Added model `WindowsParameters`
  - Operation group `MachinesOperations` added method `begin_assess_patches`
  - Operation group `MachinesOperations` added method `begin_install_patches`
  - Added Operation group `ExtensionMetadataOperations`
  - Added Operation group `LicenseProfilesOperations`
  - Added Operation group `LicensesOperations`
  - Added Operation group `NetworkProfileOperations`
  - Added Operation group `NetworkSecurityPerimeterConfigurationsOperations`

### Breaking Changes

  - Model `Machine` deleted or renamed its instance variable `properties`
  - Model `MachineExtensionUpdate` deleted or renamed its instance variable `properties`
  - Model `MachineUpdate` deleted or renamed its instance variable `properties`
  - Deleted or renamed model `MachineExtensionUpdateProperties`
  - Deleted or renamed model `MachineProperties`
  - Deleted or renamed model `MachineUpdateProperties`

## 9.0.0b4 (2024-07-23)

### Features Added

  - Added operation NetworkSecurityPerimeterConfigurationsOperations.begin_reconcile_for_private_link_scope
  - Model LicenseProfile has a new parameter billing_end_date
  - Model LicenseProfile has a new parameter error
  - Model LicenseProfileMachineInstanceView has a new parameter billing_end_date
  - Model LicenseProfileMachineInstanceView has a new parameter error
  - Model OSProfileLinuxConfiguration has a new parameter enable_hotpatching
  - Model OSProfileLinuxConfiguration has a new parameter status
  - Model OSProfileWindowsConfiguration has a new parameter enable_hotpatching
  - Model OSProfileWindowsConfiguration has a new parameter status
  - Model ProductFeature has a new parameter billing_end_date
  - Model ProductFeature has a new parameter error

### Breaking Changes

  - Removed operation MachineRunCommandsOperations.begin_update

## 9.0.0b3 (2024-05-30)

### Features Added

  - Added operation MachineRunCommandsOperations.begin_update
  - Added operation group GatewaysOperations
  - Added operation group LicensesOperations
  - Added operation group NetworkSecurityPerimeterConfigurationsOperations
  - Added operation group SettingsOperations
  - Model LicenseDetails has a new parameter volume_license_details

## 9.0.0b2 (2024-04-22)

### Features Added

  - Added operation group MachineRunCommandsOperations
  - Model LicenseProfile has a new parameter billing_start_date
  - Model LicenseProfile has a new parameter disenrollment_date
  - Model LicenseProfile has a new parameter enrollment_date
  - Model LicenseProfile has a new parameter product_features
  - Model LicenseProfile has a new parameter product_type
  - Model LicenseProfile has a new parameter software_assurance_customer
  - Model LicenseProfile has a new parameter subscription_status
  - Model LicenseProfileMachineInstanceView has a new parameter billing_start_date
  - Model LicenseProfileMachineInstanceView has a new parameter disenrollment_date
  - Model LicenseProfileMachineInstanceView has a new parameter enrollment_date
  - Model LicenseProfileMachineInstanceView has a new parameter license_channel
  - Model LicenseProfileMachineInstanceView has a new parameter license_status
  - Model LicenseProfileMachineInstanceView has a new parameter product_features
  - Model LicenseProfileMachineInstanceView has a new parameter product_type
  - Model LicenseProfileMachineInstanceView has a new parameter software_assurance_customer
  - Model LicenseProfileMachineInstanceView has a new parameter subscription_status
  - Model LicenseProfileUpdate has a new parameter product_features
  - Model LicenseProfileUpdate has a new parameter product_type
  - Model LicenseProfileUpdate has a new parameter software_assurance_customer
  - Model LicenseProfileUpdate has a new parameter subscription_status
  - Model Machine has a new parameter os_edition

### Breaking Changes

  - Removed operation group AgentVersionOperations
  - Removed operation group HybridIdentityMetadataOperations
  - Removed operation group LicenseProfilesOperations
  - Removed operation group LicensesOperations

## 9.0.0b1 (2023-11-20)

### Features Added

  - Added operation MachinesOperations.begin_assess_patches
  - Added operation MachinesOperations.begin_install_patches
  - Added operation group AgentVersionOperations
  - Added operation group ExtensionMetadataOperations
  - Added operation group HybridIdentityMetadataOperations
  - Added operation group LicenseProfilesOperations
  - Added operation group LicensesOperations
  - Added operation group NetworkProfileOperations
  - Model AgentConfiguration has a new parameter config_mode
  - Model Machine has a new parameter ad_fqdn
  - Model Machine has a new parameter agent_configuration
  - Model Machine has a new parameter agent_upgrade
  - Model Machine has a new parameter agent_version
  - Model Machine has a new parameter client_public_key
  - Model Machine has a new parameter cloud_metadata
  - Model Machine has a new parameter detected_properties
  - Model Machine has a new parameter display_name
  - Model Machine has a new parameter dns_fqdn
  - Model Machine has a new parameter domain_name
  - Model Machine has a new parameter error_details
  - Model Machine has a new parameter extensions
  - Model Machine has a new parameter kind
  - Model Machine has a new parameter last_status_change
  - Model Machine has a new parameter license_profile
  - Model Machine has a new parameter location_data
  - Model Machine has a new parameter machine_fqdn
  - Model Machine has a new parameter mssql_discovered
  - Model Machine has a new parameter network_profile
  - Model Machine has a new parameter os_name
  - Model Machine has a new parameter os_profile
  - Model Machine has a new parameter os_sku
  - Model Machine has a new parameter os_type
  - Model Machine has a new parameter os_version
  - Model Machine has a new parameter parent_cluster_resource_id
  - Model Machine has a new parameter private_link_scope_resource_id
  - Model Machine has a new parameter provisioning_state
  - Model Machine has a new parameter resources
  - Model Machine has a new parameter service_statuses
  - Model Machine has a new parameter status
  - Model Machine has a new parameter vm_id
  - Model Machine has a new parameter vm_uuid
  - Model MachineExtensionUpdate has a new parameter auto_upgrade_minor_version
  - Model MachineExtensionUpdate has a new parameter enable_automatic_upgrade
  - Model MachineExtensionUpdate has a new parameter force_update_tag
  - Model MachineExtensionUpdate has a new parameter protected_settings
  - Model MachineExtensionUpdate has a new parameter publisher
  - Model MachineExtensionUpdate has a new parameter settings
  - Model MachineExtensionUpdate has a new parameter type
  - Model MachineExtensionUpdate has a new parameter type_handler_version
  - Model MachineUpdate has a new parameter agent_upgrade
  - Model MachineUpdate has a new parameter cloud_metadata
  - Model MachineUpdate has a new parameter kind
  - Model MachineUpdate has a new parameter location_data
  - Model MachineUpdate has a new parameter os_profile
  - Model MachineUpdate has a new parameter parent_cluster_resource_id
  - Model MachineUpdate has a new parameter private_link_scope_resource_id
  - Model ProxyResource has a new parameter system_data
  - Model Resource has a new parameter system_data
  - Model TrackedResource has a new parameter system_data
  - Operation MachinesOperations.list_by_resource_group has a new optional parameter expand

### Breaking Changes

  - Model Machine no longer has parameter properties
  - Model MachineExtensionUpdate no longer has parameter properties
  - Model MachineUpdate no longer has parameter properties

## 8.0.0 (2023-02-15)

### Features Added

  - Added operation group HybridComputeManagementClientOperationsMixin
  - Model HybridComputePrivateLinkScopeProperties has a new parameter private_endpoint_connections
  - Model MachineExtensionProperties has a new parameter enable_automatic_upgrade
  - Model MachineProperties has a new parameter agent_configuration
  - Model MachineProperties has a new parameter cloud_metadata
  - Model MachineProperties has a new parameter mssql_discovered
  - Model MachineProperties has a new parameter os_type
  - Model MachineProperties has a new parameter service_statuses
  - Model MachineUpdateProperties has a new parameter cloud_metadata
  - Model MachineUpdateProperties has a new parameter os_profile
  - Model OSProfile has a new parameter linux_configuration
  - Model OSProfile has a new parameter windows_configuration
  - Model OperationValue has a new parameter is_data_action
  - Model PrivateEndpointConnectionProperties has a new parameter group_ids

## 8.0.0b1 (2022-11-18)

### Features Added

  - Added operation group ExtensionMetadataOperations
  - Added operation group HybridComputeManagementClientOperationsMixin
  - Model HybridComputePrivateLinkScopeProperties has a new parameter private_endpoint_connections
  - Model Machine has a new parameter ad_fqdn
  - Model Machine has a new parameter agent_configuration
  - Model Machine has a new parameter agent_version
  - Model Machine has a new parameter client_public_key
  - Model Machine has a new parameter cloud_metadata
  - Model Machine has a new parameter detected_properties
  - Model Machine has a new parameter display_name
  - Model Machine has a new parameter dns_fqdn
  - Model Machine has a new parameter domain_name
  - Model Machine has a new parameter error_details
  - Model Machine has a new parameter last_status_change
  - Model Machine has a new parameter location_data
  - Model Machine has a new parameter machine_fqdn
  - Model Machine has a new parameter mssql_discovered
  - Model Machine has a new parameter os_name
  - Model Machine has a new parameter os_profile
  - Model Machine has a new parameter os_sku
  - Model Machine has a new parameter os_type
  - Model Machine has a new parameter os_version
  - Model Machine has a new parameter parent_cluster_resource_id
  - Model Machine has a new parameter private_link_scope_resource_id
  - Model Machine has a new parameter provisioning_state
  - Model Machine has a new parameter resources
  - Model Machine has a new parameter service_statuses
  - Model Machine has a new parameter status
  - Model Machine has a new parameter vm_id
  - Model Machine has a new parameter vm_uuid
  - Model MachineExtension has a new parameter auto_upgrade_minor_version
  - Model MachineExtension has a new parameter enable_automatic_upgrade
  - Model MachineExtension has a new parameter force_update_tag
  - Model MachineExtension has a new parameter instance_view
  - Model MachineExtension has a new parameter protected_settings
  - Model MachineExtension has a new parameter provisioning_state
  - Model MachineExtension has a new parameter publisher
  - Model MachineExtension has a new parameter settings
  - Model MachineExtension has a new parameter type_handler_version
  - Model MachineExtension has a new parameter type_properties_type
  - Model MachineExtensionUpdate has a new parameter auto_upgrade_minor_version
  - Model MachineExtensionUpdate has a new parameter enable_automatic_upgrade
  - Model MachineExtensionUpdate has a new parameter force_update_tag
  - Model MachineExtensionUpdate has a new parameter protected_settings
  - Model MachineExtensionUpdate has a new parameter publisher
  - Model MachineExtensionUpdate has a new parameter settings
  - Model MachineExtensionUpdate has a new parameter type
  - Model MachineExtensionUpdate has a new parameter type_handler_version
  - Model MachineUpdate has a new parameter cloud_metadata
  - Model MachineUpdate has a new parameter location_data
  - Model MachineUpdate has a new parameter os_profile
  - Model MachineUpdate has a new parameter parent_cluster_resource_id
  - Model MachineUpdate has a new parameter private_link_scope_resource_id
  - Model OSProfile has a new parameter linux_configuration
  - Model OSProfile has a new parameter windows_configuration
  - Model OperationValue has a new parameter is_data_action
  - Model PrivateEndpointConnectionProperties has a new parameter group_ids
  - Model ProxyResource has a new parameter system_data
  - Model Resource has a new parameter system_data
  - Model TrackedResource has a new parameter system_data

### Breaking Changes

  - Model Machine no longer has parameter properties
  - Model MachineExtension no longer has parameter properties
  - Model MachineExtensionUpdate no longer has parameter properties
  - Model MachineUpdate no longer has parameter properties

## 7.0.0 (2021-04-15)

**Features**

  - Model MachineUpdateProperties has a new parameter private_link_scope_resource_id
  - Model MachineUpdateProperties has a new parameter parent_cluster_resource_id
  - Model MachineProperties has a new parameter private_link_scope_resource_id
  - Model MachineProperties has a new parameter parent_cluster_resource_id
  - Model MachineProperties has a new parameter detected_properties
  - Added operation group PrivateLinkResourcesOperations
  - Added operation group PrivateEndpointConnectionsOperations
  - Added operation group PrivateLinkScopesOperations

**Breaking changes**

  - Operation MachinesOperations.delete has a new signature
  - Operation MachinesOperations.get has a new signature
  - Model ErrorDetail has a new signature
  - Model OperationValue has a new signature
  - Model Machine has a new signature
  - Model MachineExtension has a new signature
  - Model MachineExtensionInstanceViewStatus has a new signature
  - Model MachineUpdate has a new signature
  - Model MachineExtensionUpdate has a new signature

## 7.0.0b1 (2020-12-07)

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

## 2.0.0 (2020-09-08)

**Features**

  - Model Machine has a new parameter ad_fqdn
  - Model Machine has a new parameter os_sku
  - Model Machine has a new parameter domain_name
  - Model Machine has a new parameter dns_fqdn
  - Model Machine has a new parameter vm_uuid
  - Model MachineProperties has a new parameter ad_fqdn
  - Model MachineProperties has a new parameter os_sku
  - Model MachineProperties has a new parameter domain_name
  - Model MachineProperties has a new parameter dns_fqdn
  - Model MachineProperties has a new parameter vm_uuid

**Breaking changes**

  - Model ErrorResponse has a new signature
  - Model MachineExtensionInstanceViewStatus has a new signature

## 1.0.0 (2020-08-19)

**Features**

  - Model Machine has a new parameter identity
  - Model Machine has a new parameter location_data
  - Model MachineUpdate has a new parameter location_data
  - Added operation group MachineExtensionsOperations

**Breaking changes**

  - Model MachineExtension no longer has parameter tenant_id
  - Model MachineExtension no longer has parameter principal_id
  - Model MachineExtension no longer has parameter type1
  - Model Machine no longer has parameter tenant_id
  - Model Machine no longer has parameter physical_location
  - Model Machine no longer has parameter principal_id
  - Model Machine no longer has parameter type1
  - Model MachineUpdate no longer has parameter physical_location
  - Model Resource no longer has parameter tenant_id
  - Model Resource no longer has parameter principal_id
  - Model Resource no longer has parameter location
  - Model Resource no longer has parameter type1
  - Model Resource no longer has parameter tags
  - Model ErrorResponse has a new signature

## 0.1.1 (2019-10-30)

  - Update project description and title

## 0.1.0 (2019-10-29)

**Breaking changes**

  - Removed MachineExtensionsOperations

## 0.1.0rc1 (2019-10-23)

  - Initial Release
