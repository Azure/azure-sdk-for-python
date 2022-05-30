# Release History

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
