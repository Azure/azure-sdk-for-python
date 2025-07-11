# Release History

## 10.0.0 (2025-07-08)

### Features Added

  - Model `DtlEnvironment` added property `properties`
  - Enum `HttpStatusCode` added member `AMBIGUOUS`
  - Enum `HttpStatusCode` added member `CONTINUE`
  - Enum `HttpStatusCode` added member `FOUND`
  - Enum `HttpStatusCode` added member `MOVED`
  - Enum `HttpStatusCode` added member `REDIRECT_KEEP_VERB`
  - Enum `HttpStatusCode` added member `REDIRECT_METHOD`
  - Enum `SourceControlType` added member `STORAGE_ACCOUNT`
  - Added enum `ActionType`
  - Added model `EnvironmentProperties`
  - Added model `ErrorAdditionalInfo`
  - Added model `ErrorDetail`
  - Added model `ErrorResponse`
  - Added enum `ManagedIdentityType`
  - Added model `OkResponse`
  - Added model `Operation`
  - Added model `OperationDisplay`
  - Added enum `Origin`
  - Model `ArmTemplatesOperations` added parameter `kwargs` in method `__init__`
  - Model `ArtifactSourcesOperations` added parameter `kwargs` in method `__init__`
  - Model `ArtifactsOperations` added parameter `kwargs` in method `__init__`
  - Model `CostsOperations` added parameter `kwargs` in method `__init__`
  - Model `CustomImagesOperations` added parameter `kwargs` in method `__init__`
  - Model `DisksOperations` added parameter `kwargs` in method `__init__`
  - Model `EnvironmentsOperations` added parameter `kwargs` in method `__init__`
  - Model `FormulasOperations` added parameter `kwargs` in method `__init__`
  - Model `GalleryImagesOperations` added parameter `kwargs` in method `__init__`
  - Model `GlobalSchedulesOperations` added parameter `kwargs` in method `__init__`
  - Model `LabsOperations` added parameter `kwargs` in method `__init__`
  - Model `NotificationChannelsOperations` added parameter `kwargs` in method `__init__`
  - Model `Operations` added parameter `kwargs` in method `__init__`
  - Model `PoliciesOperations` added parameter `kwargs` in method `__init__`
  - Model `PolicySetsOperations` added parameter `kwargs` in method `__init__`
  - Model `ProviderOperationsOperations` added parameter `kwargs` in method `__init__`
  - Model `SchedulesOperations` added parameter `kwargs` in method `__init__`
  - Model `SecretsOperations` added parameter `kwargs` in method `__init__`
  - Model `ServiceFabricSchedulesOperations` added parameter `kwargs` in method `__init__`
  - Model `ServiceFabricsOperations` added parameter `kwargs` in method `__init__`
  - Model `ServiceRunnersOperations` added parameter `kwargs` in method `__init__`
  - Model `UsersOperations` added parameter `kwargs` in method `__init__`
  - Model `VirtualMachineSchedulesOperations` added parameter `kwargs` in method `__init__`
  - Model `VirtualMachinesOperations` added parameter `kwargs` in method `__init__`
  - Model `VirtualNetworksOperations` added parameter `kwargs` in method `__init__`

