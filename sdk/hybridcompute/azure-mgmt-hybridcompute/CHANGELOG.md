# Release History

## 10.0.0 (2026-07-24)

### Features Added

  - Client `HybridComputeManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `HybridComputeManagementClient` added method `begin_setup_extensions`
  - Client `HybridComputeManagementClient` added method `send_request`
  - Client `HybridComputeManagementClient` added operation group `extension_metadata_v2`
  - Client `HybridComputeManagementClient` added operation group `extension_publisher`
  - Client `HybridComputeManagementClient` added operation group `extension_type`
  - Client `HybridComputeManagementClient` added operation group `gateways`
  - Client `HybridComputeManagementClient` added operation group `machine_run_commands`
  - Client `HybridComputeManagementClient` added operation group `settings`
  - Model `AccessRule` added property `properties`
  - Model `ExtensionValue` added property `properties`
  - Model `HybridComputePrivateLinkScopeProperties` added property `service_extensions`
  - Model `License` added property `properties`
  - Model `LicenseProfile` added property `properties`
  - Model `LicenseProfileMachineInstanceView` added property `product_profile`
  - Model `LicenseProfileMachineInstanceView` added property `software_assurance`
  - Model `LicenseProfileUpdate` added property `properties`
  - Enum `LicenseTarget` added member `WINDOWS_SERVER2016`
  - Model `LicenseUpdate` added property `properties`
  - Model `Machine` added property `properties`
  - Model `MachineExtensionUpdate` added property `properties`
  - Model `MachineUpdate` added property `properties`
  - Model `NetworkInterface` added property `id`
  - Model `NetworkInterface` added property `mac_address`
  - Model `NetworkInterface` added property `name`
  - Model `NetworkSecurityPerimeterConfiguration` added property `properties`
  - Model `NetworkSecurityPerimeterConfiguration` added property `system_data`
  - Model `ProvisioningIssue` added property `properties`
  - Enum `StatusTypes` added member `AWAITING_CONNECTION`
  - Model `WindowsParameters` added property `patch_name_masks_to_exclude`
  - Model `WindowsParameters` added property `patch_name_masks_to_include`
  - Added model `AccessRuleProperties`
  - Added model `Disk`
  - Added model `EsuProfileUpdateProperties`
  - Added enum `ExecutionState`
  - Added model `ExtensionPublisher`
  - Added model `ExtensionType`
  - Added model `ExtensionValueProperties`
  - Added model `ExtensionValueV2`
  - Added model `ExtensionValueV2Properties`
  - Added model `FirmwareProfile`
  - Added model `Gateway`
  - Added model `GatewayProperties`
  - Added enum `GatewayType`
  - Added model `GatewayUpdate`
  - Added model `GatewayUpdateProperties`
  - Added model `HardwareProfile`
  - Added enum `IdentityKeyStore`
  - Added model `LicenseProfileArmProductProfileProperties`
  - Added model `LicenseProfileMachineInstanceViewSoftwareAssurance`
  - Added model `LicenseProfileProperties`
  - Added model `LicenseProfilePropertiesSoftwareAssurance`
  - Added model `LicenseProfileUpdateProperties`
  - Added model `LicenseProfileUpdatePropertiesSoftwareAssurance`
  - Added model `LicenseProperties`
  - Added model `LicenseUpdateProperties`
  - Added model `LicenseUpdatePropertiesLicenseDetails`
  - Added model `MachineExtensionUpdateProperties`
  - Added model `MachineProperties`
  - Added model `MachineRunCommand`
  - Added model `MachineRunCommandInstanceView`
  - Added model `MachineRunCommandProperties`
  - Added model `MachineRunCommandScriptSource`
  - Added enum `MachineStatusReason`
  - Added model `MachineUpdateProperties`
  - Added model `ManagedServiceIdentity`
  - Added enum `ManagedServiceIdentityType`
  - Added model `NetworkSecurityPerimeterConfigurationProperties`
  - Added model `PatchSettings`
  - Added model `Processor`
  - Added model `ProductProfileUpdateProperties`
  - Added model `ProvisioningIssueProperties`
  - Added model `RunCommandInputParameter`
  - Added model `RunCommandManagedIdentity`
  - Added model `ServiceExtension`
  - Added enum `ServiceExtensionPublicNetworkAccess`
  - Added model `Settings`
  - Added model `SettingsGatewayProperties`
  - Added model `SettingsProperties`
  - Added model `SetupExtensionRequest`
  - Added model `StorageProfile`
  - Added model `UserAssignedIdentity`
  - Model `MachinesOperations` added method `begin_delete`
  - Model `MachinesOperations` added method `create_or_update`
  - Added operation group `ExtensionMetadataV2Operations`
  - Added operation group `ExtensionPublisherOperations`
  - Added operation group `ExtensionTypeOperations`
  - Added operation group `GatewaysOperations`
  - Added operation group `MachineRunCommandsOperations`
  - Added operation group `SettingsOperations`

### Breaking Changes

  - Model `AccessRule` deleted or renamed its instance variable `address_prefixes`
  - Model `AccessRule` deleted or renamed its instance variable `direction`
  - Model `ExtensionValue` deleted or renamed its instance variable `extension_type`
  - Model `ExtensionValue` deleted or renamed its instance variable `publisher`
  - Model `ExtensionValue` deleted or renamed its instance variable `version`
  - Model `License` deleted or renamed its instance variable `license_details`
  - Model `License` deleted or renamed its instance variable `license_type`
  - Model `License` deleted or renamed its instance variable `provisioning_state`
  - Model `License` deleted or renamed its instance variable `tenant_id`
  - Model `LicenseProfile` deleted or renamed its instance variable `assigned_license`
  - Model `LicenseProfile` deleted or renamed its instance variable `assigned_license_immutable_id`
  - Model `LicenseProfile` deleted or renamed its instance variable `billing_end_date`
  - Model `LicenseProfile` deleted or renamed its instance variable `billing_start_date`
  - Model `LicenseProfile` deleted or renamed its instance variable `disenrollment_date`
  - Model `LicenseProfile` deleted or renamed its instance variable `enrollment_date`
  - Model `LicenseProfile` deleted or renamed its instance variable `error`
  - Model `LicenseProfile` deleted or renamed its instance variable `esu_eligibility`
  - Model `LicenseProfile` deleted or renamed its instance variable `esu_key_state`
  - Model `LicenseProfile` deleted or renamed its instance variable `esu_keys`
  - Model `LicenseProfile` deleted or renamed its instance variable `product_features`
  - Model `LicenseProfile` deleted or renamed its instance variable `product_type`
  - Model `LicenseProfile` deleted or renamed its instance variable `provisioning_state`
  - Model `LicenseProfile` deleted or renamed its instance variable `server_type`
  - Model `LicenseProfile` deleted or renamed its instance variable `software_assurance_customer`
  - Model `LicenseProfile` deleted or renamed its instance variable `subscription_status`
  - Model `LicenseProfileMachineInstanceView` deleted or renamed its instance variable `billing_end_date`
  - Model `LicenseProfileMachineInstanceView` deleted or renamed its instance variable `billing_start_date`
  - Model `LicenseProfileMachineInstanceView` deleted or renamed its instance variable `disenrollment_date`
  - Model `LicenseProfileMachineInstanceView` deleted or renamed its instance variable `enrollment_date`
  - Model `LicenseProfileMachineInstanceView` deleted or renamed its instance variable `error`
  - Model `LicenseProfileMachineInstanceView` deleted or renamed its instance variable `product_features`
  - Model `LicenseProfileMachineInstanceView` deleted or renamed its instance variable `product_type`
  - Model `LicenseProfileMachineInstanceView` deleted or renamed its instance variable `software_assurance_customer`
  - Model `LicenseProfileMachineInstanceView` deleted or renamed its instance variable `subscription_status`
  - Model `LicenseProfileUpdate` deleted or renamed its instance variable `assigned_license`
  - Model `LicenseProfileUpdate` deleted or renamed its instance variable `product_features`
  - Model `LicenseProfileUpdate` deleted or renamed its instance variable `product_type`
  - Model `LicenseProfileUpdate` deleted or renamed its instance variable `software_assurance_customer`
  - Model `LicenseProfileUpdate` deleted or renamed its instance variable `subscription_status`
  - Model `LicenseUpdate` deleted or renamed its instance variable `edition`
  - Model `LicenseUpdate` deleted or renamed its instance variable `license_type`
  - Model `LicenseUpdate` deleted or renamed its instance variable `processors`
  - Model `LicenseUpdate` deleted or renamed its instance variable `state`
  - Model `LicenseUpdate` deleted or renamed its instance variable `target`
  - Model `LicenseUpdate` deleted or renamed its instance variable `type`
  - Model `Machine` deleted or renamed its instance variable `ad_fqdn`
  - Model `Machine` deleted or renamed its instance variable `agent_configuration`
  - Model `Machine` deleted or renamed its instance variable `agent_upgrade`
  - Model `Machine` deleted or renamed its instance variable `agent_version`
  - Model `Machine` deleted or renamed its instance variable `client_public_key`
  - Model `Machine` deleted or renamed its instance variable `cloud_metadata`
  - Model `Machine` deleted or renamed its instance variable `detected_properties`
  - Model `Machine` deleted or renamed its instance variable `display_name`
  - Model `Machine` deleted or renamed its instance variable `dns_fqdn`
  - Model `Machine` deleted or renamed its instance variable `domain_name`
  - Model `Machine` deleted or renamed its instance variable `error_details`
  - Model `Machine` deleted or renamed its instance variable `extensions`
  - Model `Machine` deleted or renamed its instance variable `last_status_change`
  - Model `Machine` deleted or renamed its instance variable `license_profile`
  - Model `Machine` deleted or renamed its instance variable `location_data`
  - Model `Machine` deleted or renamed its instance variable `machine_fqdn`
  - Model `Machine` deleted or renamed its instance variable `mssql_discovered`
  - Model `Machine` deleted or renamed its instance variable `network_profile`
  - Model `Machine` deleted or renamed its instance variable `os_edition`
  - Model `Machine` deleted or renamed its instance variable `os_name`
  - Model `Machine` deleted or renamed its instance variable `os_profile`
  - Model `Machine` deleted or renamed its instance variable `os_sku`
  - Model `Machine` deleted or renamed its instance variable `os_type`
  - Model `Machine` deleted or renamed its instance variable `os_version`
  - Model `Machine` deleted or renamed its instance variable `parent_cluster_resource_id`
  - Model `Machine` deleted or renamed its instance variable `private_link_scope_resource_id`
  - Model `Machine` deleted or renamed its instance variable `provisioning_state`
  - Model `Machine` deleted or renamed its instance variable `service_statuses`
  - Model `Machine` deleted or renamed its instance variable `status`
  - Model `Machine` deleted or renamed its instance variable `vm_id`
  - Model `Machine` deleted or renamed its instance variable `vm_uuid`
  - Model `MachineExtensionUpdate` deleted or renamed its instance variable `auto_upgrade_minor_version`
  - Model `MachineExtensionUpdate` deleted or renamed its instance variable `enable_automatic_upgrade`
  - Model `MachineExtensionUpdate` deleted or renamed its instance variable `force_update_tag`
  - Model `MachineExtensionUpdate` deleted or renamed its instance variable `protected_settings`
  - Model `MachineExtensionUpdate` deleted or renamed its instance variable `publisher`
  - Model `MachineExtensionUpdate` deleted or renamed its instance variable `settings`
  - Model `MachineExtensionUpdate` deleted or renamed its instance variable `type`
  - Model `MachineExtensionUpdate` deleted or renamed its instance variable `type_handler_version`
  - Model `MachineUpdate` deleted or renamed its instance variable `agent_upgrade`
  - Model `MachineUpdate` deleted or renamed its instance variable `cloud_metadata`
  - Model `MachineUpdate` deleted or renamed its instance variable `location_data`
  - Model `MachineUpdate` deleted or renamed its instance variable `os_profile`
  - Model `MachineUpdate` deleted or renamed its instance variable `parent_cluster_resource_id`
  - Model `MachineUpdate` deleted or renamed its instance variable `private_link_scope_resource_id`
  - Model `NetworkSecurityPerimeterConfiguration` deleted or renamed its instance variable `network_security_perimeter`
  - Model `NetworkSecurityPerimeterConfiguration` deleted or renamed its instance variable `profile`
  - Model `NetworkSecurityPerimeterConfiguration` deleted or renamed its instance variable `provisioning_issues`
  - Model `NetworkSecurityPerimeterConfiguration` deleted or renamed its instance variable `provisioning_state`
  - Model `NetworkSecurityPerimeterConfiguration` deleted or renamed its instance variable `resource_association`
  - Model `OSProfileLinuxConfiguration` deleted or renamed its instance variable `assessment_mode`
  - Model `OSProfileLinuxConfiguration` deleted or renamed its instance variable `enable_hotpatching`
  - Model `OSProfileLinuxConfiguration` deleted or renamed its instance variable `patch_mode`
  - Model `OSProfileLinuxConfiguration` deleted or renamed its instance variable `status`
  - Model `OSProfileWindowsConfiguration` deleted or renamed its instance variable `assessment_mode`
  - Model `OSProfileWindowsConfiguration` deleted or renamed its instance variable `enable_hotpatching`
  - Model `OSProfileWindowsConfiguration` deleted or renamed its instance variable `patch_mode`
  - Model `OSProfileWindowsConfiguration` deleted or renamed its instance variable `status`
  - Model `ProvisioningIssue` deleted or renamed its instance variable `description`
  - Model `ProvisioningIssue` deleted or renamed its instance variable `issue_type`
  - Model `ProvisioningIssue` deleted or renamed its instance variable `severity`
  - Model `ProvisioningIssue` deleted or renamed its instance variable `suggested_access_rules`
  - Model `ProvisioningIssue` deleted or renamed its instance variable `suggested_resource_ids`
  - Deleted or renamed model `ExtensionValueListResult`
  - Deleted or renamed model `HybridComputePrivateLinkScopeListResult`
  - Deleted or renamed model `Identity`
  - Deleted or renamed model `KeyDetails`
  - Deleted or renamed model `KeyProperties`
  - Deleted or renamed model `LicenseProfilesListResult`
  - Deleted or renamed model `LicensesListResult`
  - Deleted or renamed model `MachineExtensionsListResult`
  - Deleted or renamed model `MachineListResult`
  - Deleted or renamed model `NetworkSecurityPerimeterConfigurationListResult`
  - Deleted or renamed model `OperationListResult`
  - Deleted or renamed model `PrivateEndpointConnectionListResult`
  - Deleted or renamed model `PrivateLinkResourceListResult`
  - Deleted or renamed model `PrivateLinkScopesResource`
  - Deleted or renamed model `ProxyResourceAutoGenerated`
  - Deleted or renamed model `ResourceAutoGenerated`
  - Method `MachineExtensionsOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `MachinesOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `MachinesOperations.list_by_resource_group` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Deleted or renamed method `MachinesOperations.delete`
  - Deleted or renamed model `HybridComputeManagementClientOperationsMixin`

## 9.1.0b5 (2026-07-13)

### Features Added

  - Model `GatewayProperties` added property `gateway_bypass`
  - Model `GatewayUpdateProperties` added property `gateway_bypass`
  - Enum `LicenseTarget` added member `WINDOWS_SERVER2016`
  - Model `MachineProperties` added property `status_reason`
  - Added enum `MachineStatusReason`
  - Added model `ManagedServiceIdentity`
  - Added enum `ManagedServiceIdentityType`
  - Added model `UserAssignedIdentity`

### Breaking Changes

  - Deleted or renamed model `Identity`
  - Deleted or renamed model `ResourceIdentityType`

## 9.1.0b3 (2026-06-03)

### Features Added

  - Client `HybridComputeManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `HybridComputeManagementClient` added method `send_request`
  - Model `HybridComputePrivateLinkScopeProperties` added property `service_extensions`
  - Model `LicenseProfileMachineInstanceView` added property `product_profile`
  - Model `NetworkSecurityPerimeterConfiguration` added property `system_data`
  - Added model `EsuProfileUpdateProperties`
  - Added model `LicenseProfileArmProductProfileProperties`
  - Added model `LicenseProfilePropertiesSoftwareAssurance`
  - Added model `LicenseProfileUpdatePropertiesSoftwareAssurance`
  - Added model `LicenseUpdatePropertiesLicenseDetails`
  - Added model `ProductProfileUpdateProperties`
  - Added enum `ResourceIdentityType`
  - Added model `ServiceExtension`
  - Added enum `ServiceExtensionPublicNetworkAccess`
  - Added model `SettingsGatewayProperties`
  - Operation group `MachinesOperations` added method `create_or_update`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Model `ExtensionValue` moved instance variable `version`, `extension_type` and `publisher` under property `properties`
  - Model `ExtensionValueV2` moved instance variable `version`, `extension_type`, `publisher`, `extension_uris`, `extension_signature_uri`, `operating_system` and `architecture` under property `properties`
  - Model `LicenseProfileMachineInstanceView` moved instance variable `subscription_status`, `product_type`, `enrollment_date`, `billing_start_date`, `disenrollment_date`, `billing_end_date`, `error`, `product_features` and `software_assurance_customer` under property `software_assurance` whose type is `LicenseProfileMachineInstanceViewSoftwareAssurance`
  - Model `OSProfileLinuxConfiguration` moved instance variable `assessment_mode`, `patch_mode`, `enable_hotpatching` and `status` under property `patch_settings` whose type is `PatchSettings`
  - Model `OSProfileWindowsConfiguration` moved instance variable `assessment_mode`, `patch_mode`, `enable_hotpatching` and `status` under property `patch_settings` whose type is `PatchSettings`
  - Method `MachineExtensionsOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `MachineRunCommandsOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `MachinesOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `MachinesOperations.list_by_resource_group` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`

