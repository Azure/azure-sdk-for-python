# Release History

## 7.1.0 (2023-04-20)

### Features Added

  - Added operation StaticSitesOperations.create_or_update_basic_auth
  - Added operation StaticSitesOperations.create_or_update_build_database_connection
  - Added operation StaticSitesOperations.create_or_update_database_connection
  - Added operation StaticSitesOperations.delete_build_database_connection
  - Added operation StaticSitesOperations.delete_database_connection
  - Added operation StaticSitesOperations.get_basic_auth
  - Added operation StaticSitesOperations.get_build_database_connection
  - Added operation StaticSitesOperations.get_build_database_connection_with_details
  - Added operation StaticSitesOperations.get_build_database_connections
  - Added operation StaticSitesOperations.get_build_database_connections_with_details
  - Added operation StaticSitesOperations.get_database_connection
  - Added operation StaticSitesOperations.get_database_connection_with_details
  - Added operation StaticSitesOperations.get_database_connections
  - Added operation StaticSitesOperations.get_database_connections_with_details
  - Added operation StaticSitesOperations.list_basic_auth
  - Added operation StaticSitesOperations.update_build_database_connection
  - Added operation StaticSitesOperations.update_database_connection
  - Added operation WebAppsOperations.deploy_workflow_artifacts
  - Added operation WebAppsOperations.deploy_workflow_artifacts_slot
  - Added operation WebAppsOperations.get_instance_workflow_slot
  - Added operation WebAppsOperations.get_workflow
  - Added operation WebAppsOperations.list_instance_workflows_slot
  - Added operation WebAppsOperations.list_workflows
  - Added operation WebAppsOperations.list_workflows_connections
  - Added operation WebAppsOperations.list_workflows_connections_slot
  - Model Site has a new parameter managed_environment_id
  - Model SiteConfig has a new parameter elastic_web_app_scale_limit
  - Model SiteConfig has a new parameter ip_security_restrictions_default_action
  - Model SiteConfig has a new parameter metadata
  - Model SiteConfig has a new parameter scm_ip_security_restrictions_default_action
  - Model SiteConfigResource has a new parameter elastic_web_app_scale_limit
  - Model SiteConfigResource has a new parameter ip_security_restrictions_default_action
  - Model SiteConfigResource has a new parameter metadata
  - Model SiteConfigResource has a new parameter scm_ip_security_restrictions_default_action
  - Model StaticSiteARMResource has a new parameter database_connections
  - Model StaticSiteBuildARMResource has a new parameter database_connections
  - Model StaticSitePatchResource has a new parameter database_connections

## 7.0.0 (2022-07-04)

**Features**

  - Added operation AppServiceEnvironmentsOperations.begin_upgrade
  - Added operation AppServiceEnvironmentsOperations.delete_ase_custom_dns_suffix_configuration
  - Added operation AppServiceEnvironmentsOperations.get_ase_custom_dns_suffix_configuration
  - Added operation AppServiceEnvironmentsOperations.test_upgrade_available_notification
  - Added operation AppServiceEnvironmentsOperations.update_ase_custom_dns_suffix_configuration
  - Added operation StaticSitesOperations.begin_link_backend
  - Added operation StaticSitesOperations.begin_link_backend_to_build
  - Added operation StaticSitesOperations.begin_validate_backend
  - Added operation StaticSitesOperations.begin_validate_backend_for_build
  - Added operation StaticSitesOperations.get_linked_backend
  - Added operation StaticSitesOperations.get_linked_backend_for_build
  - Added operation StaticSitesOperations.get_linked_backends
  - Added operation StaticSitesOperations.get_linked_backends_for_build
  - Added operation StaticSitesOperations.unlink_backend
  - Added operation StaticSitesOperations.unlink_backend_from_build
  - Added operation WebAppsOperations.begin_get_production_site_deployment_status
  - Added operation WebAppsOperations.begin_get_slot_site_deployment_status_slot
  - Added operation WebAppsOperations.get_auth_settings_v2_without_secrets_slot
  - Added operation WebAppsOperations.list_production_site_deployment_statuses
  - Added operation WebAppsOperations.list_slot_site_deployment_statuses_slot
  - Added operation group WorkflowRunActionRepetitionsOperations
  - Added operation group WorkflowRunActionRepetitionsRequestHistoriesOperations
  - Added operation group WorkflowRunActionScopeRepetitionsOperations
  - Added operation group WorkflowRunActionsOperations
  - Added operation group WorkflowRunsOperations
  - Added operation group WorkflowTriggerHistoriesOperations
  - Added operation group WorkflowTriggersOperations
  - Added operation group WorkflowVersionsOperations
  - Added operation group WorkflowsOperations
  - Model AppServiceEnvironment has a new parameter custom_dns_suffix_configuration
  - Model AppServiceEnvironment has a new parameter networking_configuration
  - Model AppServiceEnvironment has a new parameter upgrade_availability
  - Model AppServiceEnvironment has a new parameter upgrade_preference
  - Model AppServiceEnvironmentPatchResource has a new parameter custom_dns_suffix_configuration
  - Model AppServiceEnvironmentPatchResource has a new parameter networking_configuration
  - Model AppServiceEnvironmentPatchResource has a new parameter upgrade_availability
  - Model AppServiceEnvironmentPatchResource has a new parameter upgrade_preference
  - Model AppServiceEnvironmentResource has a new parameter custom_dns_suffix_configuration
  - Model AppServiceEnvironmentResource has a new parameter networking_configuration
  - Model AppServiceEnvironmentResource has a new parameter upgrade_availability
  - Model AppServiceEnvironmentResource has a new parameter upgrade_preference
  - Model AppServicePlan has a new parameter number_of_workers
  - Model AppServicePlanPatchResource has a new parameter number_of_workers
  - Model AseV3NetworkingConfiguration has a new parameter ftp_enabled
  - Model AseV3NetworkingConfiguration has a new parameter inbound_ip_address_override
  - Model AseV3NetworkingConfiguration has a new parameter remote_debug_enabled
  - Model ErrorResponse has a new parameter error
  - Model Site has a new parameter public_network_access
  - Model Site has a new parameter vnet_content_share_enabled
  - Model Site has a new parameter vnet_image_pull_enabled
  - Model Site has a new parameter vnet_route_all_enabled
  - Model StaticSiteARMResource has a new parameter linked_backends
  - Model StaticSiteARMResource has a new parameter public_network_access
  - Model StaticSiteBuildARMResource has a new parameter linked_backends
  - Model StaticSitePatchResource has a new parameter linked_backends
  - Model StaticSitePatchResource has a new parameter public_network_access
  - Model TriggeredWebJob has a new parameter public_network_access
  - Model TriggeredWebJob has a new parameter storage_account_required

**Breaking changes**

  - Model CertificateEmail no longer has parameter id
  - Model CertificateEmail no longer has parameter kind
  - Model CertificateEmail no longer has parameter name
  - Model CertificateEmail no longer has parameter type
  - Model CertificateOrderAction no longer has parameter id
  - Model CertificateOrderAction no longer has parameter kind
  - Model CertificateOrderAction no longer has parameter name
  - Model CertificateOrderAction no longer has parameter type
  - Model ErrorResponse no longer has parameter code
  - Model ErrorResponse no longer has parameter message
  - Operation WebSiteManagementClientOperationsMixin.list_custom_host_name_sites has a new parameter hostname

## 6.1.0 (2022-01-24)

**Features**

  - Added operation WebAppsOperations.create_one_deploy_operation
  - Added operation WebAppsOperations.get_one_deploy_status

## 6.0.0 (2022-01-10)

**Features**

  - Added operation DomainsOperations.transfer_out
  - Added operation WebAppsOperations.get_auth_settings_v2_without_secrets
  - Added operation WebSiteManagementClientOperationsMixin.list_custom_host_name_sites
  - Added operation group ContainerAppsOperations
  - Added operation group ContainerAppsRevisionsOperations
  - Model KubeEnvironment has a new parameter container_apps_configuration
  - Model KubeEnvironment has a new parameter environment_type
  - Model KubeEnvironmentPatchResource has a new parameter container_apps_configuration
  - Model StaticSiteARMResource has a new parameter enterprise_grade_cdn_status
  - Model StaticSitePatchResource has a new parameter enterprise_grade_cdn_status

**Breaking changes**

  - Removed operation WebSiteManagementClientOperationsMixin.generate_github_access_token_for_appservice_cli_async

## 5.0.0 (2021-09-08)

**Features**

  - Model AppServicePlan has a new parameter zone_redundant
  - Model AppServicePlanPatchResource has a new parameter zone_redundant
  - Model AppServiceEnvironmentPatchResource has a new parameter zone_redundant
  - Model AppServiceEnvironmentResource has a new parameter zone_redundant
  - Model AzureActiveDirectoryRegistration has a new parameter client_secret_certificate_issuer
  - Model AzureActiveDirectoryRegistration has a new parameter client_secret_certificate_subject_alternative_name
  - Model AseV3NetworkingConfiguration has a new parameter external_inbound_ip_addresses
  - Model AseV3NetworkingConfiguration has a new parameter internal_inbound_ip_addresses
  - Model AppServiceEnvironment has a new parameter zone_redundant
  - Model ErrorEntity has a new parameter target
  - Model ErrorEntity has a new parameter details