### Breaking Changes

  - Deleted or renamed client `DevTestLabsClient`
  - Model `ApplicableSchedule` deleted or renamed its instance variable `lab_vms_shutdown`
  - Model `ApplicableSchedule` deleted or renamed its instance variable `lab_vms_startup`
  - Model `ArmTemplate` deleted or renamed its instance variable `display_name`
  - Model `ArmTemplate` deleted or renamed its instance variable `description`
  - Model `ArmTemplate` deleted or renamed its instance variable `publisher`
  - Model `ArmTemplate` deleted or renamed its instance variable `icon`
  - Model `ArmTemplate` deleted or renamed its instance variable `contents`
  - Model `ArmTemplate` deleted or renamed its instance variable `created_date`
  - Model `ArmTemplate` deleted or renamed its instance variable `parameters_value_files_info`
  - Model `ArmTemplate` deleted or renamed its instance variable `enabled`
  - Model `Artifact` deleted or renamed its instance variable `title`
  - Model `Artifact` deleted or renamed its instance variable `description`
  - Model `Artifact` deleted or renamed its instance variable `publisher`
  - Model `Artifact` deleted or renamed its instance variable `file_path`
  - Model `Artifact` deleted or renamed its instance variable `icon`
  - Model `Artifact` deleted or renamed its instance variable `target_os_type`
  - Model `Artifact` deleted or renamed its instance variable `parameters`
  - Model `Artifact` deleted or renamed its instance variable `created_date`
  - Model `ArtifactSource` deleted or renamed its instance variable `display_name`
  - Model `ArtifactSource` deleted or renamed its instance variable `uri`
  - Model `ArtifactSource` deleted or renamed its instance variable `source_type`
  - Model `ArtifactSource` deleted or renamed its instance variable `folder_path`
  - Model `ArtifactSource` deleted or renamed its instance variable `arm_template_folder_path`
  - Model `ArtifactSource` deleted or renamed its instance variable `branch_ref`
  - Model `ArtifactSource` deleted or renamed its instance variable `security_token`
  - Model `ArtifactSource` deleted or renamed its instance variable `status`
  - Model `ArtifactSource` deleted or renamed its instance variable `created_date`
  - Model `ArtifactSource` deleted or renamed its instance variable `provisioning_state`
  - Model `ArtifactSource` deleted or renamed its instance variable `unique_identifier`
  - Model `CustomImage` deleted or renamed its instance variable `vm`
  - Model `CustomImage` deleted or renamed its instance variable `vhd`
  - Model `CustomImage` deleted or renamed its instance variable `description`
  - Model `CustomImage` deleted or renamed its instance variable `author`
  - Model `CustomImage` deleted or renamed its instance variable `creation_date`
  - Model `CustomImage` deleted or renamed its instance variable `managed_image_id`
  - Model `CustomImage` deleted or renamed its instance variable `managed_snapshot_id`
  - Model `CustomImage` deleted or renamed its instance variable `data_disk_storage_info`
  - Model `CustomImage` deleted or renamed its instance variable `custom_image_plan`
  - Model `CustomImage` deleted or renamed its instance variable `is_plan_authorized`
  - Model `CustomImage` deleted or renamed its instance variable `provisioning_state`
  - Model `CustomImage` deleted or renamed its instance variable `unique_identifier`
  - Model `Disk` deleted or renamed its instance variable `disk_type`
  - Model `Disk` deleted or renamed its instance variable `disk_size_gi_b`
  - Model `Disk` deleted or renamed its instance variable `leased_by_lab_vm_id`
  - Model `Disk` deleted or renamed its instance variable `disk_blob_name`
  - Model `Disk` deleted or renamed its instance variable `disk_uri`
  - Model `Disk` deleted or renamed its instance variable `storage_account_id`
  - Model `Disk` deleted or renamed its instance variable `created_date`
  - Model `Disk` deleted or renamed its instance variable `host_caching`
  - Model `Disk` deleted or renamed its instance variable `managed_disk_id`
  - Model `Disk` deleted or renamed its instance variable `provisioning_state`
  - Model `Disk` deleted or renamed its instance variable `unique_identifier`
  - Model `DtlEnvironment` deleted or renamed its instance variable `deployment_properties`
  - Model `DtlEnvironment` deleted or renamed its instance variable `arm_template_display_name`
  - Model `DtlEnvironment` deleted or renamed its instance variable `resource_group_id`
  - Model `DtlEnvironment` deleted or renamed its instance variable `created_by_user`
  - Model `DtlEnvironment` deleted or renamed its instance variable `provisioning_state`
  - Model `DtlEnvironment` deleted or renamed its instance variable `unique_identifier`
  - Model `Formula` deleted or renamed its instance variable `description`
  - Model `Formula` deleted or renamed its instance variable `author`
  - Model `Formula` deleted or renamed its instance variable `os_type`
  - Model `Formula` deleted or renamed its instance variable `creation_date`
  - Model `Formula` deleted or renamed its instance variable `formula_content`
  - Model `Formula` deleted or renamed its instance variable `vm`
  - Model `Formula` deleted or renamed its instance variable `provisioning_state`
  - Model `Formula` deleted or renamed its instance variable `unique_identifier`
  - Model `GalleryImage` deleted or renamed its instance variable `author`
  - Model `GalleryImage` deleted or renamed its instance variable `created_date`
  - Model `GalleryImage` deleted or renamed its instance variable `description`
  - Model `GalleryImage` deleted or renamed its instance variable `image_reference`
  - Model `GalleryImage` deleted or renamed its instance variable `icon`
  - Model `GalleryImage` deleted or renamed its instance variable `enabled`
  - Model `GalleryImage` deleted or renamed its instance variable `plan_id`
  - Model `GalleryImage` deleted or renamed its instance variable `is_plan_authorized`
  - Model `Lab` deleted or renamed its instance variable `default_storage_account`
  - Model `Lab` deleted or renamed its instance variable `default_premium_storage_account`
  - Model `Lab` deleted or renamed its instance variable `artifacts_storage_account`
  - Model `Lab` deleted or renamed its instance variable `premium_data_disk_storage_account`
  - Model `Lab` deleted or renamed its instance variable `vault_name`
  - Model `Lab` deleted or renamed its instance variable `lab_storage_type`
  - Model `Lab` deleted or renamed its instance variable `mandatory_artifacts_resource_ids_linux`
  - Model `Lab` deleted or renamed its instance variable `mandatory_artifacts_resource_ids_windows`
  - Model `Lab` deleted or renamed its instance variable `created_date`
  - Model `Lab` deleted or renamed its instance variable `premium_data_disks`
  - Model `Lab` deleted or renamed its instance variable `environment_permission`
  - Model `Lab` deleted or renamed its instance variable `announcement`
  - Model `Lab` deleted or renamed its instance variable `support`
  - Model `Lab` deleted or renamed its instance variable `vm_creation_resource_group`
  - Model `Lab` deleted or renamed its instance variable `public_ip_id`
  - Model `Lab` deleted or renamed its instance variable `load_balancer_id`
  - Model `Lab` deleted or renamed its instance variable `network_security_group_id`
  - Model `Lab` deleted or renamed its instance variable `extended_properties`
  - Model `Lab` deleted or renamed its instance variable `provisioning_state`
  - Model `Lab` deleted or renamed its instance variable `unique_identifier`
  - Model `LabCost` deleted or renamed its instance variable `target_cost`
  - Model `LabCost` deleted or renamed its instance variable `lab_cost_summary`
  - Model `LabCost` deleted or renamed its instance variable `lab_cost_details`
  - Model `LabCost` deleted or renamed its instance variable `resource_costs`
  - Model `LabCost` deleted or renamed its instance variable `currency_code`
  - Model `LabCost` deleted or renamed its instance variable `start_date_time`
  - Model `LabCost` deleted or renamed its instance variable `end_date_time`
  - Model `LabCost` deleted or renamed its instance variable `created_date`
  - Model `LabCost` deleted or renamed its instance variable `provisioning_state`
  - Model `LabCost` deleted or renamed its instance variable `unique_identifier`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `notes`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `owner_object_id`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `owner_user_principal_name`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `created_by_user_id`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `created_by_user`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `created_date`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `compute_id`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `custom_image_id`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `os_type`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `size`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `user_name`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `password`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `ssh_key`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `is_authentication_with_ssh_key`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `fqdn`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `lab_subnet_name`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `lab_virtual_network_id`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `disallow_public_ip_address`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `artifacts`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `artifact_deployment_status`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `gallery_image_reference`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `plan_id`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `compute_vm`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `network_interface`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `applicable_schedule`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `expiration_date`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `allow_claim`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `storage_type`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `virtual_machine_creation_source`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `environment_id`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `data_disk_parameters`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `schedule_parameters`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `last_known_power_state`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `provisioning_state`
  - Model `LabVirtualMachine` deleted or renamed its instance variable `unique_identifier`
  - Model `LabVirtualMachineCreationParameter` deleted or renamed its instance variable `bulk_creation_parameters`
  - Model `LabVirtualMachineCreationParameter` deleted or renamed its instance variable `notes`
  - Model `LabVirtualMachineCreationParameter` deleted or renamed its instance variable `owner_object_id`
  - Model `LabVirtualMachineCreationParameter` deleted or renamed its instance variable `owner_user_principal_name`
  - Model `LabVirtualMachineCreationParameter` deleted or renamed its instance variable `created_date`
  - Model `LabVirtualMachineCreationParameter` deleted or renamed its instance variable `custom_image_id`
  - Model `LabVirtualMachineCreationParameter` deleted or renamed its instance variable `size`
  - Model `LabVirtualMachineCreationParameter` deleted or renamed its instance variable `user_name`
  - Model `LabVirtualMachineCreationParameter` deleted or renamed its instance variable `password`
  - Model `LabVirtualMachineCreationParameter` deleted or renamed its instance variable `ssh_key`
  - Model `LabVirtualMachineCreationParameter` deleted or renamed its instance variable `is_authentication_with_ssh_key`
  - Model `LabVirtualMachineCreationParameter` deleted or renamed its instance variable `lab_subnet_name`
  - Model `LabVirtualMachineCreationParameter` deleted or renamed its instance variable `lab_virtual_network_id`
  - Model `LabVirtualMachineCreationParameter` deleted or renamed its instance variable `disallow_public_ip_address`
  - Model `LabVirtualMachineCreationParameter` deleted or renamed its instance variable `artifacts`
  - Model `LabVirtualMachineCreationParameter` deleted or renamed its instance variable `gallery_image_reference`
  - Model `LabVirtualMachineCreationParameter` deleted or renamed its instance variable `plan_id`
  - Model `LabVirtualMachineCreationParameter` deleted or renamed its instance variable `network_interface`
  - Model `LabVirtualMachineCreationParameter` deleted or renamed its instance variable `expiration_date`
  - Model `LabVirtualMachineCreationParameter` deleted or renamed its instance variable `allow_claim`
  - Model `LabVirtualMachineCreationParameter` deleted or renamed its instance variable `storage_type`
  - Model `LabVirtualMachineCreationParameter` deleted or renamed its instance variable `environment_id`
  - Model `LabVirtualMachineCreationParameter` deleted or renamed its instance variable `data_disk_parameters`
  - Model `LabVirtualMachineCreationParameter` deleted or renamed its instance variable `schedule_parameters`
  - Model `NotificationChannel` deleted or renamed its instance variable `web_hook_url`
  - Model `NotificationChannel` deleted or renamed its instance variable `email_recipient`
  - Model `NotificationChannel` deleted or renamed its instance variable `notification_locale`
  - Model `NotificationChannel` deleted or renamed its instance variable `description`
  - Model `NotificationChannel` deleted or renamed its instance variable `events`
  - Model `NotificationChannel` deleted or renamed its instance variable `created_date`
  - Model `NotificationChannel` deleted or renamed its instance variable `provisioning_state`
  - Model `NotificationChannel` deleted or renamed its instance variable `unique_identifier`
  - Model `Policy` deleted or renamed its instance variable `description`
  - Model `Policy` deleted or renamed its instance variable `status`
  - Model `Policy` deleted or renamed its instance variable `fact_name`
  - Model `Policy` deleted or renamed its instance variable `fact_data`
  - Model `Policy` deleted or renamed its instance variable `threshold`
  - Model `Policy` deleted or renamed its instance variable `evaluator_type`
  - Model `Policy` deleted or renamed its instance variable `created_date`
  - Model `Policy` deleted or renamed its instance variable `provisioning_state`
  - Model `Policy` deleted or renamed its instance variable `unique_identifier`
  - Model `Schedule` deleted or renamed its instance variable `status`
  - Model `Schedule` deleted or renamed its instance variable `task_type`
  - Model `Schedule` deleted or renamed its instance variable `weekly_recurrence`
  - Model `Schedule` deleted or renamed its instance variable `daily_recurrence`
  - Model `Schedule` deleted or renamed its instance variable `hourly_recurrence`
  - Model `Schedule` deleted or renamed its instance variable `time_zone_id`
  - Model `Schedule` deleted or renamed its instance variable `notification_settings`
  - Model `Schedule` deleted or renamed its instance variable `created_date`
  - Model `Schedule` deleted or renamed its instance variable `target_resource_id`
  - Model `Schedule` deleted or renamed its instance variable `provisioning_state`
  - Model `Schedule` deleted or renamed its instance variable `unique_identifier`
  - Model `ScheduleCreationParameter` deleted or renamed its instance variable `status`
  - Model `ScheduleCreationParameter` deleted or renamed its instance variable `task_type`
  - Model `ScheduleCreationParameter` deleted or renamed its instance variable `weekly_recurrence`
  - Model `ScheduleCreationParameter` deleted or renamed its instance variable `daily_recurrence`
  - Model `ScheduleCreationParameter` deleted or renamed its instance variable `hourly_recurrence`
  - Model `ScheduleCreationParameter` deleted or renamed its instance variable `time_zone_id`
  - Model `ScheduleCreationParameter` deleted or renamed its instance variable `notification_settings`
  - Model `ScheduleCreationParameter` deleted or renamed its instance variable `target_resource_id`
  - Model `Secret` deleted or renamed its instance variable `value`
  - Model `Secret` deleted or renamed its instance variable `provisioning_state`
  - Model `Secret` deleted or renamed its instance variable `unique_identifier`
  - Model `ServiceFabric` deleted or renamed its instance variable `external_service_fabric_id`
  - Model `ServiceFabric` deleted or renamed its instance variable `environment_id`
  - Model `ServiceFabric` deleted or renamed its instance variable `applicable_schedule`
  - Model `ServiceFabric` deleted or renamed its instance variable `provisioning_state`
  - Model `ServiceFabric` deleted or renamed its instance variable `unique_identifier`
  - Model `User` deleted or renamed its instance variable `identity`
  - Model `User` deleted or renamed its instance variable `secret_store`
  - Model `User` deleted or renamed its instance variable `created_date`
  - Model `User` deleted or renamed its instance variable `provisioning_state`
  - Model `User` deleted or renamed its instance variable `unique_identifier`
  - Model `VirtualNetwork` deleted or renamed its instance variable `allowed_subnets`
  - Model `VirtualNetwork` deleted or renamed its instance variable `description`
  - Model `VirtualNetwork` deleted or renamed its instance variable `external_provider_resource_id`
  - Model `VirtualNetwork` deleted or renamed its instance variable `external_subnets`
  - Model `VirtualNetwork` deleted or renamed its instance variable `subnet_overrides`
  - Model `VirtualNetwork` deleted or renamed its instance variable `created_date`
  - Model `VirtualNetwork` deleted or renamed its instance variable `provisioning_state`
  - Model `VirtualNetwork` deleted or renamed its instance variable `unique_identifier`
  - Deleted or renamed model `ApplicableScheduleFragment`
  - Deleted or renamed model `ArmTemplateList`
  - Deleted or renamed model `ArtifactList`
  - Deleted or renamed model `ArtifactSourceList`
  - Deleted or renamed model `CloudErrorBody`
  - Deleted or renamed model `CustomImageList`
  - Deleted or renamed model `DiskList`
  - Deleted or renamed model `DtlEnvironmentList`
  - Deleted or renamed model `FormulaList`
  - Deleted or renamed model `GalleryImageList`
  - Deleted or renamed model `LabList`
  - Deleted or renamed model `LabVhdList`
  - Deleted or renamed model `LabVirtualMachineList`
  - Deleted or renamed model `NotificationChannelList`
  - Deleted or renamed model `OperationMetadata`
  - Deleted or renamed model `OperationMetadataDisplay`
  - Deleted or renamed model `PolicyList`
  - Deleted or renamed model `ProviderOperationResult`
  - Deleted or renamed model `ScheduleList`
  - Deleted or renamed model `SecretList`
  - Deleted or renamed model `ServiceFabricList`
  - Deleted or renamed model `ServiceRunnerList`
  - Deleted or renamed model `ShutdownNotificationContent`
  - Deleted or renamed model `UserList`
  - Deleted or renamed model `VirtualNetworkList`
  - Method `ArmTemplatesOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `ArmTemplatesOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `ArmTemplatesOperations.list` changed its parameter `orderby` from `positional_or_keyword` to `keyword_only`
  - Method `ArtifactSourcesOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `ArtifactSourcesOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `ArtifactSourcesOperations.list` changed its parameter `orderby` from `positional_or_keyword` to `keyword_only`
  - Method `ArtifactSourcesOperations.update` inserted a `positional_or_keyword` parameter `artifact_source`
  - Method `ArtifactSourcesOperations.update` deleted or renamed its parameter `tags` of kind `positional_or_keyword`
  - Method `ArtifactsOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `ArtifactsOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `ArtifactsOperations.list` changed its parameter `orderby` from `positional_or_keyword` to `keyword_only`
  - Method `CostsOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `CustomImagesOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `CustomImagesOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `CustomImagesOperations.list` changed its parameter `orderby` from `positional_or_keyword` to `keyword_only`
  - Method `CustomImagesOperations.update` inserted a `positional_or_keyword` parameter `custom_image`
  - Method `CustomImagesOperations.update` deleted or renamed its parameter `tags` of kind `positional_or_keyword`
  - Method `DisksOperations.begin_attach` inserted a `positional_or_keyword` parameter `attach_disk_properties`
  - Method `DisksOperations.begin_attach` deleted or renamed its parameter `leased_by_lab_vm_id` of kind `positional_or_keyword`
  - Method `DisksOperations.begin_detach` inserted a `positional_or_keyword` parameter `detach_disk_properties`
  - Method `DisksOperations.begin_detach` deleted or renamed its parameter `leased_by_lab_vm_id` of kind `positional_or_keyword`
  - Method `DisksOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `DisksOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `DisksOperations.list` changed its parameter `orderby` from `positional_or_keyword` to `keyword_only`
  - Method `DisksOperations.update` inserted a `positional_or_keyword` parameter `disk`
  - Method `DisksOperations.update` deleted or renamed its parameter `tags` of kind `positional_or_keyword`
  - Method `EnvironmentsOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `EnvironmentsOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `EnvironmentsOperations.list` changed its parameter `orderby` from `positional_or_keyword` to `keyword_only`
  - Method `EnvironmentsOperations.update` inserted a `positional_or_keyword` parameter `dtl_environment`
  - Method `EnvironmentsOperations.update` deleted or renamed its parameter `tags` of kind `positional_or_keyword`
  - Method `FormulasOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `FormulasOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `FormulasOperations.list` changed its parameter `orderby` from `positional_or_keyword` to `keyword_only`
  - Method `FormulasOperations.update` inserted a `positional_or_keyword` parameter `formula`
  - Method `FormulasOperations.update` deleted or renamed its parameter `tags` of kind `positional_or_keyword`
  - Method `GalleryImagesOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `GalleryImagesOperations.list` changed its parameter `orderby` from `positional_or_keyword` to `keyword_only`
  - Method `GlobalSchedulesOperations.begin_retarget` inserted a `positional_or_keyword` parameter `retarget_schedule_properties`
  - Method `GlobalSchedulesOperations.begin_retarget` deleted or renamed its parameter `current_resource_id` of kind `positional_or_keyword`
  - Method `GlobalSchedulesOperations.begin_retarget` deleted or renamed its parameter `target_resource_id` of kind `positional_or_keyword`
  - Method `GlobalSchedulesOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `GlobalSchedulesOperations.list_by_resource_group` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `GlobalSchedulesOperations.list_by_resource_group` changed its parameter `orderby` from `positional_or_keyword` to `keyword_only`
  - Method `GlobalSchedulesOperations.list_by_subscription` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `GlobalSchedulesOperations.list_by_subscription` changed its parameter `orderby` from `positional_or_keyword` to `keyword_only`
  - Method `GlobalSchedulesOperations.update` inserted a `positional_or_keyword` parameter `schedule`
  - Method `GlobalSchedulesOperations.update` deleted or renamed its parameter `tags` of kind `positional_or_keyword`
  - Method `LabsOperations.begin_export_resource_usage` inserted a `positional_or_keyword` parameter `export_resource_usage_parameters`
  - Method `LabsOperations.begin_export_resource_usage` deleted or renamed its parameter `blob_storage_absolute_sas_uri` of kind `positional_or_keyword`
  - Method `LabsOperations.begin_export_resource_usage` deleted or renamed its parameter `usage_start_date` of kind `positional_or_keyword`
  - Method `LabsOperations.begin_import_virtual_machine` inserted a `positional_or_keyword` parameter `import_lab_virtual_machine_request`
  - Method `LabsOperations.begin_import_virtual_machine` deleted or renamed its parameter `source_virtual_machine_resource_id` of kind `positional_or_keyword`
  - Method `LabsOperations.begin_import_virtual_machine` deleted or renamed its parameter `destination_virtual_machine_name` of kind `positional_or_keyword`
  - Method `LabsOperations.generate_upload_uri` inserted a `positional_or_keyword` parameter `generate_upload_uri_parameter`
  - Method `LabsOperations.generate_upload_uri` deleted or renamed its parameter `blob_name` of kind `positional_or_keyword`
  - Method `LabsOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `LabsOperations.list_by_resource_group` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `LabsOperations.list_by_resource_group` changed its parameter `orderby` from `positional_or_keyword` to `keyword_only`
  - Method `LabsOperations.list_by_subscription` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `LabsOperations.list_by_subscription` changed its parameter `orderby` from `positional_or_keyword` to `keyword_only`
  - Method `LabsOperations.update` inserted a `positional_or_keyword` parameter `lab`
  - Method `LabsOperations.update` deleted or renamed its parameter `tags` of kind `positional_or_keyword`
  - Method `NotificationChannelsOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `NotificationChannelsOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `NotificationChannelsOperations.list` changed its parameter `orderby` from `positional_or_keyword` to `keyword_only`
  - Method `NotificationChannelsOperations.notify` inserted a `positional_or_keyword` parameter `notify_parameters`
  - Method `NotificationChannelsOperations.notify` deleted or renamed its parameter `event_name` of kind `positional_or_keyword`
  - Method `NotificationChannelsOperations.notify` deleted or renamed its parameter `json_payload` of kind `positional_or_keyword`
  - Method `NotificationChannelsOperations.update` inserted a `positional_or_keyword` parameter `notification_channel`
  - Method `NotificationChannelsOperations.update` deleted or renamed its parameter `tags` of kind `positional_or_keyword`
  - Method `PoliciesOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `PoliciesOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `PoliciesOperations.list` changed its parameter `orderby` from `positional_or_keyword` to `keyword_only`
  - Method `PoliciesOperations.update` inserted a `positional_or_keyword` parameter `policy`
  - Method `PoliciesOperations.update` deleted or renamed its parameter `tags` of kind `positional_or_keyword`
  - Method `PolicySetsOperations.evaluate_policies` inserted a `positional_or_keyword` parameter `evaluate_policies_request`
  - Method `PolicySetsOperations.evaluate_policies` deleted or renamed its parameter `policies` of kind `positional_or_keyword`
  - Method `SchedulesOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `SchedulesOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `SchedulesOperations.list` changed its parameter `orderby` from `positional_or_keyword` to `keyword_only`
  - Method `SchedulesOperations.update` inserted a `positional_or_keyword` parameter `schedule`
  - Method `SchedulesOperations.update` deleted or renamed its parameter `tags` of kind `positional_or_keyword`
  - Method `SecretsOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `SecretsOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `SecretsOperations.list` changed its parameter `orderby` from `positional_or_keyword` to `keyword_only`
  - Method `SecretsOperations.update` inserted a `positional_or_keyword` parameter `secret`
  - Method `SecretsOperations.update` deleted or renamed its parameter `tags` of kind `positional_or_keyword`
  - Method `ServiceFabricSchedulesOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `ServiceFabricSchedulesOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `ServiceFabricSchedulesOperations.list` changed its parameter `orderby` from `positional_or_keyword` to `keyword_only`
  - Method `ServiceFabricSchedulesOperations.update` inserted a `positional_or_keyword` parameter `schedule`
  - Method `ServiceFabricSchedulesOperations.update` deleted or renamed its parameter `tags` of kind `positional_or_keyword`
  - Method `ServiceFabricsOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `ServiceFabricsOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `ServiceFabricsOperations.list` changed its parameter `orderby` from `positional_or_keyword` to `keyword_only`
  - Method `ServiceFabricsOperations.update` inserted a `positional_or_keyword` parameter `service_fabric`
  - Method `ServiceFabricsOperations.update` deleted or renamed its parameter `tags` of kind `positional_or_keyword`
  - Method `UsersOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `UsersOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `UsersOperations.list` changed its parameter `orderby` from `positional_or_keyword` to `keyword_only`
  - Method `UsersOperations.update` inserted a `positional_or_keyword` parameter `user`
  - Method `UsersOperations.update` deleted or renamed its parameter `tags` of kind `positional_or_keyword`
  - Method `VirtualMachineSchedulesOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `VirtualMachineSchedulesOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `VirtualMachineSchedulesOperations.list` changed its parameter `orderby` from `positional_or_keyword` to `keyword_only`
  - Method `VirtualMachineSchedulesOperations.update` inserted a `positional_or_keyword` parameter `schedule`
  - Method `VirtualMachineSchedulesOperations.update` deleted or renamed its parameter `tags` of kind `positional_or_keyword`
  - Method `VirtualMachinesOperations.begin_apply_artifacts` inserted a `positional_or_keyword` parameter `apply_artifacts_request`
  - Method `VirtualMachinesOperations.begin_apply_artifacts` deleted or renamed its parameter `artifacts` of kind `positional_or_keyword`
  - Method `VirtualMachinesOperations.begin_detach_data_disk` inserted a `positional_or_keyword` parameter `detach_data_disk_properties`
  - Method `VirtualMachinesOperations.begin_detach_data_disk` deleted or renamed its parameter `existing_lab_disk_id` of kind `positional_or_keyword`
  - Method `VirtualMachinesOperations.begin_resize` inserted a `positional_or_keyword` parameter `resize_lab_virtual_machine_properties`
  - Method `VirtualMachinesOperations.begin_resize` deleted or renamed its parameter `size` of kind `positional_or_keyword`
  - Method `VirtualMachinesOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `VirtualMachinesOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `VirtualMachinesOperations.list` changed its parameter `orderby` from `positional_or_keyword` to `keyword_only`
  - Method `VirtualMachinesOperations.update` inserted a `positional_or_keyword` parameter `lab_virtual_machine`
  - Method `VirtualMachinesOperations.update` deleted or renamed its parameter `tags` of kind `positional_or_keyword`
  - Method `VirtualNetworksOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `VirtualNetworksOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `VirtualNetworksOperations.list` changed its parameter `orderby` from `positional_or_keyword` to `keyword_only`
  - Method `VirtualNetworksOperations.update` inserted a `positional_or_keyword` parameter `virtual_network`
  - Method `VirtualNetworksOperations.update` deleted or renamed its parameter `tags` of kind `positional_or_keyword`
  - Method `GlobalSchedulesOperations.update` re-ordered its parameters from `['self', 'resource_group_name', 'name', 'tags', 'kwargs']` to `['self', 'resource_group_name', 'name', 'schedule', 'kwargs']`
  - Method `SecretsOperations.update` re-ordered its parameters from `['self', 'resource_group_name', 'lab_name', 'user_name', 'name', 'tags', 'kwargs']` to `['self', 'resource_group_name', 'lab_name', 'user_name', 'name', 'secret', 'kwargs']`
  - Method `VirtualNetworksOperations.update` re-ordered its parameters from `['self', 'resource_group_name', 'lab_name', 'name', 'tags', 'kwargs']` to `['self', 'resource_group_name', 'lab_name', 'name', 'virtual_network', 'kwargs']`
  - Method `EnvironmentsOperations.update` re-ordered its parameters from `['self', 'resource_group_name', 'lab_name', 'user_name', 'name', 'tags', 'kwargs']` to `['self', 'resource_group_name', 'lab_name', 'user_name', 'name', 'dtl_environment', 'kwargs']`
  - Method `ArtifactSourcesOperations.update` re-ordered its parameters from `['self', 'resource_group_name', 'lab_name', 'name', 'tags', 'kwargs']` to `['self', 'resource_group_name', 'lab_name', 'name', 'artifact_source', 'kwargs']`
  - Method `ServiceFabricsOperations.update` re-ordered its parameters from `['self', 'resource_group_name', 'lab_name', 'user_name', 'name', 'tags', 'kwargs']` to `['self', 'resource_group_name', 'lab_name', 'user_name', 'name', 'service_fabric', 'kwargs']`
  - Method `NotificationChannelsOperations.update` re-ordered its parameters from `['self', 'resource_group_name', 'lab_name', 'name', 'tags', 'kwargs']` to `['self', 'resource_group_name', 'lab_name', 'name', 'notification_channel', 'kwargs']`
  - Method `CustomImagesOperations.update` re-ordered its parameters from `['self', 'resource_group_name', 'lab_name', 'name', 'tags', 'kwargs']` to `['self', 'resource_group_name', 'lab_name', 'name', 'custom_image', 'kwargs']`
  - Method `ServiceFabricSchedulesOperations.update` re-ordered its parameters from `['self', 'resource_group_name', 'lab_name', 'user_name', 'service_fabric_name', 'name', 'tags', 'kwargs']` to `['self', 'resource_group_name', 'lab_name', 'user_name', 'service_fabric_name', 'name', 'schedule', 'kwargs']`
  - Method `VirtualMachinesOperations.begin_apply_artifacts` re-ordered its parameters from `['self', 'resource_group_name', 'lab_name', 'name', 'artifacts', 'kwargs']` to `['self', 'resource_group_name', 'lab_name', 'name', 'apply_artifacts_request', 'kwargs']`
  - Method `VirtualMachinesOperations.begin_detach_data_disk` re-ordered its parameters from `['self', 'resource_group_name', 'lab_name', 'name', 'existing_lab_disk_id', 'kwargs']` to `['self', 'resource_group_name', 'lab_name', 'name', 'detach_data_disk_properties', 'kwargs']`
  - Method `VirtualMachinesOperations.update` re-ordered its parameters from `['self', 'resource_group_name', 'lab_name', 'name', 'tags', 'kwargs']` to `['self', 'resource_group_name', 'lab_name', 'name', 'lab_virtual_machine', 'kwargs']`
  - Method `VirtualMachinesOperations.begin_resize` re-ordered its parameters from `['self', 'resource_group_name', 'lab_name', 'name', 'size', 'kwargs']` to `['self', 'resource_group_name', 'lab_name', 'name', 'resize_lab_virtual_machine_properties', 'kwargs']`
  - Method `PolicySetsOperations.evaluate_policies` re-ordered its parameters from `['self', 'resource_group_name', 'lab_name', 'name', 'policies', 'kwargs']` to `['self', 'resource_group_name', 'lab_name', 'name', 'evaluate_policies_request', 'kwargs']`
  - Method `UsersOperations.update` re-ordered its parameters from `['self', 'resource_group_name', 'lab_name', 'name', 'tags', 'kwargs']` to `['self', 'resource_group_name', 'lab_name', 'name', 'user', 'kwargs']`
  - Method `VirtualMachineSchedulesOperations.update` re-ordered its parameters from `['self', 'resource_group_name', 'lab_name', 'virtual_machine_name', 'name', 'tags', 'kwargs']` to `['self', 'resource_group_name', 'lab_name', 'virtual_machine_name', 'name', 'schedule', 'kwargs']`
  - Method `DisksOperations.update` re-ordered its parameters from `['self', 'resource_group_name', 'lab_name', 'user_name', 'name', 'tags', 'kwargs']` to `['self', 'resource_group_name', 'lab_name', 'user_name', 'name', 'disk', 'kwargs']`
  - Method `DisksOperations.begin_detach` re-ordered its parameters from `['self', 'resource_group_name', 'lab_name', 'user_name', 'name', 'leased_by_lab_vm_id', 'kwargs']` to `['self', 'resource_group_name', 'lab_name', 'user_name', 'name', 'detach_disk_properties', 'kwargs']`
  - Method `DisksOperations.begin_attach` re-ordered its parameters from `['self', 'resource_group_name', 'lab_name', 'user_name', 'name', 'leased_by_lab_vm_id', 'kwargs']` to `['self', 'resource_group_name', 'lab_name', 'user_name', 'name', 'attach_disk_properties', 'kwargs']`
  - Method `FormulasOperations.update` re-ordered its parameters from `['self', 'resource_group_name', 'lab_name', 'name', 'tags', 'kwargs']` to `['self', 'resource_group_name', 'lab_name', 'name', 'formula', 'kwargs']`
  - Method `SchedulesOperations.update` re-ordered its parameters from `['self', 'resource_group_name', 'lab_name', 'name', 'tags', 'kwargs']` to `['self', 'resource_group_name', 'lab_name', 'name', 'schedule', 'kwargs']`
  - Method `LabsOperations.update` re-ordered its parameters from `['self', 'resource_group_name', 'name', 'tags', 'kwargs']` to `['self', 'resource_group_name', 'name', 'lab', 'kwargs']`
  - Method `LabsOperations.generate_upload_uri` re-ordered its parameters from `['self', 'resource_group_name', 'name', 'blob_name', 'kwargs']` to `['self', 'resource_group_name', 'name', 'generate_upload_uri_parameter', 'kwargs']`
  - Method `PoliciesOperations.update` re-ordered its parameters from `['self', 'resource_group_name', 'lab_name', 'policy_set_name', 'name', 'tags', 'kwargs']` to `['self', 'resource_group_name', 'lab_name', 'policy_set_name', 'name', 'policy', 'kwargs']`



