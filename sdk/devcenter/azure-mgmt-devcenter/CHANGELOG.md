# Release History

## 2.0.0b1 (2026-07-09)

### Features Added

  - Client `DevCenterMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Client `DevCenterMgmtClient` added method `send_request`
  - Client `DevCenterMgmtClient` added operation group `project_policies`
  - Client `DevCenterMgmtClient` added operation group `customization_tasks`
  - Client `DevCenterMgmtClient` added operation group `project_catalog_image_definitions`
  - Client `DevCenterMgmtClient` added operation group `project_catalog_image_definition_build`
  - Client `DevCenterMgmtClient` added operation group `encryption_sets`
  - Client `DevCenterMgmtClient` added operation group `dev_center_catalog_image_definitions`
  - Client `DevCenterMgmtClient` added operation group `dev_center_catalog_image_definition_build`
  - Client `DevCenterMgmtClient` added operation group `dev_center_catalog_image_definition_builds`
  - Client `DevCenterMgmtClient` added operation group `project_catalog_image_definition_builds`
  - Enum `CatalogItemType` added member `IMAGE_DEFINITION`
  - Model `CatalogProperties` added property `auto_image_build_enable_status`
  - Model `CatalogUpdateProperties` added property `auto_image_build_enable_status`
  - Model `CustomerManagedKeyEncryptionKeyIdentity` added property `federated_client_id`
  - Model `DevCenterProperties` added property `network_settings`
  - Model `DevCenterProperties` added property `dev_box_provisioning_settings`
  - Model `DevCenterUpdateProperties` added property `network_settings`
  - Model `DevCenterUpdateProperties` added property `dev_box_provisioning_settings`
  - Enum `DomainJoinType` added member `NONE`
  - Enum `HealthCheckStatus` added member `INFORMATIONAL`
  - Model `PoolProperties` added property `dev_box_definition_type`
  - Model `PoolProperties` added property `dev_box_definition`
  - Model `PoolProperties` added property `stop_on_no_connect`
  - Model `PoolProperties` added property `active_hours_configuration`
  - Model `PoolProperties` added property `dev_box_tunnel_enable_status`
  - Model `PoolUpdateProperties` added property `dev_box_definition_type`
  - Model `PoolUpdateProperties` added property `dev_box_definition`
  - Model `PoolUpdateProperties` added property `stop_on_no_connect`
  - Model `PoolUpdateProperties` added property `active_hours_configuration`
  - Model `PoolUpdateProperties` added property `dev_box_tunnel_enable_status`
  - Model `ProjectProperties` added property `customization_settings`
  - Model `ProjectProperties` added property `dev_box_schedule_delete_settings`
  - Model `ProjectProperties` added property `azure_ai_services_settings`
  - Model `ProjectProperties` added property `serverless_gpu_sessions_settings`
  - Model `ProjectProperties` added property `workspace_storage_settings`
  - Model `ProjectProperties` added property `assigned_groups`
  - Model `ProjectUpdateProperties` added property `customization_settings`
  - Model `ProjectUpdateProperties` added property `dev_box_schedule_delete_settings`
  - Model `ProjectUpdateProperties` added property `azure_ai_services_settings`
  - Model `ProjectUpdateProperties` added property `serverless_gpu_sessions_settings`
  - Model `ProjectUpdateProperties` added property `workspace_storage_settings`
  - Model `ProjectUpdateProperties` added property `assigned_groups`
  - Added model `ActiveHoursConfiguration`
  - Added enum `ArchitectureType`
  - Added model `AssignedGroup`
  - Added enum `AssignedGroupScope`
  - Added enum `AutoImageBuildStatus`
  - Added enum `AutoStartEnableStatus`
  - Added enum `AzureAiServicesMode`
  - Added model `AzureAiServicesSettings`
  - Added enum `CancelOnConnectEnableStatus`
  - Added enum `CatalogAutoImageBuildEnableStatus`
  - Added enum `CmkIdentityType`
  - Added model `ConfigurationPolicies`
  - Added model `CustomizationTask`
  - Added model `CustomizationTaskInput`
  - Added enum `CustomizationTaskInputType`
  - Added model `CustomizationTaskInstance`
  - Added model `CustomizationTaskProperties`
  - Added enum `DayOfWeek`
  - Added model `DefaultValue`
  - Added model `DefinitionParametersItem`
  - Added enum `DevBoxDeleteMode`
  - Added model `DevBoxProvisioningSettings`
  - Added model `DevBoxScheduleDeleteSettings`
  - Added enum `DevBoxTunnelEnableStatus`
  - Added model `DevCenterEncryptionSet`
  - Added model `DevCenterEncryptionSetProperties`
  - Added model `DevCenterEncryptionSetUpdateProperties`
  - Added model `DevCenterNetworkSettings`
  - Added enum `DevCenterResourceType`
  - Added enum `DevboxDisksEncryptionEnableStatus`
  - Added model `EncryptionSetUpdate`
  - Added model `FeatureState`
  - Added enum `FeatureStateModifiable`
  - Added enum `FeatureStatus`
  - Added model `ImageCreationErrorDetails`
  - Added model `ImageDefinition`
  - Added model `ImageDefinitionBuild`
  - Added model `ImageDefinitionBuildDetails`
  - Added model `ImageDefinitionBuildProperties`
  - Added enum `ImageDefinitionBuildStatus`
  - Added model `ImageDefinitionBuildTask`
  - Added model `ImageDefinitionBuildTaskGroup`
  - Added model `ImageDefinitionBuildTaskParametersItem`
  - Added model `ImageDefinitionProperties`
  - Added model `ImageDefinitionReference`
  - Added model `InheritedProjectCatalogSettings`
  - Added model `InheritedSettingsForProject`
  - Added enum `InstallAzureMonitorAgentEnableStatus`
  - Added enum `KeepAwakeEnableStatus`
  - Added model `KeyEncryptionKeyIdentityUpdate`
  - Added model `LatestImageBuild`
  - Added enum `MicrosoftHostedNetworkEnableStatus`
  - Added enum `PolicyAction`
  - Added model `PoolDevBoxDefinition`
  - Added enum `PoolDevBoxDefinitionType`
  - Added enum `ProjectCustomizationIdentityType`
  - Added model `ProjectCustomizationManagedIdentity`
  - Added model `ProjectCustomizationSettings`
  - Added model `ProjectNetworkSettings`
  - Added model `ProjectPolicy`
  - Added model `ProjectPolicyProperties`
  - Added model `ProjectPolicyUpdate`
  - Added model `ProjectPolicyUpdateProperties`
  - Added model `ResourcePolicy`
  - Added enum `ServerlessGpuSessionsMode`
  - Added model `ServerlessGpuSessionsSettings`
  - Added model `StopOnNoConnectConfiguration`
  - Added enum `StopOnNoConnectEnableStatus`
  - Added enum `UserCustomizationsEnableStatus`
  - Added enum `WorkspaceStorageMode`
  - Added model `WorkspaceStorageSettings`
  - Operation group `ImageVersionsOperations` added method `get_by_project`
  - Operation group `ImageVersionsOperations` added method `list_by_project`
  - Operation group `ImagesOperations` added method `get_by_project`
  - Operation group `ImagesOperations` added method `list_by_project`
  - Operation group `ProjectsOperations` added method `get_inherited_settings`
  - Operation group `SkusOperations` added method `list_by_project`
  - Added operation group `CustomizationTasksOperations`
  - Added operation group `DevCenterCatalogImageDefinitionBuildOperations`
  - Added operation group `DevCenterCatalogImageDefinitionBuildsOperations`
  - Added operation group `DevCenterCatalogImageDefinitionsOperations`
  - Added operation group `EncryptionSetsOperations`
  - Added operation group `ProjectCatalogImageDefinitionBuildOperations`
  - Added operation group `ProjectCatalogImageDefinitionBuildsOperations`
  - Added operation group `ProjectCatalogImageDefinitionsOperations`
  - Added operation group `ProjectPoliciesOperations`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - Model `AllowedEnvironmentType` moved instance variable `provisioning_state` and `display_name` under property `properties` whose type is `AllowedEnvironmentTypeProperties`
  - Model `AttachedNetworkConnection` moved instance variable `provisioning_state`, `network_connection_id`, `network_connection_location`, `health_check_status` and `domain_join_type` under property `properties` whose type is `AttachedNetworkConnectionProperties`
  - Model `Catalog` moved instance variable `git_hub`, `ado_git`, `sync_type`, `tags`, `provisioning_state`, `sync_state`, `last_sync_stats`, `connection_state`, `last_connection_time` and `last_sync_time` under property `properties` whose type is `CatalogProperties`
  - Model `CatalogUpdate` moved instance variable `git_hub`, `ado_git`, `sync_type` and `tags` under property `properties` whose type is `CatalogUpdateProperties`
  - Model `DevBoxDefinition` moved instance variable `image_reference`, `sku`, `os_storage_type`, `hibernate_support`, `provisioning_state`, `image_validation_status`, `image_validation_error_details`, `validation_status` and `active_image_reference` under property `properties` whose type is `DevBoxDefinitionProperties`
  - Model `DevBoxDefinitionUpdate` moved instance variable `image_reference`, `sku`, `os_storage_type` and `hibernate_support` under property `properties` whose type is `DevBoxDefinitionUpdateProperties`
  - Model `DevCenter` moved instance variable `encryption`, `display_name`, `project_catalog_settings`, `provisioning_state` and `dev_center_uri` under property `properties` whose type is `DevCenterProperties`
  - Model `DevCenterUpdate` moved instance variable `encryption`, `display_name` and `project_catalog_settings` under property `properties` whose type is `DevCenterUpdateProperties`
  - Model `EnvironmentDefinition` moved instance variable `description`, `parameters`, `template_path` and `validation_status` under property `properties` whose type is `EnvironmentDefinitionProperties`
  - Model `EnvironmentType` moved instance variable `display_name` and `provisioning_state` under property `properties` whose type is `EnvironmentTypeProperties`
  - Model `EnvironmentTypeUpdate` moved instance variable `display_name` under property `properties` whose type is `EnvironmentTypeUpdateProperties`
  - Model `Gallery` moved instance variable `provisioning_state` and `gallery_resource_id` under property `properties` whose type is `GalleryProperties`
  - Model `HealthCheckStatusDetails` moved instance variable `start_date_time`, `end_date_time` and `health_checks` under property `properties` whose type is `HealthCheckStatusDetailsProperties`
  - Model `Image` moved instance variable `description`, `publisher`, `offer`, `sku`, `recommended_machine_configuration`, `provisioning_state` and `hibernate_support` under property `properties` whose type is `ImageProperties`
  - Model `ImageVersion` moved instance variable `name_properties_name`, `published_date`, `exclude_from_latest`, `os_disk_image_size_in_gb` and `provisioning_state` under property `properties` whose type is `ImageVersionProperties`
  - Model `NetworkConnection` moved instance variable `subnet_id`, `domain_name`, `organization_unit`, `domain_username`, `domain_password`, `provisioning_state`, `health_check_status`, `networking_resource_group_name` and `domain_join_type` under property `properties` whose type is `NetworkProperties`
  - Model `NetworkConnectionUpdate` moved instance variable `subnet_id`, `domain_name`, `organization_unit`, `domain_username` and `domain_password` under property `properties` whose type is `NetworkConnectionUpdateProperties`
  - Model `Pool` moved instance variable `dev_box_definition_name`, `network_connection_name`, `license_type`, `local_administrator`, `stop_on_disconnect`, `single_sign_on_status`, `display_name`, `virtual_network_type`, `managed_virtual_network_regions`, `health_status`, `health_status_details`, `dev_box_count` and `provisioning_state` under property `properties` whose type is `PoolProperties`
  - Model `PoolUpdate` moved instance variable `dev_box_definition_name`, `network_connection_name`, `license_type`, `local_administrator`, `stop_on_disconnect`, `single_sign_on_status`, `display_name`, `virtual_network_type` and `managed_virtual_network_regions` under property `properties` whose type is `PoolUpdateProperties`
  - Model `Project` moved instance variable `dev_center_id`, `description`, `max_dev_boxes_per_user`, `display_name`, `catalog_settings`, `provisioning_state` and `dev_center_uri` under property `properties` whose type is `ProjectProperties`
  - Model `ProjectEnvironmentType` moved instance variable `deployment_target_id`, `display_name`, `status`, `creator_role_assignment`, `user_role_assignments`, `provisioning_state` and `environment_count` under property `properties` whose type is `ProjectEnvironmentTypeProperties`
  - Model `ProjectEnvironmentTypeUpdate` moved instance variable `deployment_target_id`, `display_name`, `status`, `creator_role_assignment` and `user_role_assignments` under property `properties` whose type is `ProjectEnvironmentTypeUpdateProperties`
  - Model `ProjectUpdate` moved instance variable `dev_center_id`, `description`, `max_dev_boxes_per_user`, `display_name` and `catalog_settings` under property `properties` whose type is `ProjectUpdateProperties`
  - Model `Schedule` moved instance variable `tags`, `location`, `type_properties_type`, `frequency`, `time`, `time_zone`, `state` and `provisioning_state` under property `properties` whose type is `ScheduleProperties`
  - Model `ScheduleUpdate` moved instance variable `tags`, `location`, `type`, `frequency`, `time`, `time_zone` and `state` under property `properties` whose type is `ScheduleUpdateProperties`

### Other Changes

  - Deleted model `AllowedEnvironmentTypeListResult`/`AttachedNetworkListResult`/`CatalogListResult`/`DevBoxDefinitionListResult`/`DevCenterListResult`/`EnvironmentDefinitionListResult`/`EnvironmentTypeListResult`/`GalleryListResult`/`HealthCheckStatusDetailsListResult`/`ImageListResult`/`ImageVersionListResult`/`ListUsagesResult`/`NetworkConnectionListResult`/`OperationListResult`/`OutboundEnvironmentEndpointCollection`/`PoolListResult`/`ProjectEnvironmentTypeListResult`/`ProjectListResult`/`ScheduleListResult`/`SkuListResult`/`TrackedResourceUpdate` which actually were not used by SDK users

## 1.1.0 (2024-04-22)

### Features Added

  - Added operation CatalogsOperations.begin_connect
  - Added operation CatalogsOperations.get_sync_error_details
  - Added operation group CheckScopedNameAvailabilityOperations
  - Added operation group EnvironmentDefinitionsOperations
  - Added operation group ProjectCatalogEnvironmentDefinitionsOperations
  - Added operation group ProjectCatalogsOperations
  - Model AllowedEnvironmentType has a new parameter display_name
  - Model Catalog has a new parameter connection_state
  - Model Catalog has a new parameter last_connection_time
  - Model Catalog has a new parameter last_sync_stats
  - Model Catalog has a new parameter sync_type
  - Model Catalog has a new parameter tags
  - Model CatalogProperties has a new parameter connection_state
  - Model CatalogProperties has a new parameter last_connection_time
  - Model CatalogProperties has a new parameter last_sync_stats
  - Model CatalogProperties has a new parameter sync_type
  - Model CatalogProperties has a new parameter tags
  - Model CatalogUpdate has a new parameter sync_type
  - Model CatalogUpdateProperties has a new parameter sync_type
  - Model CatalogUpdateProperties has a new parameter tags
  - Model DevBoxDefinition has a new parameter validation_status
  - Model DevBoxDefinitionProperties has a new parameter validation_status
  - Model DevCenter has a new parameter display_name
  - Model DevCenter has a new parameter encryption
  - Model DevCenter has a new parameter project_catalog_settings
  - Model DevCenterUpdate has a new parameter display_name
  - Model DevCenterUpdate has a new parameter encryption
  - Model DevCenterUpdate has a new parameter project_catalog_settings
  - Model EnvironmentType has a new parameter display_name
  - Model EnvironmentTypeUpdate has a new parameter display_name
  - Model OperationStatusResult has a new parameter resource_id
  - Model Pool has a new parameter dev_box_count
  - Model Pool has a new parameter display_name
  - Model Pool has a new parameter managed_virtual_network_regions
  - Model Pool has a new parameter single_sign_on_status
  - Model Pool has a new parameter virtual_network_type
  - Model PoolProperties has a new parameter dev_box_count
  - Model PoolProperties has a new parameter display_name
  - Model PoolProperties has a new parameter managed_virtual_network_regions
  - Model PoolProperties has a new parameter single_sign_on_status
  - Model PoolProperties has a new parameter virtual_network_type
  - Model PoolUpdate has a new parameter display_name
  - Model PoolUpdate has a new parameter managed_virtual_network_regions
  - Model PoolUpdate has a new parameter single_sign_on_status
  - Model PoolUpdate has a new parameter virtual_network_type
  - Model PoolUpdateProperties has a new parameter display_name
  - Model PoolUpdateProperties has a new parameter managed_virtual_network_regions
  - Model PoolUpdateProperties has a new parameter single_sign_on_status
  - Model PoolUpdateProperties has a new parameter virtual_network_type
  - Model Project has a new parameter catalog_settings
  - Model Project has a new parameter display_name
  - Model Project has a new parameter identity
  - Model ProjectEnvironmentType has a new parameter display_name
  - Model ProjectEnvironmentType has a new parameter environment_count
  - Model ProjectEnvironmentTypeProperties has a new parameter display_name
  - Model ProjectEnvironmentTypeProperties has a new parameter environment_count
  - Model ProjectEnvironmentTypeUpdate has a new parameter display_name
  - Model ProjectEnvironmentTypeUpdateProperties has a new parameter display_name
  - Model ProjectProperties has a new parameter catalog_settings
  - Model ProjectProperties has a new parameter display_name
  - Model ProjectUpdate has a new parameter catalog_settings
  - Model ProjectUpdate has a new parameter display_name
  - Model ProjectUpdate has a new parameter identity
  - Model ProjectUpdateProperties has a new parameter catalog_settings
  - Model ProjectUpdateProperties has a new parameter display_name
  - Model Schedule has a new parameter location
  - Model Schedule has a new parameter tags
  - Model ScheduleProperties has a new parameter location
  - Model ScheduleProperties has a new parameter tags
  - Model ScheduleUpdateProperties has a new parameter location
  - Model ScheduleUpdateProperties has a new parameter tags
  - Model Usage has a new parameter id

## 1.1.0b1 (2023-10-23)

### Features Added

  - Added operation CatalogsOperations.begin_connect
  - Added operation CatalogsOperations.get_sync_error_details
  - Added operation group CatalogDevBoxDefinitionsOperations
  - Added operation group CustomizationTasksOperations
  - Added operation group EnvironmentDefinitionsOperations
  - Model AllowedEnvironmentType has a new parameter display_name
  - Model Catalog has a new parameter connection_state
  - Model Catalog has a new parameter last_connection_time
  - Model Catalog has a new parameter last_sync_stats
  - Model Catalog has a new parameter sync_type
  - Model CatalogProperties has a new parameter connection_state
  - Model CatalogProperties has a new parameter last_connection_time
  - Model CatalogProperties has a new parameter last_sync_stats
  - Model CatalogProperties has a new parameter sync_type
  - Model CatalogUpdate has a new parameter sync_type
  - Model CatalogUpdateProperties has a new parameter sync_type
  - Model DevBoxDefinition has a new parameter validation_status
  - Model DevBoxDefinitionProperties has a new parameter validation_status
  - Model DevCenter has a new parameter display_name
  - Model DevCenter has a new parameter encryption
  - Model DevCenterUpdate has a new parameter display_name
  - Model DevCenterUpdate has a new parameter encryption
  - Model EnvironmentType has a new parameter display_name
  - Model EnvironmentTypeUpdate has a new parameter display_name
  - Model Pool has a new parameter dev_box_count
  - Model Pool has a new parameter display_name
  - Model Pool has a new parameter managed_virtual_network_regions
  - Model Pool has a new parameter single_sign_on_status
  - Model Pool has a new parameter virtual_network_type
  - Model PoolProperties has a new parameter dev_box_count
  - Model PoolProperties has a new parameter display_name
  - Model PoolProperties has a new parameter managed_virtual_network_regions
  - Model PoolProperties has a new parameter single_sign_on_status
  - Model PoolProperties has a new parameter virtual_network_type
  - Model PoolUpdate has a new parameter display_name
  - Model PoolUpdate has a new parameter managed_virtual_network_regions
  - Model PoolUpdate has a new parameter single_sign_on_status
  - Model PoolUpdate has a new parameter virtual_network_type
  - Model PoolUpdateProperties has a new parameter display_name
  - Model PoolUpdateProperties has a new parameter managed_virtual_network_regions
  - Model PoolUpdateProperties has a new parameter single_sign_on_status
  - Model PoolUpdateProperties has a new parameter virtual_network_type
  - Model Project has a new parameter display_name
  - Model ProjectEnvironmentType has a new parameter display_name
  - Model ProjectEnvironmentType has a new parameter environment_count
  - Model ProjectEnvironmentTypeProperties has a new parameter display_name
  - Model ProjectEnvironmentTypeProperties has a new parameter environment_count
  - Model ProjectProperties has a new parameter display_name
  - Model ProjectUpdate has a new parameter display_name
  - Model ProjectUpdateProperties has a new parameter display_name
  - Model Usage has a new parameter id

## 1.0.0 (2023-05-20)

### Features Added

  - Added operation NetworkConnectionsOperations.list_outbound_network_dependencies_endpoints
  - Added operation PoolsOperations.begin_run_health_checks
  - Model Image has a new parameter hibernate_support
  - Model Pool has a new parameter health_status
  - Model Pool has a new parameter health_status_details
  - Model Pool has a new parameter stop_on_disconnect
  - Model PoolProperties has a new parameter health_status
  - Model PoolProperties has a new parameter health_status_details
  - Model PoolProperties has a new parameter stop_on_disconnect
  - Model PoolUpdate has a new parameter stop_on_disconnect
  - Model PoolUpdateProperties has a new parameter stop_on_disconnect
  - Model Project has a new parameter max_dev_boxes_per_user
  - Model ProjectProperties has a new parameter max_dev_boxes_per_user
  - Model ProjectUpdate has a new parameter max_dev_boxes_per_user
  - Model ProjectUpdateProperties has a new parameter max_dev_boxes_per_user

### Breaking Changes

  - Model ImageReference no longer has parameter offer
  - Model ImageReference no longer has parameter publisher
  - Model ImageReference no longer has parameter sku

## 1.0.0b4 (2022-11-24)

### Features Added

  - Added operation group CheckNameAvailabilityOperations
  - Model DevBoxDefinition has a new parameter hibernate_support
  - Model DevBoxDefinitionProperties has a new parameter hibernate_support
  - Model DevBoxDefinitionUpdate has a new parameter hibernate_support
  - Model DevBoxDefinitionUpdateProperties has a new parameter hibernate_support
  - Model DevCenter has a new parameter dev_center_uri
  - Model Project has a new parameter dev_center_uri
  - Model ProjectProperties has a new parameter dev_center_uri

### Breaking Changes

  - Renamed operation NetworkConnectionsOperations.run_health_checks to NetworkConnectionsOperations.begin_run_health_checks

## 1.0.0b3 (2022-11-08)

### Features Added

  - Model Catalog has a new parameter sync_state
  - Model CatalogProperties has a new parameter sync_state
  - Model OperationStatus has a new parameter operations
  - Model OperationStatus has a new parameter resource_id

### Breaking Changes

  - Client name is changed from `DevCenterClient` to `DevCenterMgmtClient`
  - Parameter status of model OperationStatus is now required

## 1.0.0b2 (2022-09-29)

### Features Added

  - Added operation group ProjectAllowedEnvironmentTypesOperations

## 1.0.0b1 (2022-08-15)

* Initial Release