**Breaking changes**

  - Model TokenStore no longer has parameter kind
  - Model TokenStore no longer has parameter id
  - Model TokenStore no longer has parameter name
  - Model TokenStore no longer has parameter type
  - Model IdentityProviders no longer has parameter kind
  - Model IdentityProviders no longer has parameter id
  - Model IdentityProviders no longer has parameter name
  - Model IdentityProviders no longer has parameter type
  - Model Google no longer has parameter kind
  - Model Google no longer has parameter id
  - Model Google no longer has parameter name
  - Model Google no longer has parameter type
  - Model Nonce no longer has parameter kind
  - Model Nonce no longer has parameter id
  - Model Nonce no longer has parameter name
  - Model Nonce no longer has parameter type
  - Model AppleRegistration no longer has parameter kind
  - Model AppleRegistration no longer has parameter id
  - Model AppleRegistration no longer has parameter name
  - Model AppleRegistration no longer has parameter type
  - Model ForwardProxy no longer has parameter kind
  - Model ForwardProxy no longer has parameter id
  - Model ForwardProxy no longer has parameter name
  - Model ForwardProxy no longer has parameter type
  - Model OpenIdConnectLogin no longer has parameter kind
  - Model OpenIdConnectLogin no longer has parameter id
  - Model OpenIdConnectLogin no longer has parameter name
  - Model OpenIdConnectLogin no longer has parameter type
  - Model AzureActiveDirectoryRegistration no longer has parameter kind
  - Model AzureActiveDirectoryRegistration no longer has parameter id
  - Model AzureActiveDirectoryRegistration no longer has parameter name
  - Model AzureActiveDirectoryRegistration no longer has parameter type
  - Model AzureActiveDirectoryLogin no longer has parameter kind
  - Model AzureActiveDirectoryLogin no longer has parameter id
  - Model AzureActiveDirectoryLogin no longer has parameter name
  - Model AzureActiveDirectoryLogin no longer has parameter type
  - Model TriggeredJobRun no longer has parameter kind
  - Model TriggeredJobRun no longer has parameter id
  - Model TriggeredJobRun no longer has parameter name
  - Model TriggeredJobRun no longer has parameter type
  - Model AppRegistration no longer has parameter kind
  - Model AppRegistration no longer has parameter id
  - Model AppRegistration no longer has parameter name
  - Model AppRegistration no longer has parameter type
  - Model VnetInfo no longer has parameter kind
  - Model VnetInfo no longer has parameter id
  - Model VnetInfo no longer has parameter name
  - Model VnetInfo no longer has parameter type
  - Model CustomOpenIdConnectProvider no longer has parameter kind
  - Model CustomOpenIdConnectProvider no longer has parameter id
  - Model CustomOpenIdConnectProvider no longer has parameter name
  - Model CustomOpenIdConnectProvider no longer has parameter type
  - Model TwitterRegistration no longer has parameter kind
  - Model TwitterRegistration no longer has parameter id
  - Model TwitterRegistration no longer has parameter name
  - Model TwitterRegistration no longer has parameter type
  - Model OpenIdConnectConfig no longer has parameter kind
  - Model OpenIdConnectConfig no longer has parameter id
  - Model OpenIdConnectConfig no longer has parameter name
  - Model OpenIdConnectConfig no longer has parameter type
  - Model AzureStaticWebApps no longer has parameter kind
  - Model AzureStaticWebApps no longer has parameter id
  - Model AzureStaticWebApps no longer has parameter name
  - Model AzureStaticWebApps no longer has parameter type
  - Model LegacyMicrosoftAccount no longer has parameter kind
  - Model LegacyMicrosoftAccount no longer has parameter id
  - Model LegacyMicrosoftAccount no longer has parameter name
  - Model LegacyMicrosoftAccount no longer has parameter type
  - Model AzureActiveDirectory no longer has parameter kind
  - Model AzureActiveDirectory no longer has parameter id
  - Model AzureActiveDirectory no longer has parameter name
  - Model AzureActiveDirectory no longer has parameter type
  - Model GitHub no longer has parameter kind
  - Model GitHub no longer has parameter id
  - Model GitHub no longer has parameter name
  - Model GitHub no longer has parameter type
  - Model HttpSettings no longer has parameter kind
  - Model HttpSettings no longer has parameter id
  - Model HttpSettings no longer has parameter name
  - Model HttpSettings no longer has parameter type
  - Model DetectorDefinition no longer has parameter kind
  - Model DetectorDefinition no longer has parameter id
  - Model DetectorDefinition no longer has parameter name
  - Model DetectorDefinition no longer has parameter type
  - Model Twitter no longer has parameter kind
  - Model Twitter no longer has parameter id
  - Model Twitter no longer has parameter name
  - Model Twitter no longer has parameter type
  - Model JwtClaimChecks no longer has parameter kind
  - Model JwtClaimChecks no longer has parameter id
  - Model JwtClaimChecks no longer has parameter name
  - Model JwtClaimChecks no longer has parameter type
  - Model CookieExpiration no longer has parameter kind
  - Model CookieExpiration no longer has parameter id
  - Model CookieExpiration no longer has parameter name
  - Model CookieExpiration no longer has parameter type
  - Model Apple no longer has parameter kind
  - Model Apple no longer has parameter id
  - Model Apple no longer has parameter name
  - Model Apple no longer has parameter type
  - Model OpenIdConnectRegistration no longer has parameter kind
  - Model OpenIdConnectRegistration no longer has parameter id
  - Model OpenIdConnectRegistration no longer has parameter name
  - Model OpenIdConnectRegistration no longer has parameter type
  - Model Login no longer has parameter kind
  - Model Login no longer has parameter id
  - Model Login no longer has parameter name
  - Model Login no longer has parameter type
  - Model Facebook no longer has parameter kind
  - Model Facebook no longer has parameter id
  - Model Facebook no longer has parameter name
  - Model Facebook no longer has parameter type
  - Model ClientRegistration no longer has parameter kind
  - Model ClientRegistration no longer has parameter id
  - Model ClientRegistration no longer has parameter name
  - Model ClientRegistration no longer has parameter type
  - Model GlobalValidation no longer has parameter kind
  - Model GlobalValidation no longer has parameter id
  - Model GlobalValidation no longer has parameter name
  - Model GlobalValidation no longer has parameter type
  - Model AuthPlatform no longer has parameter kind
  - Model AuthPlatform no longer has parameter id
  - Model AuthPlatform no longer has parameter name
  - Model AuthPlatform no longer has parameter type
  - Model FileSystemTokenStore has a new signature
  - Model AzureActiveDirectoryValidation has a new signature
  - Model LoginRoutes has a new signature
  - Model BlobStorageTokenStore has a new signature
  - Model OpenIdConnectClientCredential has a new signature
  - Model HttpSettingsRoutes has a new signature
  - Model LoginScopes has a new signature
  - Model AllowedAudiencesValidation has a new signature
  - Model AzureStaticWebAppsRegistration has a new signature

## 4.0.0 (2021-08-03)

**Features**

  - Model AppServicePlan has a new parameter elastic_scale_enabled
  - Added operation WebAppsOperations.update_swift_virtual_network_connection_with_check_slot
  - Added operation WebAppsOperations.create_or_update_swift_virtual_network_connection_with_check_slot
  - Added operation WebAppsOperations.update_swift_virtual_network_connection_with_check
  - Added operation WebAppsOperations.list_basic_publishing_credentials_policies
  - Added operation WebAppsOperations.list_basic_publishing_credentials_policies_slot

**Breaking changes**

  - Removed operation WebAppsOperations.get_basic_publishing_credentials_policies_slot
  - Removed operation WebAppsOperations.get_basic_publishing_credentials_policies

## 3.0.0 (2021-05-25)

