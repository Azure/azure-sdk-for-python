# Release History

## 0.3.0 (2021-03-17)

**Features**

  - Model HttpMessageDiagnostic has a new parameter data_masking
  - Model ApiTagResourceContractProperties has a new parameter contact
  - Model ApiTagResourceContractProperties has a new parameter license
  - Model ApiTagResourceContractProperties has a new parameter terms_of_service_url
  - Model ApiManagementServiceUpdateParameters has a new parameter public_ip_address_id
  - Model ApiManagementServiceUpdateParameters has a new parameter restore
  - Model CertificateContract has a new parameter key_vault
  - Model ApiManagementServiceResource has a new parameter zones
  - Model ApiManagementServiceResource has a new parameter public_ip_address_id
  - Model ApiManagementServiceResource has a new parameter restore
  - Model NamedValueContract has a new parameter key_vault
  - Model CacheUpdateParameters has a new parameter use_from_location
  - Model ParameterContract has a new parameter schema_id
  - Model ParameterContract has a new parameter type_name
  - Model RecipientUserCollection has a new parameter count
  - Model ApiContractProperties has a new parameter contact
  - Model ApiContractProperties has a new parameter license
  - Model ApiContractProperties has a new parameter terms_of_service_url
  - Model HostnameConfiguration has a new parameter certificate_status
  - Model HostnameConfiguration has a new parameter identity_client_id
  - Model HostnameConfiguration has a new parameter certificate_source
  - Model ApiContract has a new parameter contact
  - Model ApiContract has a new parameter license
  - Model ApiContract has a new parameter terms_of_service_url
  - Model ApiManagementServiceBaseProperties has a new parameter public_ip_address_id
  - Model ApiManagementServiceBaseProperties has a new parameter restore
  - Model PolicyCollection has a new parameter count
  - Model BackendServiceFabricClusterProperties has a new parameter client_certificate_id
  - Model NamedValueUpdateParameters has a new parameter key_vault
  - Model AdditionalLocation has a new parameter zones
  - Model AdditionalLocation has a new parameter public_ip_address_id
  - Model RecipientEmailCollection has a new parameter count
  - Model DiagnosticContract has a new parameter operation_name_format
  - Model ApiEntityBaseContract has a new parameter contact
  - Model ApiEntityBaseContract has a new parameter license
  - Model ApiEntityBaseContract has a new parameter terms_of_service_url
  - Model GatewayHostnameConfigurationContract has a new parameter tls10_enabled
  - Model GatewayHostnameConfigurationContract has a new parameter tls11_enabled
  - Model GatewayHostnameConfigurationContract has a new parameter http2_enabled
  - Model ApiUpdateContract has a new parameter contact
  - Model ApiUpdateContract has a new parameter license
  - Model ApiUpdateContract has a new parameter terms_of_service_url
  - Model NamedValueCreateContract has a new parameter key_vault
  - Model BackendCredentialsContract has a new parameter certificate_ids
  - Model ApiCreateOrUpdateParameter has a new parameter contact
  - Model ApiCreateOrUpdateParameter has a new parameter license
  - Model ApiCreateOrUpdateParameter has a new parameter terms_of_service_url
  - Added operation TenantAccessOperations.list_by_service
  - Added operation TenantAccessOperations.create
  - Added operation CertificateOperations.refresh_secret
  - Added operation UserSubscriptionOperations.get
  - Added operation ApiManagementServiceOperations.get_domain_ownership_identifier
  - Added operation NamedValueOperations.refresh_secret
  - Added operation group ApiManagementSkusOperations
  - Added operation group DeletedServicesOperations
  - Added operation group PortalSettingsOperations
  - Added operation group TenantSettingsOperations
  - Added operation group PortalRevisionOperations
  - Added operation group ContentItemOperations
  - Added operation group GatewayCertificateAuthorityOperations
  - Added operation group ContentTypeOperations

