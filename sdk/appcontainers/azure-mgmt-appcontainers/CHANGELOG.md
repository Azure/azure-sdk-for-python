# Release History

## 3.1.0 (2024-08-06)

### Features Added

  - The 'azure.mgmt.appcontainers.ContainerAppsAPIClient' client method 'get_custom_domain_verification_id' was added in the current version
  - The 'azure.mgmt.appcontainers.ContainerAppsAPIClient' client had operation group 'usages' added in the current version
  - The 'azure.mgmt.appcontainers.ContainerAppsAPIClient' client had operation group 'managed_environment_usages' added in the current version
  - The 'azure.mgmt.appcontainers.aio.ContainerAppsAPIClient' client method 'get_custom_domain_verification_id' was added in the current version
  - The 'azure.mgmt.appcontainers.aio.ContainerAppsAPIClient' client had operation group 'usages' added in the current version
  - The 'azure.mgmt.appcontainers.aio.ContainerAppsAPIClient' client had operation group 'managed_environment_usages' added in the current version
  - The 'azure.mgmt.appcontainers.aio.operations.ContainerAppsAPIClientOperationsMixin' method 'get_custom_domain_verification_id' was added in the current version
  - The 'azure.mgmt.appcontainers.aio.operations.JobsOperations' method 'get_detector' was added in the current version
  - The 'azure.mgmt.appcontainers.aio.operations.JobsOperations' method 'list_detectors' was added in the current version
  - The 'azure.mgmt.appcontainers.aio.operations.JobsOperations' method 'proxy_get' was added in the current version
  - The model or publicly exposed class 'azure.mgmt.appcontainers.aio.operations.ManagedEnvironmentUsagesOperations' was added in the current version
  - The model or publicly exposed class 'azure.mgmt.appcontainers.aio.operations.UsagesOperations' was added in the current version
  - The 'azure.mgmt.appcontainers.operations.ContainerAppsAPIClientOperationsMixin' method 'get_custom_domain_verification_id' was added in the current version
  - The 'azure.mgmt.appcontainers.operations.JobsOperations' method 'get_detector' was added in the current version
  - The 'azure.mgmt.appcontainers.operations.JobsOperations' method 'list_detectors' was added in the current version
  - The 'azure.mgmt.appcontainers.operations.JobsOperations' method 'proxy_get' was added in the current version
  - The model or publicly exposed class 'azure.mgmt.appcontainers.operations.ManagedEnvironmentUsagesOperations' was added in the current version
  - The model or publicly exposed class 'azure.mgmt.appcontainers.operations.UsagesOperations' was added in the current version
  - The model or publicly exposed class 'azure.mgmt.appcontainers.models.AuthConfig' had property 'encryption_settings' added in the current version
  - The model or publicly exposed class 'azure.mgmt.appcontainers.models.AvailableWorkloadProfileProperties' had property 'gpus' added in the current version
  - The model or publicly exposed class 'azure.mgmt.appcontainers.models.Ingress' had property 'additional_port_mappings' added in the current version
  - The model or publicly exposed class 'azure.mgmt.appcontainers.models.Login' had property 'token_store' added in the current version
  - The model or publicly exposed class 'azure.mgmt.appcontainers.models.ManagedEnvironment' had property 'peer_traffic_configuration' added in the current version
  - The model or publicly exposed class 'azure.mgmt.appcontainers.models.BlobStorageTokenStore' was added in the current version
  - The model or publicly exposed class 'azure.mgmt.appcontainers.models.EncryptionSettings' was added in the current version
  - The model or publicly exposed class 'azure.mgmt.appcontainers.models.IngressPortMapping' was added in the current version
  - The model or publicly exposed class 'azure.mgmt.appcontainers.models.ListUsagesResult' was added in the current version
  - The model or publicly exposed class 'azure.mgmt.appcontainers.models.ManagedEnvironmentPropertiesPeerTrafficConfiguration' was added in the current version
  - The model or publicly exposed class 'azure.mgmt.appcontainers.models.ManagedEnvironmentPropertiesPeerTrafficConfigurationEncryption' was added in the current version
  - The model or publicly exposed class 'azure.mgmt.appcontainers.models.TokenStore' was added in the current version
  - The model or publicly exposed class 'azure.mgmt.appcontainers.models.Usage' was added in the current version
  - The model or publicly exposed class 'azure.mgmt.appcontainers.models.UsageName' was added in the current version