**Features**

  - Model SiteAuthSettings has a new parameter config_version
  - Model CertificatePatchResource has a new parameter domain_validation_method
  - Model StaticSiteBuildProperties has a new parameter github_action_secret_name_override
  - Model StaticSiteBuildProperties has a new parameter output_location
  - Model StaticSiteBuildProperties has a new parameter api_build_command
  - Model StaticSiteBuildProperties has a new parameter skip_github_action_workflow_generation
  - Model StaticSiteBuildProperties has a new parameter app_build_command
  - Model DetectorResponse has a new parameter status
  - Model DetectorResponse has a new parameter data_providers_metadata
  - Model DetectorResponse has a new parameter suggested_utterances
  - Model StaticSitePatchResource has a new parameter key_vault_reference_identity
  - Model StaticSitePatchResource has a new parameter private_endpoint_connections
  - Model StaticSitePatchResource has a new parameter user_provided_function_apps
  - Model StaticSitePatchResource has a new parameter allow_config_file_updates
  - Model StaticSitePatchResource has a new parameter template_properties
  - Model StaticSitePatchResource has a new parameter staging_environment_policy
  - Model StaticSitePatchResource has a new parameter content_distribution_endpoint
  - Model StaticSitePatchResource has a new parameter provider
  - Model SiteConfigResource has a new parameter key_vault_reference_identity
  - Model SiteConfigResource has a new parameter functions_runtime_scale_monitoring_enabled
  - Model SiteConfigResource has a new parameter acr_user_managed_identity_id
  - Model SiteConfigResource has a new parameter public_network_access
  - Model SiteConfigResource has a new parameter website_time_zone
  - Model SiteConfigResource has a new parameter acr_use_managed_identity_creds
  - Model SiteConfigResource has a new parameter minimum_elastic_instance_count
  - Model SiteConfigResource has a new parameter function_app_scale_limit
  - Model SiteConfigResource has a new parameter azure_storage_accounts
  - Model ValidateRequest has a new parameter app_service_environment
  - Model StaticSiteCustomDomainOverviewARMResource has a new parameter status
  - Model StaticSiteCustomDomainOverviewARMResource has a new parameter error_message
  - Model StaticSiteCustomDomainOverviewARMResource has a new parameter validation_token
  - Model AppServicePlan has a new parameter extended_location
  - Model AppServicePlan has a new parameter kube_environment_profile
  - Model StaticSiteBuildARMResource has a new parameter user_provided_function_apps
  - Model AppServiceCertificateOrder has a new parameter contact
  - Model VnetParameters has a new parameter subnet_resource_id
  - Model SkuCapacity has a new parameter elastic_maximum
  - Model ApplicationStackResource has a new parameter is_deprecated
  - Model StackMajorVersion has a new parameter site_config_properties_dictionary
  - Model StackMajorVersion has a new parameter app_settings_dictionary
  - Model StatusCodesBasedTrigger has a new parameter path
  - Model AppServiceCertificateOrderPatchResource has a new parameter contact
  - Model BillingMeter has a new parameter multiplier
  - Model IdentityProviders has a new parameter legacy_microsoft_account
  - Model IdentityProviders has a new parameter apple
  - Model IdentityProviders has a new parameter azure_static_web_apps
  - Model StaticSiteARMResource has a new parameter key_vault_reference_identity
  - Model StaticSiteARMResource has a new parameter private_endpoint_connections
  - Model StaticSiteARMResource has a new parameter user_provided_function_apps
  - Model StaticSiteARMResource has a new parameter identity
  - Model StaticSiteARMResource has a new parameter allow_config_file_updates
  - Model StaticSiteARMResource has a new parameter template_properties
  - Model StaticSiteARMResource has a new parameter staging_environment_policy
  - Model StaticSiteARMResource has a new parameter content_distribution_endpoint
  - Model StaticSiteARMResource has a new parameter provider
  - Model SitePatchResource has a new parameter virtual_network_subnet_id
  - Model SitePatchResource has a new parameter storage_account_required
  - Model SitePatchResource has a new parameter key_vault_reference_identity
  - Model ApiKVReference has a new parameter name
  - Model ApiKVReference has a new parameter active_version
  - Model ApiKVReference has a new parameter type
  - Model ApiKVReference has a new parameter id
  - Model ApiKVReference has a new parameter kind
  - Model VnetValidationFailureDetails has a new parameter message
  - Model VnetValidationFailureDetails has a new parameter warnings
  - Model Site has a new parameter virtual_network_subnet_id
  - Model Site has a new parameter storage_account_required
  - Model Site has a new parameter extended_location
  - Model Site has a new parameter key_vault_reference_identity
  - Model Certificate has a new parameter domain_validation_method
  - Model CsmOperationDescription has a new parameter is_data_action
  - Model AutoHealTriggers has a new parameter slow_requests_with_path
  - Model AutoHealTriggers has a new parameter status_codes_range
  - Model SiteConfig has a new parameter key_vault_reference_identity
  - Model SiteConfig has a new parameter functions_runtime_scale_monitoring_enabled
  - Model SiteConfig has a new parameter acr_user_managed_identity_id
  - Model SiteConfig has a new parameter public_network_access
  - Model SiteConfig has a new parameter website_time_zone
  - Model SiteConfig has a new parameter acr_use_managed_identity_creds
  - Model SiteConfig has a new parameter minimum_elastic_instance_count
  - Model SiteConfig has a new parameter function_app_scale_limit
  - Model SiteConfig has a new parameter azure_storage_accounts
  - Model SlowRequestsBasedTrigger has a new parameter path
  - Model AppServicePlanPatchResource has a new parameter elastic_scale_enabled
  - Model AppServicePlanPatchResource has a new parameter kube_environment_profile
  - Model ApplicationStack has a new parameter is_deprecated
  - Model SiteSourceControl has a new parameter git_hub_action_configuration
  - Added operation ProviderOperations.get_function_app_stacks
  - Added operation ProviderOperations.get_web_app_stacks_for_location
  - Added operation ProviderOperations.get_web_app_stacks
  - Added operation ProviderOperations.get_function_app_stacks_for_location
  - Added operation StaticSitesOperations.get_private_endpoint_connection_list
  - Added operation StaticSitesOperations.detach_user_provided_function_app_from_static_site_build
  - Added operation StaticSitesOperations.begin_create_or_update_static_site
  - Added operation StaticSitesOperations.create_or_update_static_site_build_app_settings
  - Added operation StaticSitesOperations.begin_create_or_update_static_site_custom_domain
  - Added operation StaticSitesOperations.list_static_site_app_settings
  - Added operation StaticSitesOperations.begin_delete_private_endpoint_connection
  - Added operation StaticSitesOperations.detach_user_provided_function_app_from_static_site
  - Added operation StaticSitesOperations.begin_register_user_provided_function_app_with_static_site
  - Added operation StaticSitesOperations.begin_create_zip_deployment_for_static_site
  - Added operation StaticSitesOperations.begin_register_user_provided_function_app_with_static_site_build
  - Added operation StaticSitesOperations.list_static_site_configured_roles
  - Added operation StaticSitesOperations.begin_create_zip_deployment_for_static_site_build
  - Added operation StaticSitesOperations.begin_detach_static_site
  - Added operation StaticSitesOperations.get_private_endpoint_connection
  - Added operation StaticSitesOperations.begin_validate_custom_domain_can_be_added_to_static_site
  - Added operation StaticSitesOperations.create_or_update_static_site_app_settings
  - Added operation StaticSitesOperations.begin_delete_static_site_custom_domain
  - Added operation StaticSitesOperations.get_user_provided_function_app_for_static_site_build
  - Added operation StaticSitesOperations.get_user_provided_function_app_for_static_site
  - Added operation StaticSitesOperations.begin_approve_or_reject_private_endpoint_connection
  - Added operation StaticSitesOperations.begin_delete_static_site_build
  - Added operation StaticSitesOperations.get_static_site_custom_domain
  - Added operation StaticSitesOperations.begin_delete_static_site
  - Added operation StaticSitesOperations.get_user_provided_function_apps_for_static_site
  - Added operation StaticSitesOperations.get_user_provided_function_apps_for_static_site_build
  - Added operation StaticSitesOperations.get_private_link_resources
  - Added operation StaticSitesOperations.list_static_site_build_app_settings
  - Added operation AppServiceEnvironmentsOperations.get_private_endpoint_connection_list
  - Added operation AppServiceEnvironmentsOperations.get_private_link_resources
  - Added operation AppServiceEnvironmentsOperations.get_ase_v3_networking_configuration
  - Added operation AppServiceEnvironmentsOperations.get_private_endpoint_connection
  - Added operation AppServiceEnvironmentsOperations.begin_approve_or_reject_private_endpoint_connection
  - Added operation AppServiceEnvironmentsOperations.begin_delete_private_endpoint_connection
  - Added operation AppServiceEnvironmentsOperations.update_ase_networking_configuration
  - Added operation WebAppsOperations.update_ftp_allowed_slot
  - Added operation WebAppsOperations.get_private_endpoint_connection_list
  - Added operation WebAppsOperations.get_private_link_resources_slot
  - Added operation WebAppsOperations.get_site_connection_string_key_vault_reference
  - Added operation WebAppsOperations.get_ftp_allowed_slot
  - Added operation WebAppsOperations.get_site_connection_string_key_vault_reference_slot
  - Added operation WebAppsOperations.get_app_settings_key_vault_references
  - Added operation WebAppsOperations.get_site_connection_string_key_vault_references_slot
  - Added operation WebAppsOperations.get_app_settings_key_vault_references_slot
  - Added operation WebAppsOperations.get_app_setting_key_vault_reference_slot
  - Added operation WebAppsOperations.get_app_setting_key_vault_reference
  - Added operation WebAppsOperations.update_scm_allowed_slot
  - Added operation WebAppsOperations.get_private_endpoint_connection_list_slot
  - Added operation WebAppsOperations.get_scm_allowed_slot
  - Added operation WebAppsOperations.get_basic_publishing_credentials_policies_slot
  - Added operation WebAppsOperations.create_or_update_swift_virtual_network_connection_with_check
  - Added operation WebAppsOperations.get_private_endpoint_connection_slot
  - Added operation WebAppsOperations.begin_approve_or_reject_private_endpoint_connection_slot
  - Added operation WebAppsOperations.get_site_connection_string_key_vault_references
  - Added operation WebAppsOperations.begin_delete_private_endpoint_connection_slot
  - Added operation group KubeEnvironmentsOperations
  - Added operation group GlobalOperations
  - Added operation group CertificateOrdersDiagnosticsOperations

