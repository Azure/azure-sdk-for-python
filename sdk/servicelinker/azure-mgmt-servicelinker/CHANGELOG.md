# Release History

## 1.2.0b3 (2024-10-11)

### Features Added

  - Enum `AzureResourceType` added member `APP_CONFIG`
  - Enum `TargetServiceType` added member `FABRIC_PLATFORM`
  - Added model `AzureAppConfigProperties`
  - Added model `FabricPlatform`

## 1.2.0b2 (2024-03-19)

### Features Added

  - Added operation LinkersOperations.list_dapr_configurations
  - Model AccessKeyInfoBase has a new parameter auth_mode
  - Model AuthInfoBase has a new parameter auth_mode
  - Model ConfigurationInfo has a new parameter additional_connection_string_properties
  - Model ConfigurationInfo has a new parameter configuration_store
  - Model ConfigurationInfo has a new parameter dapr_properties
  - Model ConfigurationName has a new parameter required
  - Model ConfigurationNameItem has a new parameter dapr_properties
  - Model ConfigurationNameItem has a new parameter secret_type
  - Model SecretAuthInfo has a new parameter auth_mode
  - Model ServicePrincipalCertificateAuthInfo has a new parameter auth_mode
  - Model ServicePrincipalSecretAuthInfo has a new parameter auth_mode
  - Model SourceConfiguration has a new parameter config_type
  - Model SourceConfiguration has a new parameter description
  - Model SourceConfiguration has a new parameter key_vault_reference_identity
  - Model SystemAssignedIdentityAuthInfo has a new parameter auth_mode
  - Model UserAccountAuthInfo has a new parameter auth_mode
  - Model UserAssignedIdentityAuthInfo has a new parameter auth_mode

## 1.2.0b1 (2022-12-02)

### Features Added

  - Added operation group ConfigurationNamesOperations
  - Added operation group ConnectorOperations
  - Added operation group LinkersOperations
  - Model LinkerPatch has a new parameter configuration_info
  - Model LinkerPatch has a new parameter public_network_solution
  - Model LinkerResource has a new parameter configuration_info
  - Model LinkerResource has a new parameter public_network_solution
  - Model ProxyResource has a new parameter system_data
  - Model Resource has a new parameter system_data
  - Model SecretStore has a new parameter key_vault_secret_name
  - Model ServicePrincipalCertificateAuthInfo has a new parameter delete_or_update_behavior
  - Model ServicePrincipalCertificateAuthInfo has a new parameter roles
  - Model ServicePrincipalSecretAuthInfo has a new parameter delete_or_update_behavior
  - Model ServicePrincipalSecretAuthInfo has a new parameter roles
  - Model ServicePrincipalSecretAuthInfo has a new parameter user_name
  - Model SystemAssignedIdentityAuthInfo has a new parameter delete_or_update_behavior
  - Model SystemAssignedIdentityAuthInfo has a new parameter roles
  - Model SystemAssignedIdentityAuthInfo has a new parameter user_name
  - Model UserAssignedIdentityAuthInfo has a new parameter delete_or_update_behavior
  - Model UserAssignedIdentityAuthInfo has a new parameter roles
  - Model UserAssignedIdentityAuthInfo has a new parameter user_name
  - Model VNetSolution has a new parameter delete_or_update_behavior

## 1.1.0 (2022-05-16)

**Features**

  - Added model AzureResourceType
  - Added model TargetServiceType
  - Added model ValidateOperationResult

## 1.0.0 (2022-04-22)

**Features**

  - Model LinkerPatch has a new parameter scope
  - Model LinkerPatch has a new parameter target_service
  - Model LinkerResource has a new parameter scope
  - Model LinkerResource has a new parameter target_service
  - Model SecretAuthInfo has a new parameter secret_info
  - Model ValidateResult has a new parameter is_connection_available
  - Model ValidateResult has a new parameter linker_name
  - Model ValidateResult has a new parameter source_id
  - Model ValidateResult has a new parameter validation_detail

**Breaking changes**

  - Model LinkerPatch no longer has parameter target_id
  - Model LinkerResource no longer has parameter target_id
  - Model SecretAuthInfo no longer has parameter secret
  - Model ValidateResult no longer has parameter linker_status
  - Model ValidateResult no longer has parameter name
  - Model ValidateResult no longer has parameter reason

## 1.0.0b2 (2022-02-24)

**Features**

  - Model LinkerPatch has a new parameter secret_store
  - Model LinkerPatch has a new parameter v_net_solution
  - Model LinkerResource has a new parameter secret_store
  - Model LinkerResource has a new parameter v_net_solution

## 1.0.0b1 (2021-09-28)

* Initial Release