## 3.1.0b1 (2024-03-18)

### Features Added

  - Added operation ContainerAppsAPIClientOperationsMixin.get_custom_domain_verification_id
  - Added operation JobsOperations.get_detector
  - Added operation JobsOperations.list_detectors
  - Added operation JobsOperations.proxy_get
  - Added operation group AppResiliencyOperations
  - Added operation group BuildAuthTokenOperations
  - Added operation group BuildersOperations
  - Added operation group BuildsByBuilderResourceOperations
  - Added operation group BuildsOperations
  - Added operation group DaprComponentResiliencyPoliciesOperations
  - Added operation group DaprSubscriptionsOperations
  - Added operation group DotNetComponentsOperations
  - Added operation group JavaComponentsOperations
  - Added operation group ManagedEnvironmentUsagesOperations
  - Added operation group UsagesOperations
  - Model AuthConfig has a new parameter encryption_settings
  - Model AvailableWorkloadProfileProperties has a new parameter gpus
  - Model CertificateProperties has a new parameter certificate_key_vault_properties
  - Model CertificateProperties has a new parameter certificate_type
  - Model CustomDomainConfiguration has a new parameter certificate_key_vault_properties
  - Model DaprComponent has a new parameter service_component_bind
  - Model GithubActionConfiguration has a new parameter build_environment_variables
  - Model Ingress has a new parameter additional_port_mappings
  - Model Ingress has a new parameter target_port_http_scheme
  - Model Job has a new parameter extended_location
  - Model JobPatchProperties has a new parameter extended_location
  - Model LogAnalyticsConfiguration has a new parameter dynamic_json_columns
  - Model Login has a new parameter token_store
  - Model ManagedEnvironment has a new parameter app_insights_configuration
  - Model ManagedEnvironment has a new parameter identity
  - Model ManagedEnvironment has a new parameter open_telemetry_configuration
  - Model ManagedEnvironmentStorageProperties has a new parameter nfs_azure_file
  - Model ServiceBind has a new parameter client_type
  - Model ServiceBind has a new parameter customized_keys

## 3.0.0 (2023-08-18)

### Features Added

  - Added operation ContainerAppsOperations.begin_start
  - Added operation ContainerAppsOperations.begin_stop
  - Added operation group ContainerAppsAPIClientOperationsMixin
  - Added operation group JobsExecutionsOperations
  - Added operation group JobsOperations
  - Added operation group ManagedCertificatesOperations
  - Model AvailableWorkloadProfileProperties has a new parameter category
  - Model AzureCredentials has a new parameter kind
  - Model Configuration has a new parameter service
  - Model ContainerApp has a new parameter managed_by
  - Model ContainerApp has a new parameter workload_profile_name
  - Model ContainerAppSecret has a new parameter identity
  - Model ContainerAppSecret has a new parameter key_vault_url
  - Model GithubActionConfiguration has a new parameter github_personal_access_token
  - Model Ingress has a new parameter sticky_sessions
  - Model ManagedEnvironment has a new parameter dapr_configuration
  - Model ManagedEnvironment has a new parameter infrastructure_resource_group
  - Model ManagedEnvironment has a new parameter keda_configuration
  - Model ManagedEnvironment has a new parameter peer_authentication
  - Model Replica has a new parameter init_containers
  - Model Replica has a new parameter running_state
  - Model Replica has a new parameter running_state_details
  - Model ReplicaContainer has a new parameter running_state
  - Model ReplicaContainer has a new parameter running_state_details
  - Model Revision has a new parameter running_state
  - Model Secret has a new parameter identity
  - Model Secret has a new parameter key_vault_url
  - Model Template has a new parameter service_binds
  - Model Template has a new parameter termination_grace_period_seconds
  - Model Volume has a new parameter mount_options
  - Model Volume has a new parameter secrets
  - Model VolumeMount has a new parameter sub_path