**Breaking changes**

  - Parameter id of model VirtualNetworkProfile is now required
  - Operation StaticSitesOperations.list_static_site_build_function_app_settings has a new signature
  - Operation StaticSitesOperations.list_static_site_build_functions has a new signature
  - Operation StaticSitesOperations.create_or_update_static_site_build_function_app_settings has a new signature
  - Operation StaticSitesOperations.get_static_site_build has a new signature
  - Operation CertificatesOperations.list has a new signature
  - Operation WebAppsOperations.delete_source_control has a new signature
  - Operation WebAppsOperations.delete_source_control_slot has a new signature
  - Model SwiftVirtualNetwork no longer has parameter system_data
  - Model CertificateOrderAction no longer has parameter system_data
  - Model GeoRegion no longer has parameter system_data
  - Model SiteAuthSettings no longer has parameter system_data
  - Model CsmPublishingCredentialsPoliciesCollection no longer has parameter system_data
  - Model AddressResponse no longer has parameter system_data
  - Model SiteLogsConfig no longer has parameter system_data
  - Model PrivateLinkConnectionApprovalRequestResource no longer has parameter system_data
  - Model PublicCertificate no longer has parameter system_data
  - Model Nonce no longer has parameter system_data
  - Model CertificatePatchResource no longer has parameter system_data
  - Model StorageMigrationOptions no longer has parameter system_data
  - Model DiagnosticCategory no longer has parameter system_data
  - Model DetectorResponse no longer has parameter system_data
  - Model CustomOpenIdConnectProvider no longer has parameter system_data
  - Model StaticSitePatchResource no longer has parameter system_data
  - Model CookieExpiration no longer has parameter system_data
  - Model MSDeployStatus no longer has parameter system_data
  - Model StaticSiteResetPropertiesARMResource no longer has parameter system_data
  - Model MSDeploy no longer has parameter system_data
  - Model DiagnosticDetectorResponse no longer has parameter system_data
  - Model DiagnosticAnalysis no longer has parameter system_data
  - Model SiteConfigResource no longer has parameter system_data
  - Model Recommendation no longer has parameter system_data
  - Model DeletedAppRestoreRequest no longer has parameter system_data
  - Model SlotConfigNamesResource no longer has parameter system_data
  - Model Domain no longer has parameter system_data
  - Model StorageMigrationResponse no longer has parameter system_data
  - Model VnetInfo no longer has parameter system_data
  - Model AzureActiveDirectoryLogin no longer has parameter system_data
  - Model SlotDifference no longer has parameter system_data
  - Model StaticSiteUserInvitationRequestResource no longer has parameter system_data
  - Model BackupRequest no longer has parameter system_data
  - Model PushSettings no longer has parameter system_data
  - Model StaticSiteCustomDomainOverviewARMResource no longer has parameter system_data
  - Model AppServicePlan no longer has parameter system_data
  - Model Google no longer has parameter system_data
  - Model Twitter no longer has parameter system_data
  - Model DomainOwnershipIdentifier no longer has parameter system_data
  - Model OpenIdConnectClientCredential no longer has parameter system_data
  - Model Identifier no longer has parameter system_data
  - Model RestoreRequest no longer has parameter system_data
  - Model SiteConfigurationSnapshotInfo no longer has parameter system_data
  - Model VnetRoute no longer has parameter system_data
  - Model StaticSiteBuildARMResource no longer has parameter system_data
  - Model SourceControl no longer has parameter system_data
  - Model AppServiceCertificateOrder no longer has parameter system_data
  - Model AzureActiveDirectory no longer has parameter system_data
  - Model DomainPatchResource no longer has parameter system_data
  - Model Resource no longer has parameter system_data
  - Model SiteAuthSettingsV2 no longer has parameter system_data
  - Model VnetParameters no longer has parameter system_data
  - Model ResourceMetricDefinition no longer has parameter system_data
  - Model LoginScopes no longer has parameter system_data
  - Model CertificateEmail no longer has parameter system_data
  - Model PremierAddOn no longer has parameter system_data
  - Model TriggeredJobRun no longer has parameter system_data
  - Model WebJob no longer has parameter system_data
  - Model StaticSiteUserARMResource no longer has parameter system_data
  - Model HybridConnectionKey no longer has parameter system_data
  - Model Deployment no longer has parameter system_data
  - Model PrivateAccess no longer has parameter system_data
  - Model VnetValidationTestFailure no longer has parameter system_data
  - Model StaticSitesWorkflowPreview no longer has parameter system_data
  - Model OpenIdConnectRegistration no longer has parameter system_data
  - Model ProxyOnlyResource no longer has parameter system_data
  - Model ApplicationStackResource no longer has parameter system_data
  - Model AzureStoragePropertyDictionaryResource no longer has parameter system_data
  - Model TwitterRegistration no longer has parameter system_data
  - Model RelayServiceConnectionEntity no longer has parameter system_data
  - Model CsmPublishingCredentialsPoliciesEntity no longer has parameter system_data
  - Model LoginRoutes no longer has parameter system_data
  - Model AnalysisDefinition no longer has parameter system_data
  - Model ReissueCertificateOrderRequest no longer has parameter system_data
  - Model User no longer has parameter system_data
  - Model AppServiceCertificateOrderPatchResource no longer has parameter system_data
  - Model TriggeredWebJob no longer has parameter system_data
  - Model HybridConnection no longer has parameter system_data
  - Model HttpSettingsRoutes no longer has parameter system_data
  - Model BillingMeter no longer has parameter system_data
  - Model SiteExtensionInfo no longer has parameter system_data
  - Model IdentityProviders no longer has parameter system_data
  - Model Snapshot no longer has parameter system_data
  - Model StaticSitesWorkflowPreviewRequest no longer has parameter system_data
  - Model HostNameBinding no longer has parameter system_data
  - Model AzureActiveDirectoryRegistration no longer has parameter system_data
  - Model StaticSiteARMResource no longer has parameter system_data
  - Model MigrateMySqlRequest no longer has parameter system_data
  - Model VnetGateway no longer has parameter system_data
  - Model ProcessInfo no longer has parameter system_data
  - Model WebSiteInstanceStatus no longer has parameter system_data
  - Model SitePatchResource no longer has parameter system_data
  - Model GitHub no longer has parameter system_data
  - Model TokenStore no longer has parameter system_data
  - Model ContinuousWebJob no longer has parameter system_data
  - Model FunctionEnvelope no longer has parameter system_data
  - Model BlobStorageTokenStore no longer has parameter system_data
  - Model PremierAddOnOffer no longer has parameter system_data
  - Model ProcessThreadInfo no longer has parameter system_data
  - Model ApiKVReference no longer has parameter location
  - Model AzureActiveDirectoryValidation no longer has parameter system_data
  - Model SnapshotRestoreRequest no longer has parameter system_data
  - Model DeletedSite no longer has parameter system_data
  - Model VnetValidationFailureDetails no longer has parameter system_data
  - Model Site no longer has parameter system_data
  - Model StaticSiteFunctionOverviewARMResource no longer has parameter system_data
  - Model RenewCertificateOrderRequest no longer has parameter system_data
  - Model Certificate no longer has parameter system_data
  - Model NetworkFeatures no longer has parameter system_data
  - Model ResourceHealthMetadata no longer has parameter system_data
  - Model DetectorDefinition no longer has parameter system_data
  - Model BackupItem no longer has parameter system_data
  - Model TriggeredJobHistory no longer has parameter system_data
  - Model Usage no longer has parameter system_data
  - Model MigrateMySqlStatus no longer has parameter system_data
  - Model ConnectionStringDictionary no longer has parameter system_data
  - Model CustomHostnameAnalysisResult no longer has parameter system_data
  - Model StringDictionary no longer has parameter system_data
  - Model TopLevelDomain no longer has parameter system_data
  - Model PremierAddOnPatchResource no longer has parameter system_data
  - Model AppServiceCertificatePatchResource no longer has parameter system_data
  - Model AllowedAudiencesValidation no longer has parameter system_data
  - Model Facebook no longer has parameter system_data
  - Model ClientRegistration no longer has parameter system_data
  - Model StaticSiteUserInvitationResponseResource no longer has parameter system_data
  - Model HybridConnectionLimits no longer has parameter system_data
  - Model RecommendationRule no longer has parameter system_data
  - Model ForwardProxy no longer has parameter system_data
  - Model Login no longer has parameter system_data
  - Model OpenIdConnectConfig no longer has parameter system_data
  - Model AppServiceCertificateResource no longer has parameter system_data
  - Model MSDeployLog no longer has parameter system_data
  - Model WorkerPoolResource no longer has parameter system_data
  - Model SitePhpErrorLogFlag no longer has parameter system_data
  - Model AppServicePlanPatchResource no longer has parameter system_data
  - Model OpenIdConnectLogin no longer has parameter system_data
  - Model SiteSourceControl no longer has parameter system_data
  - Model AuthPlatform no longer has parameter system_data
  - Model FileSystemTokenStore no longer has parameter system_data
  - Model AppRegistration no longer has parameter system_data
  - Model ProcessModuleInfo no longer has parameter system_data
  - Model HttpSettings no longer has parameter system_data
  - Model GlobalValidation no longer has parameter system_data
  - Model JwtClaimChecks no longer has parameter system_data
  - Model AppServiceEnvironmentResource has a new signature
  - Model AppServiceEnvironment has a new signature
  - Model DetectorInfo has a new signature
  - Model AppServiceEnvironmentPatchResource has a new signature
  - Removed operation StaticSitesOperations.create_or_update_static_site
  - Removed operation StaticSitesOperations.validate_custom_domain_can_be_added_to_static_site
  - Removed operation StaticSitesOperations.delete_static_site_custom_domain
  - Removed operation StaticSitesOperations.delete_static_site_build
  - Removed operation StaticSitesOperations.delete_static_site
  - Removed operation StaticSitesOperations.create_or_update_static_site_custom_domain
  - Removed operation StaticSitesOperations.detach_static_site
  - Removed operation WebAppsOperations.update_swift_virtual_network_connection
  - Removed operation WebAppsOperations.begin_copy_production_slot
  - Removed operation WebAppsOperations.create_or_update_swift_virtual_network_connection_slot
  - Removed operation WebAppsOperations.update_swift_virtual_network_connection_slot
  - Removed operation WebAppsOperations.create_or_update_swift_virtual_network_connection
  - Removed operation WebAppsOperations.begin_copy_slot

## 2.0.0 (2021-02-25)

