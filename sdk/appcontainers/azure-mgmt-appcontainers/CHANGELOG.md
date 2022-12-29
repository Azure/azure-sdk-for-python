# Release History

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