### Other Changes

  - Deleted model `AgentVersion`/`AgentVersionsList`/`ExtensionValueListResultV2`/`HybridIdentityMetadata`/`HybridIdentityMetadataList`/`KeyDetails`/`KeyProperties`/`MachineRunCommandUpdate`/`NetworkConfiguration`/`PrivateLinkScopesResource`/`ProxyResourceAutoGenerated`/`ResourceAutoGenerated` which actually were not used by SDK users
  - Renamed operation group `HybridComputeManagementClientOperationsMixin` to `_HybridComputeManagementClientOperationsMixin`

## 9.1.0b2 (2025-06-16)

### Features Added

  - Client `HybridComputeManagementClient` added method `begin_setup_extensions`
  - Client `HybridComputeManagementClient` added operation group `extension_metadata_v2`
  - Client `HybridComputeManagementClient` added operation group `extension_type`
  - Client `HybridComputeManagementClient` added operation group `extension_publisher`
  - Model `Machine` added property `identity_key_store`
  - Model `Machine` added property `tpm_ek_certificate`
  - Model `Machine` added property `hardware_resource_id`
  - Model `MachineUpdate` added property `identity_key_store`
  - Model `MachineUpdate` added property `tpm_ek_certificate`
  - Enum `StatusTypes` added member `AWAITING_CONNECTION`
  - Model `WindowsParameters` added property `patch_name_masks_to_include`
  - Model `WindowsParameters` added property `patch_name_masks_to_exclude`
  - Added model `ExtensionPublisher`
  - Added model `ExtensionPublisherListResult`
  - Added model `ExtensionType`
  - Added model `ExtensionTypeListResult`
  - Added model `ExtensionValueListResultV2`
  - Added model `ExtensionValueProperties`
  - Added model `ExtensionValueV2`
  - Added model `ExtensionValueV2Properties`
  - Added enum `IdentityKeyStore`
  - Added model `SetupExtensionRequest`
  - Model `HybridComputeManagementClientOperationsMixin` added method `begin_setup_extensions`
  - Model `MachinesOperations` added method `begin_delete`
  - Added operation group `ExtensionMetadataV2Operations`
  - Added operation group `ExtensionPublisherOperations`
  - Added operation group `ExtensionTypeOperations`