**Features**

  - Model Usage has a new parameter system_data
  - Model StaticSiteFunctionOverviewARMResource has a new parameter system_data
  - Model HybridConnection has a new parameter system_data
  - Model GeoRegion has a new parameter system_data
  - Model IpSecurityRestriction has a new parameter headers
  - Model StaticSiteBuildARMResource has a new parameter system_data
  - Model PushSettings has a new parameter system_data
  - Model SlotDifference has a new parameter system_data
  - Model AppServiceCertificatePatchResource has a new parameter system_data
  - Model DiagnosticDetectorResponse has a new parameter system_data
  - Model MetricSpecification has a new parameter supported_aggregation_types
  - Model PremierAddOnPatchResource has a new parameter system_data
  - Model SitePatchResource has a new parameter custom_domain_verification_id
  - Model SitePatchResource has a new parameter system_data
  - Model SitePatchResource has a new parameter client_cert_mode
  - Model HostNameBinding has a new parameter system_data
  - Model CustomHostnameAnalysisResult has a new parameter system_data
  - Model VnetGateway has a new parameter system_data
  - Model MSDeployLog has a new parameter system_data
  - Model Site has a new parameter custom_domain_verification_id
  - Model Site has a new parameter system_data
  - Model Site has a new parameter client_cert_mode
  - Model PrivateEndpointConnectionResource has a new parameter system_data
  - Model ResourceHealthMetadata has a new parameter system_data
  - Model CertificatePatchResource has a new parameter system_data
  - Model WorkerPoolResource has a new parameter system_data
  - Model AppServiceEnvironmentResource has a new parameter system_data
  - Model DetectorResponse has a new parameter system_data
  - Model TriggeredWebJob has a new parameter system_data
  - Model SiteSourceControl has a new parameter is_git_hub_action
  - Model SiteSourceControl has a new parameter system_data
  - Model MSDeploy has a new parameter system_data
  - Model TriggeredJobHistory has a new parameter system_data
  - Model SiteConfigResource has a new parameter vnet_route_all_enabled
  - Model SiteConfigResource has a new parameter system_data
  - Model SiteConfigResource has a new parameter scm_min_tls_version
  - Model SiteConfigResource has a new parameter vnet_private_ports_count
  - Model BackupRequest has a new parameter system_data
  - Model DeletedSite has a new parameter system_data
  - Model RenewCertificateOrderRequest has a new parameter system_data
  - Model StorageMigrationResponse has a new parameter system_data
  - Model CsmPublishingCredentialsPoliciesCollection has a new parameter system_data
  - Model AddressResponse has a new parameter system_data
  - Model BillingMeter has a new parameter system_data
  - Model Deployment has a new parameter system_data
  - Model ProcessModuleInfo has a new parameter system_data
  - Model CertificateEmail has a new parameter system_data
  - Model Certificate has a new parameter system_data
  - Model StaticSitePatchResource has a new parameter system_data
  - Model SitePhpErrorLogFlag has a new parameter system_data
  - Model CsmPublishingCredentialsPoliciesEntity has a new parameter system_data
  - Model SwiftVirtualNetwork has a new parameter system_data
  - Model VnetRoute has a new parameter system_data
  - Model ConnectionStringDictionary has a new parameter system_data
  - Model WebSiteInstanceStatus has a new parameter system_data
  - Model WebSiteInstanceStatus has a new parameter health_check_url
  - Model HybridConnectionKey has a new parameter system_data
  - Model PremierAddOnOffer has a new parameter system_data
  - Model ContinuousWebJob has a new parameter system_data
  - Model SnapshotRestoreRequest has a new parameter system_data
  - Model SiteAuthSettings has a new parameter git_hub_client_id
  - Model SiteAuthSettings has a new parameter microsoft_account_client_secret_setting_name
  - Model SiteAuthSettings has a new parameter git_hub_client_secret
  - Model SiteAuthSettings has a new parameter is_auth_from_file
  - Model SiteAuthSettings has a new parameter auth_file_path
  - Model SiteAuthSettings has a new parameter google_client_secret_setting_name
  - Model SiteAuthSettings has a new parameter git_hub_client_secret_setting_name
  - Model SiteAuthSettings has a new parameter aad_claims_authorization
  - Model SiteAuthSettings has a new parameter system_data
  - Model SiteAuthSettings has a new parameter git_hub_o_auth_scopes
  - Model SiteAuthSettings has a new parameter client_secret_setting_name
  - Model SiteAuthSettings has a new parameter twitter_consumer_secret_setting_name
  - Model SiteAuthSettings has a new parameter facebook_app_secret_setting_name
  - Model DetectorDefinition has a new parameter system_data
  - Model SiteConfigurationSnapshotInfo has a new parameter system_data
  - Model PublicCertificate has a new parameter system_data
  - Model DomainOwnershipIdentifier has a new parameter system_data
  - Model StringDictionary has a new parameter system_data
  - Model PrivateLinkConnectionApprovalRequestResource has a new parameter system_data
  - Model SlotConfigNamesResource has a new parameter system_data
  - Model WebJob has a new parameter system_data
  - Model ApplicationStackResource has a new parameter system_data
  - Model ReissueCertificateOrderRequest has a new parameter system_data
  - Model User has a new parameter system_data
  - Model RestoreRequest has a new parameter system_data
  - Model StaticSiteUserInvitationRequestResource has a new parameter system_data
  - Model StorageMigrationOptions has a new parameter system_data
  - Model HybridConnectionLimits has a new parameter system_data
  - Model StaticSiteUserARMResource has a new parameter system_data
  - Model AppServiceCertificateResource has a new parameter system_data
  - Model AnalysisDefinition has a new parameter system_data
  - Model VnetInfo has a new parameter system_data
  - Model DomainPatchResource has a new parameter system_data
  - Model MSDeployStatus has a new parameter system_data
  - Model MigrateMySqlRequest has a new parameter system_data
  - Model Identifier has a new parameter system_data
  - Model SiteLogsConfig has a new parameter system_data
  - Model AppServiceCertificateOrder has a new parameter system_data
  - Model BackupItem has a new parameter system_data
  - Model ProcessInfo has a new parameter system_data
  - Model MigrateMySqlStatus has a new parameter system_data
  - Model StaticSiteResetPropertiesARMResource has a new parameter system_data
  - Model NetworkFeatures has a new parameter system_data
  - Model Recommendation has a new parameter system_data
  - Model ProcessThreadInfo has a new parameter system_data
  - Model AzureStoragePropertyDictionaryResource has a new parameter system_data
  - Model Domain has a new parameter system_data
  - Model StaticSiteARMResource has a new parameter system_data
  - Model ResourceMetricDefinition has a new parameter system_data
  - Model VnetValidationTestFailure has a new parameter system_data
  - Model StaticSiteUserInvitationResponseResource has a new parameter system_data
  - Model PrivateAccess has a new parameter system_data
  - Model SiteConfig has a new parameter vnet_route_all_enabled
  - Model SiteConfig has a new parameter vnet_private_ports_count
  - Model SiteConfig has a new parameter scm_min_tls_version
  - Model FunctionEnvelope has a new parameter system_data
  - Model TopLevelDomain has a new parameter system_data
  - Model RecommendationRule has a new parameter system_data
  - Model RelayServiceConnectionEntity has a new parameter system_data
  - Model ProxyOnlyResource has a new parameter system_data
  - Model Snapshot has a new parameter system_data
  - Model VnetParameters has a new parameter system_data
  - Model DiagnosticAnalysis has a new parameter system_data
  - Model CertificateOrderAction has a new parameter system_data
  - Model DeletedAppRestoreRequest has a new parameter system_data
  - Model AppServicePlan has a new parameter system_data
  - Model Resource has a new parameter system_data
  - Model StaticSiteCustomDomainOverviewARMResource has a new parameter system_data
  - Model PremierAddOn has a new parameter system_data
  - Model TriggeredJobRun has a new parameter system_data
  - Model LogSpecification has a new parameter log_filter_pattern
  - Model DiagnosticCategory has a new parameter system_data
  - Model SourceControl has a new parameter system_data
  - Model VnetValidationFailureDetails has a new parameter system_data
  - Model AppServiceEnvironmentPatchResource has a new parameter system_data
  - Model AppServiceCertificateOrderPatchResource has a new parameter system_data
  - Model SiteExtensionInfo has a new parameter system_data
  - Model AppServicePlanPatchResource has a new parameter system_data
  - Added operation WebAppsOperations.update_auth_settings_v2
  - Added operation WebAppsOperations.update_auth_settings_v2_slot
  - Added operation WebAppsOperations.get_auth_settings_v2
  - Added operation WebAppsOperations.get_auth_settings_v2_slot
  - Added operation StaticSitesOperations.preview_workflow
  - Added operation WebSiteManagementClientOperationsMixin.generate_github_access_token_for_appservice_cli_async

**Breaking changes**

  - Model SiteConfigResource no longer has parameter acr_use_managed_identity_creds
  - Model SiteConfigResource no longer has parameter acr_user_managed_identity_id
  - Model SiteConfig no longer has parameter acr_use_managed_identity_creds
  - Model SiteConfig no longer has parameter acr_user_managed_identity_id
  - Model FunctionSecrets has a new signature
  - Removed operation WebAppsOperations.get_app_settings_key_vault_references
  - Removed operation WebAppsOperations.get_app_setting_key_vault_reference

## 1.0.0 (2020-11-23)

- GA release

## 1.0.0b1 (2020-10-13)

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

## 0.48.0 (2020-09-22)

**Features**

  - Model SiteConfig has a new parameter acr_use_managed_identity_creds
  - Model SiteConfig has a new parameter acr_user_managed_identity_id
  - Model SiteConfigResource has a new parameter acr_use_managed_identity_creds
  - Model SiteConfigResource has a new parameter acr_user_managed_identity_id

## 0.47.0 (2020-06-03)

**Features**

  - Added operation WebAppsOperations.get_basic_publishing_credentials_policies
  - Added operation WebAppsOperations.update_scm_allowed
  - Added operation WebAppsOperations.update_ftp_allowed
  - Added operation WebAppsOperations.get_scm_allowed
  - Added operation WebAppsOperations.get_ftp_allowed

## 0.46.0 (2020-04-10)

**Features**

  - Model SiteConfig has a new parameter power_shell_version
  - Model SiteConfigResource has a new parameter power_shell_version
  - Added operation WebAppsOperations.get_private_endpoint_connection
  - Added operation WebAppsOperations.get_private_link_resources
  - Added operation WebAppsOperations.delete_private_endpoint_connection
  - Added operation WebAppsOperations.approve_or_reject_private_endpoint_connection