### Breaking Changes

  - Model AvailableWorkloadProfileProperties no longer has parameter billing_meter_category
  - Model ContainerApp no longer has parameter workload_profile_type
  - Model ManagedEnvironment no longer has parameter sku
  - Model VnetConfiguration no longer has parameter outbound_settings
  - Model VnetConfiguration no longer has parameter runtime_subnet_id
  - Model WorkloadProfile has a new required parameter name

## 3.0.0b1 (2023-05-20)

### Features Added

  - Added operation group JobsExecutionsOperations
  - Added operation group JobsOperations
  - Added operation group ManagedCertificatesOperations
  - Model AvailableWorkloadProfileProperties has a new parameter category
  - Model ContainerApp has a new parameter managed_by
  - Model ContainerApp has a new parameter workload_profile_name
  - Model ContainerAppSecret has a new parameter identity
  - Model ContainerAppSecret has a new parameter key_vault_url
  - Model Ingress has a new parameter sticky_sessions
  - Model ManagedEnvironment has a new parameter dapr_configuration
  - Model ManagedEnvironment has a new parameter infrastructure_resource_group
  - Model ManagedEnvironment has a new parameter keda_configuration
  - Model Secret has a new parameter identity
  - Model Secret has a new parameter key_vault_url
  - Model Volume has a new parameter secrets

### Breaking Changes

  - Model AvailableWorkloadProfileProperties no longer has parameter billing_meter_category
  - Model ContainerApp no longer has parameter workload_profile_type
  - Model ManagedEnvironment no longer has parameter sku
  - Model VnetConfiguration no longer has parameter outbound_settings
  - Model VnetConfiguration no longer has parameter runtime_subnet_id
  - Model WorkloadProfile has a new required parameter name

## 2.0.0 (2023-03-20)

### Features Added

  - Added operation ContainerAppsOperations.get_auth_token
  - Added operation ManagedEnvironmentsOperations.get_auth_token
  - Added operation ManagedEnvironmentsOperations.list_workload_profile_states
  - Added operation group AvailableWorkloadProfilesOperations
  - Added operation group BillingMetersOperations
  - Added operation group ConnectedEnvironmentsCertificatesOperations
  - Added operation group ConnectedEnvironmentsDaprComponentsOperations
  - Added operation group ConnectedEnvironmentsOperations
  - Added operation group ConnectedEnvironmentsStoragesOperations
  - Added operation group ContainerAppsDiagnosticsOperations
  - Added operation group ManagedEnvironmentDiagnosticsOperations
  - Added operation group ManagedEnvironmentsDiagnosticsOperations
  - Model CertificateProperties has a new parameter subject_alternative_names
  - Model Configuration has a new parameter max_inactive_revisions
  - Model ContainerApp has a new parameter environment_id
  - Model ContainerApp has a new parameter event_stream_endpoint
  - Model ContainerApp has a new parameter extended_location
  - Model ContainerApp has a new parameter latest_ready_revision_name
  - Model ContainerApp has a new parameter workload_profile_type
  - Model CustomHostnameAnalysisResult has a new parameter conflict_with_environment_custom_domain
  - Model Dapr has a new parameter enable_api_logging
  - Model Dapr has a new parameter http_max_request_size
  - Model Dapr has a new parameter http_read_buffer_size
  - Model Dapr has a new parameter log_level
  - Model DaprComponent has a new parameter secret_store_component
  - Model Ingress has a new parameter client_certificate_mode
  - Model Ingress has a new parameter cors_policy
  - Model Ingress has a new parameter exposed_port
  - Model Ingress has a new parameter ip_security_restrictions
  - Model ManagedEnvironment has a new parameter custom_domain_configuration
  - Model ManagedEnvironment has a new parameter event_stream_endpoint
  - Model ManagedEnvironment has a new parameter kind
  - Model ManagedEnvironment has a new parameter sku
  - Model ManagedEnvironment has a new parameter workload_profiles
  - Model ReplicaContainer has a new parameter exec_endpoint
  - Model ReplicaContainer has a new parameter log_stream_endpoint
  - Model Revision has a new parameter last_active_time
  - Model ScaleRule has a new parameter tcp
  - Model Template has a new parameter init_containers
  - Model VnetConfiguration has a new parameter outbound_settings

