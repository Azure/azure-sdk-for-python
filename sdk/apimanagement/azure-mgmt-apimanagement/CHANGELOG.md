# Release History

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

**Breaking changes**

  - Parameter capacity of model ApiManagementServiceSkuProperties is now required
  - Operation ApiSchemaOperations.create_or_update has a new signature
  - Operation ApiTagDescriptionOperations.get has a new signature
  - Operation ApiTagDescriptionOperations.create_or_update has a new signature
  - Operation ApiTagDescriptionOperations.get_entity_tag has a new signature
  - Operation ApiTagDescriptionOperations.delete has a new signature
  - Operation ApiSchemaOperations.create_or_update has a new signature
  - Model AuthenticationSettingsContract no longer has parameter subscription_key_required
  - Model AuthorizationServerContractBaseProperties no longer has parameter client_secret
  - Model DiagnosticContract no longer has parameter enable_http_correlation_headers
  - Model SchemaContract no longer has parameter document
  - Removed operation group PropertyOperations
  - Removed operation group PolicySnippetOperations

## 0.1.0 (2019-05-01)

  - Initial Release
