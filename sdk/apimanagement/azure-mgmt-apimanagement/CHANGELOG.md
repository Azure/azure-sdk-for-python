# Release History

## 3.0.0 (2022-01-13)

**Features**

  - Added operation group ApiManagementClientOperationsMixin
  - Added operation group GlobalSchemaOperations
  - Added operation group OutboundNetworkDependenciesEndpointsOperations
  - Added operation group PrivateEndpointConnectionOperations
  - Model AdditionalLocation has a new parameter platform_version
  - Model AdditionalLocation has a new parameter public_ip_address_id
  - Model ApiContract has a new parameter contact
  - Model ApiContract has a new parameter license
  - Model ApiContract has a new parameter terms_of_service_url
  - Model ApiContractProperties has a new parameter contact
  - Model ApiContractProperties has a new parameter license
  - Model ApiContractProperties has a new parameter terms_of_service_url
  - Model ApiContractUpdateProperties has a new parameter contact
  - Model ApiContractUpdateProperties has a new parameter license
  - Model ApiContractUpdateProperties has a new parameter terms_of_service_url
  - Model ApiCreateOrUpdateParameter has a new parameter contact
  - Model ApiCreateOrUpdateParameter has a new parameter license
  - Model ApiCreateOrUpdateParameter has a new parameter terms_of_service_url
  - Model ApiCreateOrUpdateProperties has a new parameter contact
  - Model ApiCreateOrUpdateProperties has a new parameter license
  - Model ApiCreateOrUpdateProperties has a new parameter terms_of_service_url
  - Model ApiEntityBaseContract has a new parameter contact
  - Model ApiEntityBaseContract has a new parameter license
  - Model ApiEntityBaseContract has a new parameter terms_of_service_url
  - Model ApiManagementServiceBackupRestoreParameters has a new parameter access_type
  - Model ApiManagementServiceBackupRestoreParameters has a new parameter client_id
  - Model ApiManagementServiceBaseProperties has a new parameter platform_version
  - Model ApiManagementServiceBaseProperties has a new parameter private_endpoint_connections
  - Model ApiManagementServiceBaseProperties has a new parameter public_ip_address_id
  - Model ApiManagementServiceBaseProperties has a new parameter public_network_access
  - Model ApiManagementServiceProperties has a new parameter platform_version
  - Model ApiManagementServiceProperties has a new parameter private_endpoint_connections
  - Model ApiManagementServiceProperties has a new parameter public_ip_address_id
  - Model ApiManagementServiceProperties has a new parameter public_network_access
  - Model ApiManagementServiceResource has a new parameter platform_version
  - Model ApiManagementServiceResource has a new parameter private_endpoint_connections
  - Model ApiManagementServiceResource has a new parameter public_ip_address_id
  - Model ApiManagementServiceResource has a new parameter public_network_access
  - Model ApiManagementServiceResource has a new parameter system_data
  - Model ApiManagementServiceUpdateParameters has a new parameter platform_version
  - Model ApiManagementServiceUpdateParameters has a new parameter private_endpoint_connections
  - Model ApiManagementServiceUpdateParameters has a new parameter public_ip_address_id
  - Model ApiManagementServiceUpdateParameters has a new parameter public_network_access
  - Model ApiManagementServiceUpdateParameters has a new parameter zones
  - Model ApiManagementServiceUpdateProperties has a new parameter platform_version
  - Model ApiManagementServiceUpdateProperties has a new parameter private_endpoint_connections
  - Model ApiManagementServiceUpdateProperties has a new parameter public_ip_address_id
  - Model ApiManagementServiceUpdateProperties has a new parameter public_network_access
  - Model ApiTagResourceContractProperties has a new parameter contact
  - Model ApiTagResourceContractProperties has a new parameter license
  - Model ApiTagResourceContractProperties has a new parameter terms_of_service_url
  - Model ApiUpdateContract has a new parameter contact
  - Model ApiUpdateContract has a new parameter license
  - Model ApiUpdateContract has a new parameter terms_of_service_url
  - Model HostnameConfiguration has a new parameter certificate_source
  - Model HostnameConfiguration has a new parameter certificate_status
  - Model ParameterContract has a new parameter examples
  - Model ParameterContract has a new parameter schema_id
  - Model ParameterContract has a new parameter type_name
  - Model RepresentationContract has a new parameter examples
  - Model SchemaContract has a new parameter components
  - Model TenantConfigurationSyncStateContract has a new parameter id
  - Model TenantConfigurationSyncStateContract has a new parameter name
  - Model TenantConfigurationSyncStateContract has a new parameter type

**Breaking changes**

  - Model RepresentationContract no longer has parameter sample

## 2.1.0 (2021-08-03)

**Features**

  - Model OperationResultContract has a new parameter id_properties_id
  - Model OperationResultContract has a new parameter name
  - Model OperationResultContract has a new parameter type
  - Model TenantConfigurationSyncStateContract has a new parameter last_operation_id

## 2.0.0 (2021-03-25)