### Breaking Changes

  - Model CustomHostnameAnalysisResult no longer has parameter id
  - Model CustomHostnameAnalysisResult no longer has parameter name
  - Model CustomHostnameAnalysisResult no longer has parameter system_data
  - Model CustomHostnameAnalysisResult no longer has parameter type

## 2.0.0b2 (2022-12-29)

### Features Added

  - Added operation ContainerAppsOperations.get_auth_token
  - Added operation ManagedEnvironmentsOperations.get_auth_token
  - Added operation ManagedEnvironmentsOperations.list_workload_profile_states
  - Added operation group AvailableWorkloadProfilesOperations
  - Added operation group BillingMetersOperations
  - Added operation group ConnectedEnvironmentsCertificatesOperations
  - Added operation group ConnectedEnvironmentsDaprComponentsOperations
  - Added operation group ConnectedEnvironmentsOperations
  - Added operation group ConnectedEnvironmentsStoragesOperations
  - Added operation group ContainerAppsDiagnosticsOperations
  - Added operation group ManagedEnvironmentDiagnosticsOperations
  - Added operation group ManagedEnvironmentsDiagnosticsOperations
  - Model CertificateProperties has a new parameter subject_alternative_names
  - Model Configuration has a new parameter max_inactive_revisions
  - Model ContainerApp has a new parameter environment_id
  - Model ContainerApp has a new parameter event_stream_endpoint
  - Model ContainerApp has a new parameter extended_location
  - Model ContainerApp has a new parameter latest_ready_revision_name
  - Model ContainerApp has a new parameter workload_profile_type
  - Model CustomHostnameAnalysisResult has a new parameter conflict_with_environment_custom_domain
  - Model Dapr has a new parameter enable_api_logging
  - Model Dapr has a new parameter http_max_request_size
  - Model Dapr has a new parameter http_read_buffer_size
  - Model Dapr has a new parameter log_level
  - Model DaprComponent has a new parameter secret_store_component
  - Model Ingress has a new parameter client_certificate_mode
  - Model Ingress has a new parameter cors_policy
  - Model Ingress has a new parameter exposed_port
  - Model Ingress has a new parameter ip_security_restrictions
  - Model ManagedEnvironment has a new parameter custom_domain_configuration
  - Model ManagedEnvironment has a new parameter event_stream_endpoint
  - Model ManagedEnvironment has a new parameter kind
  - Model ManagedEnvironment has a new parameter sku
  - Model ManagedEnvironment has a new parameter workload_profiles
  - Model ReplicaContainer has a new parameter exec_endpoint
  - Model ReplicaContainer has a new parameter log_stream_endpoint
  - Model Revision has a new parameter last_active_time
  - Model ScaleRule has a new parameter tcp
  - Model Template has a new parameter init_containers
  - Model VnetConfiguration has a new parameter outbound_settings

### Breaking Changes

  - Model CustomHostnameAnalysisResult no longer has parameter id
  - Model CustomHostnameAnalysisResult no longer has parameter name
  - Model CustomHostnameAnalysisResult no longer has parameter system_data
  - Model CustomHostnameAnalysisResult no longer has parameter type

## 2.0.0b1 (2022-10-12)