## 10.0.0b2 (2024-11-04)

### Other Changes

  - Update dependencies

## 10.0.0b1 (2022-10-28)

### Features Added

  - Model Disk has a new parameter storage_account_id

### Breaking Changes

  - Model ApplicableScheduleFragment no longer has parameter lab_vms_shutdown
  - Model ApplicableScheduleFragment no longer has parameter lab_vms_startup
  - Model ArtifactSourceFragment no longer has parameter arm_template_folder_path
  - Model ArtifactSourceFragment no longer has parameter branch_ref
  - Model ArtifactSourceFragment no longer has parameter display_name
  - Model ArtifactSourceFragment no longer has parameter folder_path
  - Model ArtifactSourceFragment no longer has parameter security_token
  - Model ArtifactSourceFragment no longer has parameter source_type
  - Model ArtifactSourceFragment no longer has parameter status
  - Model ArtifactSourceFragment no longer has parameter uri
  - Model CustomImageFragment no longer has parameter author
  - Model CustomImageFragment no longer has parameter custom_image_plan
  - Model CustomImageFragment no longer has parameter data_disk_storage_info
  - Model CustomImageFragment no longer has parameter description
  - Model CustomImageFragment no longer has parameter is_plan_authorized
  - Model CustomImageFragment no longer has parameter managed_image_id
  - Model CustomImageFragment no longer has parameter managed_snapshot_id
  - Model CustomImageFragment no longer has parameter vhd
  - Model CustomImageFragment no longer has parameter vm
  - Model DiskFragment no longer has parameter disk_blob_name
  - Model DiskFragment no longer has parameter disk_size_gi_b
  - Model DiskFragment no longer has parameter disk_type
  - Model DiskFragment no longer has parameter disk_uri
  - Model DiskFragment no longer has parameter host_caching
  - Model DiskFragment no longer has parameter leased_by_lab_vm_id
  - Model DiskFragment no longer has parameter managed_disk_id
  - Model DtlEnvironmentFragment no longer has parameter arm_template_display_name
  - Model DtlEnvironmentFragment no longer has parameter deployment_properties
  - Model FormulaFragment no longer has parameter author
  - Model FormulaFragment no longer has parameter description
  - Model FormulaFragment no longer has parameter formula_content
  - Model FormulaFragment no longer has parameter os_type
  - Model FormulaFragment no longer has parameter vm
  - Model LabFragment no longer has parameter announcement
  - Model LabFragment no longer has parameter environment_permission
  - Model LabFragment no longer has parameter extended_properties
  - Model LabFragment no longer has parameter lab_storage_type
  - Model LabFragment no longer has parameter mandatory_artifacts_resource_ids_linux
  - Model LabFragment no longer has parameter mandatory_artifacts_resource_ids_windows
  - Model LabFragment no longer has parameter premium_data_disks
  - Model LabFragment no longer has parameter support
  - Model LabVirtualMachineCreationParameter no longer has parameter artifact_deployment_status
  - Model LabVirtualMachineCreationParameter no longer has parameter compute_id
  - Model LabVirtualMachineCreationParameter no longer has parameter created_by_user
  - Model LabVirtualMachineCreationParameter no longer has parameter created_by_user_id
  - Model LabVirtualMachineCreationParameter no longer has parameter fqdn
  - Model LabVirtualMachineCreationParameter no longer has parameter last_known_power_state
  - Model LabVirtualMachineCreationParameter no longer has parameter os_type
  - Model LabVirtualMachineCreationParameter no longer has parameter virtual_machine_creation_source
  - Model LabVirtualMachineFragment no longer has parameter allow_claim
  - Model LabVirtualMachineFragment no longer has parameter artifact_deployment_status
  - Model LabVirtualMachineFragment no longer has parameter artifacts
  - Model LabVirtualMachineFragment no longer has parameter compute_id
  - Model LabVirtualMachineFragment no longer has parameter created_by_user
  - Model LabVirtualMachineFragment no longer has parameter created_by_user_id
  - Model LabVirtualMachineFragment no longer has parameter created_date
  - Model LabVirtualMachineFragment no longer has parameter custom_image_id
  - Model LabVirtualMachineFragment no longer has parameter data_disk_parameters
  - Model LabVirtualMachineFragment no longer has parameter disallow_public_ip_address
  - Model LabVirtualMachineFragment no longer has parameter environment_id
  - Model LabVirtualMachineFragment no longer has parameter expiration_date
  - Model LabVirtualMachineFragment no longer has parameter fqdn
  - Model LabVirtualMachineFragment no longer has parameter gallery_image_reference
  - Model LabVirtualMachineFragment no longer has parameter is_authentication_with_ssh_key
  - Model LabVirtualMachineFragment no longer has parameter lab_subnet_name
  - Model LabVirtualMachineFragment no longer has parameter lab_virtual_network_id
  - Model LabVirtualMachineFragment no longer has parameter last_known_power_state
  - Model LabVirtualMachineFragment no longer has parameter network_interface
  - Model LabVirtualMachineFragment no longer has parameter notes
  - Model LabVirtualMachineFragment no longer has parameter os_type
  - Model LabVirtualMachineFragment no longer has parameter owner_object_id
  - Model LabVirtualMachineFragment no longer has parameter owner_user_principal_name
  - Model LabVirtualMachineFragment no longer has parameter password
  - Model LabVirtualMachineFragment no longer has parameter plan_id
  - Model LabVirtualMachineFragment no longer has parameter schedule_parameters
  - Model LabVirtualMachineFragment no longer has parameter size
  - Model LabVirtualMachineFragment no longer has parameter ssh_key
  - Model LabVirtualMachineFragment no longer has parameter storage_type
  - Model LabVirtualMachineFragment no longer has parameter user_name
  - Model LabVirtualMachineFragment no longer has parameter virtual_machine_creation_source
  - Model NotificationChannelFragment no longer has parameter description
  - Model NotificationChannelFragment no longer has parameter email_recipient
  - Model NotificationChannelFragment no longer has parameter events
  - Model NotificationChannelFragment no longer has parameter notification_locale
  - Model NotificationChannelFragment no longer has parameter web_hook_url
  - Model PolicyFragment no longer has parameter description
  - Model PolicyFragment no longer has parameter evaluator_type
  - Model PolicyFragment no longer has parameter fact_data
  - Model PolicyFragment no longer has parameter fact_name
  - Model PolicyFragment no longer has parameter status
  - Model PolicyFragment no longer has parameter threshold
  - Model ScheduleFragment no longer has parameter daily_recurrence
  - Model ScheduleFragment no longer has parameter hourly_recurrence
  - Model ScheduleFragment no longer has parameter notification_settings
  - Model ScheduleFragment no longer has parameter status
  - Model ScheduleFragment no longer has parameter target_resource_id
  - Model ScheduleFragment no longer has parameter task_type
  - Model ScheduleFragment no longer has parameter time_zone_id
  - Model ScheduleFragment no longer has parameter weekly_recurrence
  - Model SecretFragment no longer has parameter value
  - Model ServiceFabricFragment no longer has parameter environment_id
  - Model ServiceFabricFragment no longer has parameter external_service_fabric_id
  - Model UserFragment no longer has parameter identity
  - Model UserFragment no longer has parameter secret_store
  - Model VirtualNetworkFragment no longer has parameter allowed_subnets
  - Model VirtualNetworkFragment no longer has parameter description
  - Model VirtualNetworkFragment no longer has parameter external_provider_resource_id
  - Model VirtualNetworkFragment no longer has parameter subnet_overrides
  - Operation ArtifactSourcesOperations.update has a new parameter tags
  - Operation ArtifactSourcesOperations.update no longer has parameter artifact_source
  - Operation CustomImagesOperations.update has a new parameter tags
  - Operation CustomImagesOperations.update no longer has parameter custom_image
  - Operation DisksOperations.update has a new parameter tags
  - Operation DisksOperations.update no longer has parameter disk
  - Operation EnvironmentsOperations.update has a new parameter tags
  - Operation EnvironmentsOperations.update no longer has parameter dtl_environment
  - Operation FormulasOperations.update has a new parameter tags
  - Operation FormulasOperations.update no longer has parameter formula
  - Operation GlobalSchedulesOperations.update has a new parameter tags
  - Operation GlobalSchedulesOperations.update no longer has parameter schedule
  - Operation LabsOperations.update has a new parameter tags
  - Operation LabsOperations.update no longer has parameter lab
  - Operation NotificationChannelsOperations.update has a new parameter tags
  - Operation NotificationChannelsOperations.update no longer has parameter notification_channel
  - Operation PoliciesOperations.update has a new parameter tags
  - Operation PoliciesOperations.update no longer has parameter policy
  - Operation SchedulesOperations.update has a new parameter tags
  - Operation SchedulesOperations.update no longer has parameter schedule
  - Operation SecretsOperations.update no longer has parameter value
  - Operation ServiceFabricSchedulesOperations.update has a new parameter tags
  - Operation ServiceFabricSchedulesOperations.update no longer has parameter schedule
  - Operation ServiceFabricsOperations.update has a new parameter tags
  - Operation ServiceFabricsOperations.update no longer has parameter service_fabric
  - Operation UsersOperations.update has a new parameter tags
  - Operation UsersOperations.update no longer has parameter user
  - Operation VirtualMachineSchedulesOperations.update has a new parameter tags
  - Operation VirtualMachineSchedulesOperations.update no longer has parameter schedule
  - Operation VirtualMachinesOperations.update has a new parameter tags
  - Operation VirtualMachinesOperations.update no longer has parameter lab_virtual_machine
  - Operation VirtualNetworksOperations.update has a new parameter tags
  - Operation VirtualNetworksOperations.update no longer has parameter virtual_network