## 0.45.0 (2020-03-20)

**Features**

  - Added operation WebAppsOperations.list_host_keys
  - Added operation WebAppsOperations.sync_functions
  - Added operation WebAppsOperations.list_function_keys_slot
  - Added operation WebAppsOperations.sync_functions_slot
  - Added operation WebAppsOperations.delete_function_secret
  - Added operation WebAppsOperations.delete_host_secret_slot
  - Added operation WebAppsOperations.list_host_keys_slot
  - Added operation WebAppsOperations.delete_function_secret_slot
  - Added operation WebAppsOperations.create_or_update_host_secret
  - Added operation WebAppsOperations.list_sync_status
  - Added operation WebAppsOperations.list_sync_status_slot
  - Added operation WebAppsOperations.create_or_update_function_secret_slot
  - Added operation WebAppsOperations.list_function_keys
  - Added operation WebAppsOperations.create_or_update_host_secret_slot
  - Added operation WebAppsOperations.create_or_update_function_secret
  - Added operation WebAppsOperations.delete_host_secret
  - Added operation group StaticSitesOperations

## 0.44.0 (2019-11-08)

**Features**

  - Model EndpointDetail has a new parameter is_accessible
  - Model Identifier has a new parameter value
  - Model VirtualIPMapping has a new parameter service_name
  - Model SiteConfig has a new parameter health_check_path
  - Model SiteConfig has a new parameter pre_warmed_instance_count
  - Model SiteConfig has a new parameter api_management_config
  - Model CertificatePatchResource has a new parameter canonical_name
  - Model ValidateRequest has a new parameter container_image_platform
  - Model ValidateRequest has a new parameter
    container_registry_password
  - Model ValidateRequest has a new parameter
    container_image_repository
  - Model ValidateRequest has a new parameter container_image_tag
  - Model ValidateRequest has a new parameter
    container_registry_base_url
  - Model ValidateRequest has a new parameter
    container_registry_username
  - Model MetricSpecification has a new parameter
    supported_time_grain_types
  - Model FunctionEnvelope has a new parameter invoke_url_template
  - Model FunctionEnvelope has a new parameter is_disabled
  - Model FunctionEnvelope has a new parameter language
  - Model FunctionEnvelope has a new parameter test_data_href
  - Model GeoRegion has a new parameter org_domain
  - Model Certificate has a new parameter canonical_name
  - Model StackMajorVersion has a new parameter is_deprecated
  - Model StackMajorVersion has a new parameter is_hidden
  - Model StackMajorVersion has a new parameter is_preview
  - Model SiteConfigResource has a new parameter health_check_path
  - Model SiteConfigResource has a new parameter
    pre_warmed_instance_count
  - Model SiteConfigResource has a new parameter api_management_config
  - Model HostingEnvironmentDiagnostics has a new parameter
    diagnostics_output
  - Model AddressResponse has a new parameter type
  - Model AddressResponse has a new parameter id
  - Model AddressResponse has a new parameter name
  - Model AddressResponse has a new parameter kind
  - Added operation AppServiceEnvironmentsOperations.get_vip_info
  - Added operation WebAppsOperations.copy_production_slot
  - Added operation WebAppsOperations.list_site_backups
  - Added operation
    WebAppsOperations.get_app_setting_key_vault_reference
  - Added operation
    WebAppsOperations.get_app_settings_key_vault_references
  - Added operation WebAppsOperations.copy_slot_slot
  - Added operation WebAppsOperations.get_instance_info_slot
  - Added operation WebAppsOperations.get_instance_info
  - Added operation WebAppsOperations.list_site_backups_slot

**Breaking changes**

  - Operation
    WebAppsOperations.create_or_update_domain_ownership_identifier
    has a new signature
  - Operation
    WebAppsOperations.create_or_update_domain_ownership_identifier_slot
    has a new signature
  - Operation
    WebAppsOperations.update_domain_ownership_identifier_slot has a
    new signature
  - Operation WebAppsOperations.update_domain_ownership_identifier
    has a new signature
  - Model SitePatchResource no longer has parameter geo_distributions
  - Model Site no longer has parameter geo_distributions
  - Model EndpointDetail no longer has parameter is_accessable
  - Model ProcessThreadInfo no longer has parameter
    priviledged_processor_time
  - Model Identifier no longer has parameter identifier_id
  - Model SiteConfig no longer has parameter reserved_instance_count
  - Model SiteConfig no longer has parameter azure_storage_accounts
  - Model SiteConfigResource no longer has parameter
    reserved_instance_count
  - Model SiteConfigResource no longer has parameter
    azure_storage_accounts
  - Model HostingEnvironmentDiagnostics no longer has parameter
    diagnosics_output
  - Removed operation AppServicePlansOperations.list_metric_defintions
  - Removed operation AppServicePlansOperations.list_metrics
  - Removed operation
    WebSiteManagementClientOperationsMixin.validate_container_settings
  - Removed operation AppServiceEnvironmentsOperations.list_metrics
  - Removed operation
    AppServiceEnvironmentsOperations.list_worker_pool_instance_metrics
  - Removed operation
    AppServiceEnvironmentsOperations.list_multi_role_pool_instance_metrics
  - Removed operation
    AppServiceEnvironmentsOperations.list_multi_role_metrics
  - Removed operation AppServiceEnvironmentsOperations.list_vips
  - Removed operation
    AppServiceEnvironmentsOperations.list_web_worker_metrics
  - Removed operation
    AppServiceEnvironmentsOperations.list_metric_definitions
  - Removed operation WebAppsOperations.get_instance_process_thread
  - Removed operation WebAppsOperations.list_metrics
  - Removed operation WebAppsOperations.get_process_thread
  - Removed operation WebAppsOperations.list_hybrid_connection_keys
  - Removed operation WebAppsOperations.list_metric_definitions_slot
  - Removed operation WebAppsOperations.list_metrics_slot
  - Removed operation WebAppsOperations.get_process_thread_slot
  - Removed operation
    WebAppsOperations.list_hybrid_connection_keys_slot
  - Removed operation
    WebAppsOperations.get_instance_process_thread_slot
  - Removed operation WebAppsOperations.list_metric_definitions

## 0.43.1 (2019-10-17)

**General**

  - Fixed incorrectly generated multi-api package structure

## 0.43.0 (2019-10-01)

**Features**

  - Added operation group BillingMetersOperations
  - Added operation group WebSiteManagementClientOperationsMixin

**General**

  - Package is now multiapi

## 0.42.0 (2019-05-24)

**Features**

  - Model SitePatchResource has a new parameter identity
  - Model ManagedServiceIdentity has a new parameter
    user_assigned_identities
  - Model CloningInfo has a new parameter source_web_app_location
  - Added operation
    AppServiceEnvironmentsOperations.get_inbound_network_dependencies_endpoints
  - Added operation
    AppServiceEnvironmentsOperations.get_outbound_network_dependencies_endpoints
  - Added operation DeletedWebAppsOperations.list_by_location
  - Added operation
    DeletedWebAppsOperations.get_deleted_web_app_by_location

**Breaking changes**

  - Model ManagedServiceIdentity has a new parameter
    user_assigned_identities (renamed from identity_ids)

## 0.41.0 (2019-02-13)

**Features**

  - Model DeletedAppRestoreRequest has a new parameter
    use_dr_secondary
  - Model StackMinorVersion has a new parameter
    is_remote_debugging_enabled
  - Model IpSecurityRestriction has a new parameter subnet_traffic_tag
  - Model IpSecurityRestriction has a new parameter vnet_traffic_tag
  - Model IpSecurityRestriction has a new parameter
    vnet_subnet_resource_id
  - Model DeletedSite has a new parameter geo_region_name
  - Model SnapshotRestoreRequest has a new parameter use_dr_secondary
  - Model SiteAuthSettings has a new parameter
    client_secret_certificate_thumbprint
  - Model SiteConfig has a new parameter
    scm_ip_security_restrictions_use_main
  - Model SiteConfig has a new parameter scm_ip_security_restrictions
  - Model CorsSettings has a new parameter support_credentials
  - Model SiteConfigResource has a new parameter
    scm_ip_security_restrictions_use_main
  - Model SiteConfigResource has a new parameter
    scm_ip_security_restrictions
  - Model StackMajorVersion has a new parameter application_insights
  - Model AppServicePlanPatchResource has a new parameter
    maximum_elastic_worker_count
  - Model AppServicePlan has a new parameter
    maximum_elastic_worker_count
  - Model SitePatchResource has a new parameter geo_distributions
  - Model SitePatchResource has a new parameter
    in_progress_operation_id
  - Model SitePatchResource has a new parameter
    client_cert_exclusion_paths
  - Model SitePatchResource has a new parameter redundancy_mode
  - Model Site has a new parameter geo_distributions
  - Model Site has a new parameter in_progress_operation_id
  - Model Site has a new parameter client_cert_exclusion_paths
  - Model Site has a new parameter redundancy_mode
  - Model VnetInfo has a new parameter is_swift
  - Added operation WebAppsOperations.get_network_traces_slot_v2
  - Added operation
    WebAppsOperations.list_snapshots_from_dr_secondary_slot
  - Added operation WebAppsOperations.get_network_traces_slot
  - Added operation
    WebAppsOperations.start_web_site_network_trace_operation_slot
  - Added operation WebAppsOperations.get_network_trace_operation_v2
  - Added operation
    WebAppsOperations.start_web_site_network_trace_operation
  - Added operation WebAppsOperations.get_network_traces_v2
  - Added operation WebAppsOperations.stop_network_trace_slot
  - Added operation
    WebAppsOperations.get_network_trace_operation_slot_v2
  - Added operation
    WebAppsOperations.list_snapshots_from_dr_secondary
  - Added operation
    WebAppsOperations.get_network_trace_operation_slot
  - Added operation WebAppsOperations.stop_network_trace
  - Added operation WebAppsOperations.start_network_trace_slot
  - Added operation WebAppsOperations.get_network_trace_operation
  - Added operation WebAppsOperations.start_network_trace
  - Added operation WebAppsOperations.get_network_traces
  - Added operation
    RecommendationsOperations.list_recommended_rules_for_hosting_environment
  - Added operation
    RecommendationsOperations.list_history_for_hosting_environment
  - Added operation
    RecommendationsOperations.disable_all_for_hosting_environment
  - Added operation
    RecommendationsOperations.disable_recommendation_for_hosting_environment
  - Added operation
    RecommendationsOperations.reset_all_filters_for_hosting_environment
  - Added operation
    RecommendationsOperations.get_rule_details_by_hosting_environment