### Features Added

  - Added operation ContainerAppsOperations.get_auth_token
  - Added operation ManagedEnvironmentsOperations.get_auth_token
  - Added operation ManagedEnvironmentsOperations.list_workload_profile_states
  - Added operation group AvailableWorkloadProfilesOperations
  - Added operation group BillingMetersOperations
  - Added operation group ConnectedEnvironmentsCertificatesOperations
  - Added operation group ConnectedEnvironmentsDaprComponentsOperations
  - Added operation group ConnectedEnvironmentsOperations
  - Added operation group ConnectedEnvironmentsStoragesOperations
  - Added operation group ContainerAppsDiagnosticsOperations
  - Added operation group ManagedEnvironmentDiagnosticsOperations
  - Added operation group ManagedEnvironmentsDiagnosticsOperations
  - Model CertificateProperties has a new parameter subject_alternative_names
  - Model Configuration has a new parameter max_inactive_revisions
  - Model ContainerApp has a new parameter environment_id
  - Model ContainerApp has a new parameter event_stream_endpoint
  - Model ContainerApp has a new parameter extended_location
  - Model ContainerApp has a new parameter workload_profile_type
  - Model CustomHostnameAnalysisResult has a new parameter conflict_with_environment_custom_domain
  - Model Dapr has a new parameter enable_api_logging
  - Model Dapr has a new parameter http_max_request_size
  - Model Dapr has a new parameter http_read_buffer_size
  - Model Dapr has a new parameter log_level
  - Model DaprComponent has a new parameter secret_store_component
  - Model Ingress has a new parameter exposed_port
  - Model Ingress has a new parameter ip_security_restrictions
  - Model ManagedEnvironment has a new parameter custom_domain_configuration
  - Model ManagedEnvironment has a new parameter event_stream_endpoint
  - Model ManagedEnvironment has a new parameter sku
  - Model ManagedEnvironment has a new parameter workload_profiles
  - Model ReplicaContainer has a new parameter exec_endpoint
  - Model ReplicaContainer has a new parameter log_stream_endpoint
  - Model Revision has a new parameter last_active_time
  - Model ScaleRule has a new parameter tcp
  - Model Template has a new parameter init_containers
  - Model VnetConfiguration has a new parameter outbound_settings

### Breaking Changes

  - Model CustomHostnameAnalysisResult no longer has parameter id
  - Model CustomHostnameAnalysisResult no longer has parameter name
  - Model CustomHostnameAnalysisResult no longer has parameter system_data
  - Model CustomHostnameAnalysisResult no longer has parameter type

## 1.0.0 (2022-05-17)