## 9.0.0 (2020-12-21)

- GA release

## 9.0.0b1 (2020-10-27)

This is beta preview version.
For detailed changelog please refer to equivalent stable version 4.0.0(https://pypi.org/project/azure-mgmt-devtestlabs/4.0.0/)

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

## 4.0.0 (2019-07-26)

**Breaking changes**

  - Removed operation ServiceRunnersOperations.list

**General breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes if from some import. In summary, some modules
were incorrectly visible/importable and have been renamed. This fixed
several issues caused by usage of classes that were not supposed to be
used in the first place.

  - DevTestLabsClient cannot be imported from
    `azure.mgmt.devtestlabs.dev_test_labs_management_client`
    anymore (import from `azure.mgmt.devtestlabs` works like before)
  - DevTestLabsManagementClientConfiguration import has been moved from
    `azure.mgmt.devtestlabs.dev_test_labs_management_client` to
    `azure.mgmt.devtestlabs`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.devtestlabs.models.my_class` (import
    from `azure.mgmt.devtestlabs.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.devtestlabs.operations.my_class_operations` (import
    from `azure.mgmt.devtestlabs.operations` works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 3.0.0 (2019-02-07)

**Features**

  - Model NotificationChannel has a new parameter email_recipient
  - Model NotificationChannel has a new parameter notification_locale
  - Model ArtifactInstallProperties has a new parameter artifact_title
  - Model GalleryImage has a new parameter plan_id
  - Model GalleryImage has a new parameter is_plan_authorized
  - Model EvaluatePoliciesProperties has a new parameter
    user_object_id
  - Model ArtifactInstallPropertiesFragment has a new parameter
    artifact_title
  - Model Lab has a new parameter announcement
  - Model Lab has a new parameter support
  - Model Lab has a new parameter load_balancer_id
  - Model Lab has a new parameter
    mandatory_artifacts_resource_ids_linux
  - Model Lab has a new parameter extended_properties
  - Model Lab has a new parameter
    mandatory_artifacts_resource_ids_windows
  - Model Lab has a new parameter vm_creation_resource_group
  - Model Lab has a new parameter environment_permission
  - Model Lab has a new parameter network_security_group_id
  - Model Lab has a new parameter public_ip_id
  - Model NotificationSettingsFragment has a new parameter
    email_recipient
  - Model NotificationSettingsFragment has a new parameter
    notification_locale
  - Model LabVirtualMachineCreationParameter has a new parameter
    schedule_parameters
  - Model LabVirtualMachineCreationParameter has a new parameter
    compute_id
  - Model LabVirtualMachineCreationParameter has a new parameter
    data_disk_parameters
  - Model LabVirtualMachineCreationParameter has a new parameter
    last_known_power_state
  - Model LabVirtualMachineCreationParameter has a new parameter
    plan_id
  - Model ShutdownNotificationContent has a new parameter vm_url
  - Model ShutdownNotificationContent has a new parameter
    minutes_until_shutdown
  - Model NotificationSettings has a new parameter email_recipient
  - Model NotificationSettings has a new parameter notification_locale
  - Model LabVirtualMachine has a new parameter plan_id
  - Model LabVirtualMachine has a new parameter schedule_parameters
  - Model LabVirtualMachine has a new parameter
    last_known_power_state
  - Model LabVirtualMachine has a new parameter data_disk_parameters
  - Model ArmTemplate has a new parameter enabled
  - Model CustomImage has a new parameter custom_image_plan
  - Model CustomImage has a new parameter data_disk_storage_info
  - Model CustomImage has a new parameter is_plan_authorized
  - Model CustomImage has a new parameter managed_snapshot_id
  - Model LabVirtualMachineFragment has a new parameter
    schedule_parameters
  - Model LabVirtualMachineFragment has a new parameter compute_id
  - Model LabVirtualMachineFragment has a new parameter
    data_disk_parameters
  - Model LabVirtualMachineFragment has a new parameter
    last_known_power_state
  - Model LabVirtualMachineFragment has a new parameter plan_id
  - Added operation DisksOperations.update
  - Added operation CustomImagesOperations.update
  - Added operation LabsOperations.import_virtual_machine
  - Added operation SecretsOperations.update
  - Added operation EnvironmentsOperations.update
  - Added operation FormulasOperations.update
  - Added operation VirtualMachinesOperations.transfer_disks
  - Added operation VirtualMachinesOperations.un_claim
  - Added operation VirtualMachinesOperations.resize
  - Added operation VirtualMachinesOperations.restart
  - Added operation VirtualMachinesOperations.get_rdp_file_contents
  - Added operation VirtualMachinesOperations.redeploy
  - Added operation group ServiceFabricsOperations
  - Added operation group ServiceFabricSchedulesOperations

**Breaking changes**

  - Model VirtualNetworkFragment no longer has parameter type
  - Model VirtualNetworkFragment no longer has parameter id
  - Model VirtualNetworkFragment no longer has parameter location
  - Model VirtualNetworkFragment no longer has parameter name
  - Model VirtualNetworkFragment no longer has parameter
    external_subnets
  - Model VirtualNetworkFragment no longer has parameter
    provisioning_state
  - Model VirtualNetworkFragment no longer has parameter
    unique_identifier
  - Model PolicyFragment no longer has parameter type
  - Model PolicyFragment no longer has parameter id
  - Model PolicyFragment no longer has parameter location
  - Model PolicyFragment no longer has parameter name
  - Model PolicyFragment no longer has parameter unique_identifier
  - Model PolicyFragment no longer has parameter provisioning_state
  - Model ArtifactSourceFragment no longer has parameter type
  - Model ArtifactSourceFragment no longer has parameter id
  - Model ArtifactSourceFragment no longer has parameter location
  - Model ArtifactSourceFragment no longer has parameter name
  - Model ArtifactSourceFragment no longer has parameter
    unique_identifier
  - Model ArtifactSourceFragment no longer has parameter
    provisioning_state
  - Model LabVirtualMachineCreationParameter no longer has parameter
    applicable_schedule
  - Model LabVirtualMachineCreationParameter no longer has parameter
    compute_vm
  - Model LabVirtualMachineCreationParameter no longer has parameter
    unique_identifier
  - Model LabVirtualMachineCreationParameter no longer has parameter
    provisioning_state
  - Model ApplicableScheduleFragment no longer has parameter location
  - Model ApplicableScheduleFragment no longer has parameter type
  - Model ApplicableScheduleFragment no longer has parameter id
  - Model ApplicableScheduleFragment no longer has parameter name
  - Model ScheduleFragment no longer has parameter type
  - Model ScheduleFragment no longer has parameter id
  - Model ScheduleFragment no longer has parameter location
  - Model ScheduleFragment no longer has parameter name
  - Model ScheduleFragment no longer has parameter unique_identifier
  - Model ScheduleFragment no longer has parameter provisioning_state
  - Model LabVirtualMachineFragment no longer has parameter type
  - Model LabVirtualMachineFragment no longer has parameter id
  - Model LabVirtualMachineFragment no longer has parameter compute_vm
  - Model LabVirtualMachineFragment no longer has parameter location
  - Model LabVirtualMachineFragment no longer has parameter name
  - Model LabVirtualMachineFragment no longer has parameter
    unique_identifier
  - Model LabVirtualMachineFragment no longer has parameter
    provisioning_state
  - Model LabVirtualMachineFragment no longer has parameter
    applicable_schedule
  - Model LabFragment has a new signature
  - Model UserFragment has a new signature
  - Model NotificationChannelFragment has a new signature

## 2.2.0 (2018-02-15)

  - Add "providers" operation group

## 2.1.0 (2017-10-25)

  - Add "operations" operation group

## 2.0.0 (2017-04-27)

  - Major refactoring to follow name conventions + new features.
  - This wheel package is now built with the azure wheel extension

## 1.0.0 (2016-09-13)

  - Initial Release