**Features**

  - Model TagCollection has a new parameter count
  - Model OpenIdConnectProviderCollection has a new parameter count
  - Model TagResourceCollection has a new parameter count
  - Model CertificateCollection has a new parameter count
  - Model PolicyCollection has a new parameter count
  - Model IssueAttachmentCollection has a new parameter count
  - Model BackendServiceFabricClusterProperties has a new parameter client_certificate_id
  - Model BackendCollection has a new parameter count
  - Model SubscriptionCollection has a new parameter count
  - Model RecipientEmailCollection has a new parameter count
  - Model GatewayCollection has a new parameter count
  - Model IssueCommentCollection has a new parameter count
  - Model OperationCollection has a new parameter count
  - Model DiagnosticCollection has a new parameter count
  - Model ApiVersionSetCollection has a new parameter count
  - Model ProductCollection has a new parameter count
  - Model IssueCollection has a new parameter count
  - Model NotificationCollection has a new parameter count
  - Model UserCollection has a new parameter count
  - Model IdentityProviderList has a new parameter count
  - Model ApiReleaseCollection has a new parameter count
  - Model TagDescriptionCollection has a new parameter count
  - Model ApiRevisionCollection has a new parameter count
  - Model CacheCollection has a new parameter count
  - Model RecipientUserCollection has a new parameter count
  - Model NamedValueCollection has a new parameter count
  - Model EmailTemplateCollection has a new parameter count
  - Model BackendCredentialsContract has a new parameter certificate_ids
  - Model ApiCollection has a new parameter count
  - Model GroupCollection has a new parameter count
  - Model SchemaCollection has a new parameter count
  - Added operation TenantAccessOperations.list_by_service
  - Added operation TenantAccessOperations.create
  - Added operation ApiManagementServiceOperations.get_domain_ownership_identifier
  - Added operation NamedValueOperations.begin_refresh_secret
  - Added operation CertificateOperations.refresh_secret
  - Added operation DeletedServicesOperations.begin_purge
  - Added operation UserSubscriptionOperations.get
  - Added operation group PortalSettingsOperations
  - Added operation group TenantSettingsOperations
  - Added operation group GatewayCertificateAuthorityOperations
  - Added operation group ApiManagementSkusOperations

**Breaking changes**

  - Operation CertificateOperations.list_by_service has a new signature
  - Operation NamedValueOperations.list_by_service has a new signature
  - Removed operation DeletedServicesOperations.purge
  - Removed operation TenantAccessGitOperations.list_secrets
  - Removed operation TenantAccessGitOperations.get
  - Model AccessInformationContract has a new signature

## 1.0.0 (2020-12-21)

**Features**

  - Added operation group ContentItemOperations
  - Added operation group PortalRevisionOperations

**Breaking changes**

  - Operation SignUpSettingsOperations.update has a new signature
  - Operation TenantAccessOperations.update has a new signature
  - Operation UserOperations.get_shared_access_token has a new signature
  - Operation SignInSettingsOperations.update has a new signature
  - Operation QuotaByPeriodKeysOperations.update has a new signature
  - Operation TenantConfigurationOperations.begin_save has a new signature
  - Operation TenantConfigurationOperations.begin_validate has a new signature
  - Operation TenantConfigurationOperations.begin_deploy has a new signature
  - Operation BackendOperations.reconnect has a new signature
  - Operation QuotaByCounterKeysOperations.update has a new signature
  - Operation ApiReleaseOperations.update has a new signature
  - Operation TagOperations.update has a new signature
  - Operation ApiManagementServiceOperations.check_name_availability has a new signature
  - Operation ApiManagementServiceOperations.begin_apply_network_configuration_updates has a new signature
  - Operation GatewayOperations.update has a new signature
  - Operation GatewayOperations.generate_token has a new signature
  - Operation GatewayOperations.regenerate_key has a new signature
  - Operation UserOperations.get_shared_access_token has a new signature
  - Operation TenantConfigurationOperations.begin_validate has a new signature
  - Operation TenantConfigurationOperations.begin_save has a new signature
  - Operation TenantConfigurationOperations.begin_deploy has a new signature
  - Operation TagOperations.create_or_update has a new signature
  - Operation SignUpSettingsOperations.update has a new signature
  - Operation QuotaByPeriodKeysOperations.update has a new signature
  - Operation QuotaByCounterKeysOperations.update has a new signature
  - Operation GatewayOperations.update has a new signature
  - Operation GatewayOperations.generate_token has a new signature
  - Operation ApiReleaseOperations.update has a new signature
  - Operation GatewayApiOperations.create_or_update has a new signature
  - Operation TagOperations.create_or_update has a new signature
  - Operation SignUpSettingsOperations.create_or_update has a new signature
  - Operation SignInSettingsOperations.create_or_update has a new signature
  - Operation ApiOperationPolicyOperations.create_or_update has a new signature
  - Operation PolicyOperations.create_or_update has a new signature
  - Operation ApiPolicyOperations.create_or_update has a new signature
  - Operation ApiReleaseOperations.create_or_update has a new signature
  - Operation GatewayOperations.create_or_update has a new signature
  - Operation ProductPolicyOperations.create_or_update has a new signature
  - Removed operation group ContentTypeContentItemOperations

## 1.0.0b1 (2020-10-31)

This is beta preview version.
For detailed changelog please refer to equivalent stable version 0.2.0(https://pypi.org/project/azure-mgmt-apimanagement/0.2.0/)

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
  - For a complete set of supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core-tracing-opentelemetry) for an overview.

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