**Breaking changes**

  - Operation CertificatesOperations.create_or_update has a new parameter certificate_name
  - Operation CertificatesOperations.create_or_update has a new parameter environment_name
  - Operation CertificatesOperations.create_or_update no longer has parameter managed_environment_name
  - Operation CertificatesOperations.create_or_update no longer has parameter name
  - Operation CertificatesOperations.delete has a new parameter certificate_name
  - Operation CertificatesOperations.delete has a new parameter environment_name
  - Operation CertificatesOperations.delete no longer has parameter managed_environment_name
  - Operation CertificatesOperations.delete no longer has parameter name
  - Operation CertificatesOperations.get has a new parameter certificate_name
  - Operation CertificatesOperations.get has a new parameter environment_name
  - Operation CertificatesOperations.get no longer has parameter managed_environment_name
  - Operation CertificatesOperations.get no longer has parameter name
  - Operation CertificatesOperations.list has a new parameter environment_name
  - Operation CertificatesOperations.list no longer has parameter managed_environment_name
  - Operation CertificatesOperations.update has a new parameter certificate_name
  - Operation CertificatesOperations.update has a new parameter environment_name
  - Operation CertificatesOperations.update no longer has parameter managed_environment_name
  - Operation CertificatesOperations.update no longer has parameter name
  - Operation ContainerAppsAuthConfigsOperations.create_or_update has a new parameter auth_config_name
  - Operation ContainerAppsAuthConfigsOperations.create_or_update no longer has parameter name
  - Operation ContainerAppsAuthConfigsOperations.delete has a new parameter auth_config_name
  - Operation ContainerAppsAuthConfigsOperations.delete no longer has parameter name
  - Operation ContainerAppsAuthConfigsOperations.get has a new parameter auth_config_name
  - Operation ContainerAppsAuthConfigsOperations.get no longer has parameter name
  - Operation ContainerAppsOperations.begin_create_or_update has a new parameter container_app_name
  - Operation ContainerAppsOperations.begin_create_or_update no longer has parameter name
  - Operation ContainerAppsOperations.begin_delete has a new parameter container_app_name
  - Operation ContainerAppsOperations.begin_delete no longer has parameter name
  - Operation ContainerAppsOperations.begin_update has a new parameter container_app_name
  - Operation ContainerAppsOperations.begin_update no longer has parameter name
  - Operation ContainerAppsOperations.get has a new parameter container_app_name
  - Operation ContainerAppsOperations.get no longer has parameter name
  - Operation ContainerAppsOperations.list_secrets has a new parameter container_app_name
  - Operation ContainerAppsOperations.list_secrets no longer has parameter name
  - Operation ContainerAppsRevisionReplicasOperations.get_replica has a new parameter replica_name
  - Operation ContainerAppsRevisionReplicasOperations.get_replica no longer has parameter name
  - Operation ContainerAppsRevisionsOperations.activate_revision has a new parameter revision_name
  - Operation ContainerAppsRevisionsOperations.activate_revision no longer has parameter name
  - Operation ContainerAppsRevisionsOperations.deactivate_revision has a new parameter revision_name
  - Operation ContainerAppsRevisionsOperations.deactivate_revision no longer has parameter name
  - Operation ContainerAppsRevisionsOperations.get_revision has a new parameter revision_name
  - Operation ContainerAppsRevisionsOperations.get_revision no longer has parameter name
  - Operation ContainerAppsRevisionsOperations.restart_revision has a new parameter revision_name
  - Operation ContainerAppsRevisionsOperations.restart_revision no longer has parameter name
  - Operation ContainerAppsSourceControlsOperations.begin_create_or_update has a new parameter source_control_name
  - Operation ContainerAppsSourceControlsOperations.begin_create_or_update no longer has parameter name
  - Operation ContainerAppsSourceControlsOperations.begin_delete has a new parameter source_control_name
  - Operation ContainerAppsSourceControlsOperations.begin_delete no longer has parameter name
  - Operation ContainerAppsSourceControlsOperations.get has a new parameter source_control_name
  - Operation ContainerAppsSourceControlsOperations.get no longer has parameter name
  - Operation DaprComponentsOperations.create_or_update has a new parameter component_name
  - Operation DaprComponentsOperations.create_or_update no longer has parameter name
  - Operation DaprComponentsOperations.delete has a new parameter component_name
  - Operation DaprComponentsOperations.delete no longer has parameter name
  - Operation DaprComponentsOperations.get has a new parameter component_name
  - Operation DaprComponentsOperations.get no longer has parameter name
  - Operation DaprComponentsOperations.list_secrets has a new parameter component_name
  - Operation DaprComponentsOperations.list_secrets no longer has parameter name
  - Operation ManagedEnvironmentsOperations.begin_create_or_update has a new parameter environment_name
  - Operation ManagedEnvironmentsOperations.begin_create_or_update no longer has parameter name
  - Operation ManagedEnvironmentsOperations.begin_delete has a new parameter environment_name
  - Operation ManagedEnvironmentsOperations.begin_delete no longer has parameter name
  - Operation ManagedEnvironmentsOperations.begin_update has a new parameter environment_name
  - Operation ManagedEnvironmentsOperations.begin_update no longer has parameter name
  - Operation ManagedEnvironmentsOperations.get has a new parameter environment_name
  - Operation ManagedEnvironmentsOperations.get no longer has parameter name
  - Operation ManagedEnvironmentsStoragesOperations.create_or_update has a new parameter environment_name
  - Operation ManagedEnvironmentsStoragesOperations.create_or_update has a new parameter storage_name
  - Operation ManagedEnvironmentsStoragesOperations.create_or_update no longer has parameter env_name
  - Operation ManagedEnvironmentsStoragesOperations.create_or_update no longer has parameter name
  - Operation ManagedEnvironmentsStoragesOperations.delete has a new parameter environment_name
  - Operation ManagedEnvironmentsStoragesOperations.delete has a new parameter storage_name
  - Operation ManagedEnvironmentsStoragesOperations.delete no longer has parameter env_name
  - Operation ManagedEnvironmentsStoragesOperations.delete no longer has parameter name
  - Operation ManagedEnvironmentsStoragesOperations.get has a new parameter environment_name
  - Operation ManagedEnvironmentsStoragesOperations.get has a new parameter storage_name
  - Operation ManagedEnvironmentsStoragesOperations.get no longer has parameter env_name
  - Operation ManagedEnvironmentsStoragesOperations.get no longer has parameter name
  - Operation ManagedEnvironmentsStoragesOperations.list has a new parameter environment_name
  - Operation ManagedEnvironmentsStoragesOperations.list no longer has parameter env_name
  - Operation NamespacesOperations.check_name_availability has a new parameter environment_name
  - Operation NamespacesOperations.check_name_availability no longer has parameter managed_environment_name

## 1.0.0b1 (2022-05-06)

* Initial Release