**Breaking changes**

  - Model AppServicePlanPatchResource no longer has parameter
    admin_site_name
  - Model AppServicePlan no longer has parameter admin_site_name

## 0.40.0 (2018-08-28)

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes.

  - Model signatures now use only keyword-argument syntax. All
    positional arguments must be re-written as keyword-arguments. To
    keep auto-completion in most cases, models are now generated for
    Python 2 and Python 3. Python 3 uses the "*" syntax for
    keyword-only arguments.
  - Enum types now use the "str" mixin (class AzureEnum(str, Enum)) to
    improve the behavior when unrecognized enum values are encountered.
    While this is not a breaking change, the distinctions are important,
    and are documented here:
    <https://docs.python.org/3/library/enum.html#others> At a glance:
      - "is" should not be used at all.
      - "format" will return the string value, where "%s" string
        formatting will return `NameOfEnum.stringvalue`. Format syntax
        should be prefered.
  - New Long Running Operation:
      - Return type changes from
        `msrestazure.azure_operation.AzureOperationPoller` to
        `msrest.polling.LROPoller`. External API is the same.
      - Return type is now **always** a `msrest.polling.LROPoller`,
        regardless of the optional parameters used.
      - The behavior has changed when using `raw=True`. Instead of
        returning the initial call result as `ClientRawResponse`,
        without polling, now this returns an LROPoller. After polling,
        the final resource will be returned as a `ClientRawResponse`.
      - New `polling` parameter. The default behavior is
        `Polling=True` which will poll using ARM algorithm. When
        `Polling=False`, the response of the initial call will be
        returned without polling.
      - `polling` parameter accepts instances of subclasses of
        `msrest.polling.PollingMethod`.
      - `add_done_callback` will no longer raise if called after
        polling is finished, but will instead execute the callback right
        away.

**General Features**

  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance

**Features**

  - Model ValidateRequest has a new parameter is_xenon
  - Model SiteConfigResource has a new parameter
    reserved_instance_count
  - Model SiteConfigResource has a new parameter windows_fx_version
  - Model SiteConfigResource has a new parameter
    azure_storage_accounts
  - Model SiteConfigResource has a new parameter
    x_managed_service_identity_id
  - Model SiteConfigResource has a new parameter
    managed_service_identity_id
  - Model SiteConfigResource has a new parameter ftps_state
  - Model TriggeredWebJob has a new parameter web_job_type
  - Model CsmPublishingProfileOptions has a new parameter
    include_disaster_recovery_endpoints
  - Model SitePatchResource has a new parameter hyper_v
  - Model SitePatchResource has a new parameter is_xenon
  - Model StampCapacity has a new parameter is_linux
  - Model User has a new parameter scm_uri
  - Model SiteConfigurationSnapshotInfo has a new parameter snapshot_id
  - Model AppServiceEnvironmentPatchResource has a new parameter
    ssl_cert_key_vault_secret_name
  - Model AppServiceEnvironmentPatchResource has a new parameter
    has_linux_workers
  - Model AppServiceEnvironmentPatchResource has a new parameter
    ssl_cert_key_vault_id
  - Model BackupRequest has a new parameter backup_name
  - Model RecommendationRule has a new parameter id
  - Model RecommendationRule has a new parameter recommendation_name
  - Model RecommendationRule has a new parameter kind
  - Model RecommendationRule has a new parameter type
  - Model RecommendationRule has a new parameter category_tags
  - Model Site has a new parameter hyper_v
  - Model Site has a new parameter is_xenon
  - Model TriggeredJobRun has a new parameter web_job_id
  - Model TriggeredJobRun has a new parameter web_job_name
  - Model CertificateOrderAction has a new parameter action_type
  - Model SiteExtensionInfo has a new parameter
    installer_command_line_params
  - Model SiteExtensionInfo has a new parameter extension_id
  - Model SiteExtensionInfo has a new parameter extension_type
  - Model SiteAuthSettings has a new parameter validate_issuer
  - Model TriggeredJobHistory has a new parameter runs
  - Model ProcessInfo has a new parameter minidump
  - Model ProcessInfo has a new parameter total_cpu_time
  - Model ProcessInfo has a new parameter non_paged_system_memory
  - Model ProcessInfo has a new parameter working_set
  - Model ProcessInfo has a new parameter paged_memory
  - Model ProcessInfo has a new parameter private_memory
  - Model ProcessInfo has a new parameter user_cpu_time
  - Model ProcessInfo has a new parameter deployment_name
  - Model ProcessInfo has a new parameter peak_paged_memory
  - Model ProcessInfo has a new parameter peak_working_set
  - Model ProcessInfo has a new parameter peak_virtual_memory
  - Model ProcessInfo has a new parameter is_webjob
  - Model ProcessInfo has a new parameter privileged_cpu_time
  - Model ProcessInfo has a new parameter identifier
  - Model ProcessInfo has a new parameter paged_system_memory
  - Model ProcessInfo has a new parameter virtual_memory
  - Model ServiceSpecification has a new parameter log_specifications
  - Model ProcessThreadInfo has a new parameter identifier
  - Model ManagedServiceIdentity has a new parameter identity_ids
  - Model AppServicePlan has a new parameter
    free_offer_expiration_time
  - Model AppServicePlan has a new parameter hyper_v
  - Model AppServicePlan has a new parameter is_xenon
  - Model SiteConfig has a new parameter reserved_instance_count
  - Model SiteConfig has a new parameter windows_fx_version
  - Model SiteConfig has a new parameter azure_storage_accounts
  - Model SiteConfig has a new parameter
    x_managed_service_identity_id
  - Model SiteConfig has a new parameter managed_service_identity_id
  - Model SiteConfig has a new parameter ftps_state
  - Model WebJob has a new parameter web_job_type
  - Model Recommendation has a new parameter name
  - Model Recommendation has a new parameter id
  - Model Recommendation has a new parameter kind
  - Model Recommendation has a new parameter enabled
  - Model Recommendation has a new parameter type
  - Model Recommendation has a new parameter states
  - Model Recommendation has a new parameter category_tags
  - Model SlotConfigNamesResource has a new parameter
    azure_storage_config_names
  - Model SlotDifference has a new parameter level
  - Model AppServiceEnvironment has a new parameter
    ssl_cert_key_vault_secret_name
  - Model AppServiceEnvironment has a new parameter has_linux_workers
  - Model AppServiceEnvironment has a new parameter
    ssl_cert_key_vault_id
  - Model ContinuousWebJob has a new parameter web_job_type
  - Model AppServiceEnvironmentResource has a new parameter
    ssl_cert_key_vault_secret_name
  - Model AppServiceEnvironmentResource has a new parameter
    has_linux_workers
  - Model AppServiceEnvironmentResource has a new parameter
    ssl_cert_key_vault_id
  - Model AppServicePlanPatchResource has a new parameter
    free_offer_expiration_time
  - Model AppServicePlanPatchResource has a new parameter hyper_v
  - Model AppServicePlanPatchResource has a new parameter is_xenon
  - Model DeletedSite has a new parameter deleted_site_name
  - Model DeletedSite has a new parameter deleted_site_kind
  - Model DeletedSite has a new parameter kind
  - Model DeletedSite has a new parameter type
  - Model DeletedSite has a new parameter deleted_site_id
  - Added operation WebAppsOperations.put_private_access_vnet
  - Added operation
    WebAppsOperations.create_or_update_swift_virtual_network_connection
  - Added operation WebAppsOperations.update_azure_storage_accounts
  - Added operation WebAppsOperations.update_premier_add_on_slot
  - Added operation WebAppsOperations.get_container_logs_zip_slot
  - Added operation WebAppsOperations.discover_backup_slot
  - Added operation
    WebAppsOperations.update_swift_virtual_network_connection_slot
  - Added operation WebAppsOperations.get_private_access
  - Added operation WebAppsOperations.discover_backup
  - Added operation
    WebAppsOperations.create_or_update_swift_virtual_network_connection_slot
  - Added operation WebAppsOperations.delete_swift_virtual_network
  - Added operation WebAppsOperations.put_private_access_vnet_slot
  - Added operation WebAppsOperations.restore_from_deleted_app
  - Added operation WebAppsOperations.restore_from_backup_blob
  - Added operation
    WebAppsOperations.delete_swift_virtual_network_slot
  - Added operation WebAppsOperations.list_azure_storage_accounts
  - Added operation
    WebAppsOperations.list_azure_storage_accounts_slot
  - Added operation WebAppsOperations.restore_from_backup_blob_slot
  - Added operation
    WebAppsOperations.get_swift_virtual_network_connection
  - Added operation
    WebAppsOperations.get_swift_virtual_network_connection_slot
  - Added operation WebAppsOperations.get_container_logs_zip
  - Added operation WebAppsOperations.restore_snapshot
  - Added operation
    WebAppsOperations.update_swift_virtual_network_connection
  - Added operation WebAppsOperations.restore_snapshot_slot
  - Added operation WebAppsOperations.restore_from_deleted_app_slot
  - Added operation
    WebAppsOperations.update_azure_storage_accounts_slot
  - Added operation WebAppsOperations.get_private_access_slot
  - Added operation WebAppsOperations.update_premier_add_on
  - Added operation AppServiceEnvironmentsOperations.change_vnet
  - Added operation
    DiagnosticsOperations.list_site_detector_responses_slot
  - Added operation
    DiagnosticsOperations.get_site_detector_response_slot
  - Added operation DiagnosticsOperations.get_site_detector_response
  - Added operation
    DiagnosticsOperations.get_hosting_environment_detector_response
  - Added operation
    DiagnosticsOperations.list_site_detector_responses
  - Added operation
    DiagnosticsOperations.list_hosting_environment_detector_responses
  - Added operation
    RecommendationsOperations.disable_recommendation_for_subscription
  - Added operation
    RecommendationsOperations.disable_recommendation_for_site
  - Added operation group ResourceHealthMetadataOperations