**Breaking changes**

  - Operation CertificateOperations.create_or_update has a new signature
  - Operation CertificateOperations.list_by_service has a new signature
  - Operation EmailTemplateOperations.update has a new signature
  - Operation GatewayHostnameConfigurationOperations.create_or_update has a new signature
  - Operation GatewayHostnameConfigurationOperations.delete has a new signature
  - Operation NamedValueOperations.list_by_service has a new signature
  - Operation SubscriptionOperations.create_or_update has a new signature
  - Operation SubscriptionOperations.update has a new signature
  - Operation TenantAccessGitOperations.regenerate_primary_key has a new signature
  - Operation TenantAccessGitOperations.regenerate_secondary_key has a new signature
  - Operation TenantAccessOperations.get has a new signature
  - Operation TenantAccessOperations.get_entity_tag has a new signature
  - Operation TenantAccessOperations.list_secrets has a new signature
  - Operation TenantAccessOperations.regenerate_primary_key has a new signature
  - Operation TenantAccessOperations.regenerate_secondary_key has a new signature
  - Operation UserConfirmationPasswordOperations.send has a new signature
  - Operation UserOperations.delete has a new signature
  - Operation LoggerOperations.delete has a new signature
  - Operation EmailTemplateOperations.update has a new signature
  - Operation CertificateOperations.create_or_update has a new signature
  - Operation GatewayApiOperations.list_by_service has a new signature
  - Operation GatewayHostnameConfigurationOperations.list_by_service has a new signature
  - Operation GatewayOperations.list_by_service has a new signature
  - Operation TenantAccessOperations.update has a new signature
  - Operation UserOperations.create_or_update has a new signature
  - Model ConnectivityStatusContract has a new required parameter is_optional
  - Model ConnectivityStatusContract has a new required parameter resource_type
  - Model CacheContract has a new required parameter use_from_location
  - Removed operation TenantAccessGitOperations.list_secrets
  - Removed operation TenantAccessGitOperations.get
  - Model CertificateCreateOrUpdateParameters has a new signature
  - Model AccessInformationContract has a new signature

## 0.2.0 (2020-03-25)

**Features**

  - Model IdentityProviderUpdateParameters has a new parameter signin_tenant
  - Model ApiManagementServiceIdentity has a new parameter user_assigned_identities
  - Model AdditionalLocation has a new parameter disable_gateway
  - Model UserCreateParameters has a new parameter app_type
  - Model ApiManagementServiceResource has a new parameter disable_gateway
  - Model ApiManagementServiceResource has a new parameter developer_portal_url
  - Model ApiManagementServiceResource has a new parameter api_version_constraint
  - Model DiagnosticContract has a new parameter log_client_ip
  - Model DiagnosticContract has a new parameter verbosity
  - Model DiagnosticContract has a new parameter http_correlation_protocol
  - Model SchemaContract has a new parameter value
  - Model SchemaContract has a new parameter definitions
  - Model ApiManagementServiceUpdateParameters has a new parameter disable_gateway
  - Model ApiManagementServiceUpdateParameters has a new parameter developer_portal_url
  - Model ApiManagementServiceUpdateParameters has a new parameter api_version_constraint
  - Model TagDescriptionContract has a new parameter tag_id
  - Model ApiManagementServiceBaseProperties has a new parameter disable_gateway
  - Model ApiManagementServiceBaseProperties has a new parameter developer_portal_url
  - Model ApiManagementServiceBaseProperties has a new parameter api_version_constraint
  - Model IdentityProviderBaseParameters has a new parameter signin_tenant
  - Model IdentityProviderContract has a new parameter signin_tenant
  - Added operation TenantAccessGitOperations.list_secrets
  - Added operation DelegationSettingsOperations.list_secrets
  - Added operation AuthorizationServerOperations.list_secrets
  - Added operation TenantAccessOperations.list_secrets
  - Added operation SubscriptionOperations.list_secrets
  - Added operation IdentityProviderOperations.list_secrets
  - Added operation OpenIdConnectProviderOperations.list_secrets
  - Added operation group GatewayApiOperations
  - Added operation group PolicyDescriptionOperations
  - Added operation group GatewayHostnameConfigurationOperations
  - Added operation group NamedValueOperations
  - Added operation group GatewayOperations

**General breaking changes**

This version uses a next-generation code generator that *might* introduce breaking changes if from some import. In summary, some modules were incorrectly visible/importable and have been renamed. This fixed several issues caused by usage of classes that were not supposed to be used in the first place.
  
  - ApiManagementClient cannot be imported from `azure.mgmt.apimanagement.api_management_client` anymore (import from `azure.mgmt.apimanagement` works like before)
  - ApiManagementClientConfiguration import has been moved from `azure.mgmt.apimanagement.api_management_client` to `azure.mgmt.apimanagement`
  - A model `MyClass` from a "models" sub-module cannot be imported anymore using `azure.mgmt.apimanagement.models.my_class` (import from `azure.mgmt.apimanagement.models` works like before)
  - An operation class `MyClassOperations` from an `operations` sub-module cannot be imported anymore using `azure.mgmt.apimanagement.operations.my_class_operations` (import from `azure.mgmt.apimanagement.operations` works like before)
  
Last but not least, HTTP connection pooling is now enabled by default. You should always use a client as a context manager, or call close(), or use no more than one client per process.

## 0.1.0 (2019-05-01)

  - Initial Release