### Breaking Changes

  - Deleted or renamed model `ErrorDetailAutoGenerated`
  - Deleted or renamed model `ErrorResponseAutoGenerated`
  - Deleted or renamed model `TrackedResourceAutoGenerated`
  - Deleted or renamed method `MachinesOperations.delete`

## 9.1.0b1 (2024-11-15)

### Features Added

  - Client `HybridComputeManagementClient` added operation group `machine_run_commands`
  - Client `HybridComputeManagementClient` added operation group `gateways`
  - Client `HybridComputeManagementClient` added operation group `settings`
  - Model `Machine` added property `hardware_profile`
  - Model `Machine` added property `storage_profile`
  - Model `Machine` added property `firmware_profile`
  - Model `NetworkInterface` added property `mac_address`
  - Model `NetworkInterface` added property `id`
  - Model `NetworkInterface` added property `name`
  - Added model `AgentVersion`
  - Added model `AgentVersionsList`
  - Added model `Disk`
  - Added model `ErrorDetailAutoGenerated`
  - Added model `ErrorResponseAutoGenerated`
  - Added enum `ExecutionState`
  - Added model `FirmwareProfile`
  - Added model `Gateway`
  - Added enum `GatewayType`
  - Added model `GatewayUpdate`
  - Added model `GatewaysListResult`
  - Added model `HardwareProfile`
  - Added model `HybridIdentityMetadata`
  - Added model `HybridIdentityMetadataList`
  - Added model `MachineRunCommand`
  - Added model `MachineRunCommandInstanceView`
  - Added model `MachineRunCommandScriptSource`
  - Added model `MachineRunCommandUpdate`
  - Added model `MachineRunCommandsListResult`
  - Added model `NetworkConfiguration`
  - Added model `Processor`
  - Added model `RunCommandInputParameter`
  - Added model `RunCommandManagedIdentity`
  - Added model `Settings`
  - Added model `StorageProfile`
  - Added model `TrackedResourceAutoGenerated`
  - Added operation group `GatewaysOperations`
  - Added operation group `MachineRunCommandsOperations`
  - Added operation group `SettingsOperations`

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