**Breaking changes**

  - Operation RecommendationsOperations.get_rule_details_by_web_app
    has a new signature
  - Operation
    WebAppsOperations.list_publishing_profile_xml_with_secrets has
    a new signature
  - Operation
    WebAppsOperations.list_publishing_profile_xml_with_secrets_slot
    has a new signature
  - Operation WebAppsOperations.delete_slot has a new signature
  - Operation WebAppsOperations.delete has a new signature
  - Operation RecommendationsOperations.list_history_for_web_app has
    a new signature
  - Operation WebAppsOperations.update_slot has a new signature
  - Operation WebAppsOperations.create_or_update_slot has a new
    signature
  - Operation WebAppsOperations.create_or_update has a new signature
  - Operation WebAppsOperations.update has a new signature
  - Model TriggeredWebJob no longer has parameter
    triggered_web_job_name
  - Model TriggeredWebJob no longer has parameter job_type
  - Model SitePatchResource no longer has parameter snapshot_info
  - Model User no longer has parameter user_name
  - Model SiteConfigurationSnapshotInfo no longer has parameter
    site_configuration_snapshot_info_id
  - Model BackupRequest no longer has parameter backup_request_name
  - Model BackupRequest no longer has parameter backup_request_type
  - Model ResourceMetricDefinition no longer has parameter
    resource_metric_definition_id
  - Model ResourceMetricDefinition no longer has parameter
    resource_metric_definition_name
  - Model RecommendationRule no longer has parameter tags
  - Model SourceControl no longer has parameter source_control_name
  - Model Site no longer has parameter snapshot_info
  - Model VnetRoute no longer has parameter vnet_route_name
  - Model Certificate no longer has parameter geo_region
  - Model TriggeredJobRun no longer has parameter
    triggered_job_run_id
  - Model TriggeredJobRun no longer has parameter
    triggered_job_run_name
  - Model CertificateOrderAction no longer has parameter
    certificate_order_action_type
  - Model SiteExtensionInfo no longer has parameter
    site_extension_info_id
  - Model SiteExtensionInfo no longer has parameter installation_args
  - Model SiteExtensionInfo no longer has parameter
    site_extension_info_type
  - Model PremierAddOnOffer no longer has parameter
    premier_add_on_offer_name
  - Model TriggeredJobHistory no longer has parameter
    triggered_job_runs
  - Model ProcessInfo no longer has parameter total_processor_time
  - Model ProcessInfo no longer has parameter user_processor_time
  - Model ProcessInfo no longer has parameter
    peak_paged_memory_size64
  - Model ProcessInfo no longer has parameter
    privileged_processor_time
  - Model ProcessInfo no longer has parameter
    paged_system_memory_size64
  - Model ProcessInfo no longer has parameter process_info_name
  - Model ProcessInfo no longer has parameter peak_working_set64
  - Model ProcessInfo no longer has parameter virtual_memory_size64
  - Model ProcessInfo no longer has parameter mini_dump
  - Model ProcessInfo no longer has parameter is_web_job
  - Model ProcessInfo no longer has parameter private_memory_size64
  - Model ProcessInfo no longer has parameter
    nonpaged_system_memory_size64
  - Model ProcessInfo no longer has parameter working_set64
  - Model ProcessInfo no longer has parameter process_info_id
  - Model ProcessInfo no longer has parameter paged_memory_size64
  - Model ProcessInfo no longer has parameter
    peak_virtual_memory_size64
  - Model GeoRegion no longer has parameter geo_region_name
  - Model FunctionEnvelope no longer has parameter
    function_envelope_name
  - Model ProcessThreadInfo no longer has parameter
    process_thread_info_id
  - Model CloningInfo no longer has parameter ignore_quotas
  - Model AppServicePlan no longer has parameter
    app_service_plan_name
  - Model CertificatePatchResource no longer has parameter geo_region
  - Model WebJob no longer has parameter job_type
  - Model WebJob no longer has parameter web_job_name
  - Model Usage no longer has parameter usage_name
  - Model Deployment no longer has parameter deployment_id
  - Model Recommendation no longer has parameter tags
  - Model PremierAddOn no longer has parameter premier_add_on_tags
  - Model PremierAddOn no longer has parameter
    premier_add_on_location
  - Model PremierAddOn no longer has parameter premier_add_on_name
  - Model SlotDifference no longer has parameter slot_difference_type
  - Model ContinuousWebJob no longer has parameter
    continuous_web_job_name
  - Model ContinuousWebJob no longer has parameter job_type
  - Model TopLevelDomain no longer has parameter domain_name
  - Model AppServicePlanPatchResource no longer has parameter
    app_service_plan_patch_resource_name
  - Model MetricDefinition no longer has parameter
    metric_definition_name
  - Model PerfMonSample no longer has parameter core_count
  - Removed operation WebAppsOperations.recover
  - Removed operation WebAppsOperations.recover_slot
  - Removed operation
    WebAppsOperations.get_web_site_container_logs_zip
  - Removed operation
    WebAppsOperations.get_web_site_container_logs_zip_slot
  - Removed operation WebAppsOperations.discover_restore
  - Removed operation WebAppsOperations.discover_restore_slot
  - Model IpSecurityRestriction has a new signature

## 0.35.0 (2018-02-20)

**Breaking changes**

  - Many models signature changed to expose correctly required
    parameters. Example (non exhaustive) list:
      - AppServiceCertificateOrderPatchResource now requires
        product_type
      - AppServicePlanPatchResource now requires
        app_service_plan_patch_resource_name
      - CertificatePatchResource now requires password
      - DomainPatchResource now requires contact_admin,
        contact_billing, contact_registrant, contact_tech, consent
      - MigrateMySqlRequest now requires connection_string,
        migration_type
      - PushSettings now requires is_push_enabled
  - get_available_stacks now returns a pageable object

**Features**

  - Add certificate_registration_provider operations group
  - Add Diagnostics operations group
  - Add domain registration provider operations groups
  - All operations group have now a "models" attribute

## 0.34.1 (2017-10-24)

  - MSI fixes

## 0.34.0 (2017-10-16)

  - Add MSI support

## 0.33.0 (2017-10-04)

**Features**

  - Add providers.list_operations
  - Add verify_hosting_environment_vnet
  - Add web_apps.list_sync_function_triggers
  - Add web_apps.list_processes
  - Add web_apps.get_instance_process_module
  - Add web_apps.delete_process
  - Add web_apps.get_process_dump
  - Add web_apps continous web job operations
  - Add web_apps continous web job slots operations
  - Add web_apps public certificate operations
  - Add web_apps site_extension operations
  - Add web_apps functions operations
  - Add web_apps.list_function_secrets
  - Add web_apps.list_deployment_log
  - Add web_apps.list_deployment_log_slot
  - Add web_apps ms_deploy_status operations
  - Add web_apps ms_deploy_status_slot operations
  - Add web_apps ms_deploy_log_slot operations
  - Add web_apps instance_process_modules operations
  - Add web_apps instance_process_threads operations
  - Add web_apps instance_process_slot operations
  - Add web_apps instance_process_modules_slot operations
  - Add web_apps instance_process_threads_slot operations
  - Add web_apps.list_sync_function_triggers_slot
  - Add web_apps processes_slot operations
  - Add web_apps site_extensions_slot operations
  - Add web_apps triggered_web_jobs_slot operations
  - Add web_apps web_jobs_slot operations
  - Add web_apps triggered_web_jobs operations
  - Add web_apps web_jobs operations
  - Add web_apps.is_cloneable

**Breaking changes**

  - Remove 'name' and 'type' from several models (was ignored by server
    as read-only parameters)
  - Remove completely 'location' parameter from several models (None was
    the only acceptable value)
  - Remove a lot of incorrect parameter into DeletedSite
  - Remove deleted_web_apps.list_by_resource_group
  - Change web_apps.update_application_settings method signature
  - Change web_apps.update_connection_strings method signature
  - Change web_apps.update_metadata method signature
  - web_apps.recover now recover from a delete app to a previous
    snapshot
  - web_apps.recover_slot now recover from a delete app to a previous
    snapshot

## 0.32.0 (2017-04-26)

  - Support list web runtime stacks
  - Expose non resource based model type for SiteConfig,
    SiteAuthSettings, etc, to be used as property
  - Support list linux web available regions

## 0.31.1 (2017-04-20)

This wheel package is now built with the azure wheel extension

## 0.31.0 (2017-02-13)

  - Major refactoring and breaking changes
  - New API Version

## 0.30.0 (2016-10-17)

  - Initial release
