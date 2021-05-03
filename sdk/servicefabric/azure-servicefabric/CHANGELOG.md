# Release History

## 8.0.0.0 (2021-05-03)

**Features**

  - Model ServiceDescription has a new parameter tags_required_to_run
  - Model ServiceDescription has a new parameter tags_required_to_place
  - Model NodeInfo has a new parameter node_tags
  - Model StatefulServiceDescription has a new parameter tags_required_to_run
  - Model StatefulServiceDescription has a new parameter tags_required_to_place
  - Model StatefulServiceDescription has a new parameter replica_lifecycle_description
  - Model ApplicationInfo has a new parameter managed_application_identity
  - Model ClusterHealthPolicy has a new parameter node_type_health_policy_map
  - Model StatelessServiceDescription has a new parameter instance_lifecycle_description
  - Model StatelessServiceDescription has a new parameter tags_required_to_run
  - Model StatelessServiceDescription has a new parameter tags_required_to_place
  - Model StatelessServiceDescription has a new parameter instance_restart_wait_duration_seconds
  - Model ApplicationUpgradeDescription has a new parameter managed_application_identity
  - Model StatelessServiceUpdateDescription has a new parameter tags_for_placement
  - Model StatelessServiceUpdateDescription has a new parameter service_dns_name
  - Model StatelessServiceUpdateDescription has a new parameter instance_restart_wait_duration_seconds
  - Model StatelessServiceUpdateDescription has a new parameter instance_lifecycle_description
  - Model StatelessServiceUpdateDescription has a new parameter tags_for_running
  - Model ServiceUpdateDescription has a new parameter tags_for_placement
  - Model ServiceUpdateDescription has a new parameter tags_for_running
  - Model ServiceUpdateDescription has a new parameter service_dns_name
  - Model StatefulServiceUpdateDescription has a new parameter replica_lifecycle_description
  - Model StatefulServiceUpdateDescription has a new parameter tags_for_placement
  - Model StatefulServiceUpdateDescription has a new parameter tags_for_running
  - Model StatefulServiceUpdateDescription has a new parameter service_dns_name
  - Added operation ServiceFabricClientAPIsOperationsMixin.add_node_tags
  - Added operation ServiceFabricClientAPIsOperationsMixin.get_loaded_partition_info_list
  - Added operation ServiceFabricClientAPIsOperationsMixin.remove_node_tags
  - Added operation ServiceFabricClientAPIsOperationsMixin.move_instance

**Breaking changes**

  - Operation ServiceFabricClientAPIsOperationsMixin.get_application_type_info_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_application_backup_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_application_info_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_replica_health_using_policy has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_application_health_using_policy has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_service_backup_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_application_type_info_list_by_name has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_deployed_service_package_health_using_policy has a new signature
  - Operation MeshApplicationOperations.create_or_update has a new signature
  - Operation MeshApplicationOperations.delete has a new signature
  - Operation MeshApplicationOperations.get has a new signature
  - Operation MeshApplicationOperations.get_upgrade_progress has a new signature
  - Operation MeshCodePackageOperations.get_container_logs has a new signature
  - Operation MeshGatewayOperations.create_or_update has a new signature
  - Operation MeshGatewayOperations.delete has a new signature
  - Operation MeshGatewayOperations.get has a new signature
  - Operation MeshNetworkOperations.create_or_update has a new signature
  - Operation MeshNetworkOperations.delete has a new signature
  - Operation MeshNetworkOperations.get has a new signature
  - Operation MeshSecretOperations.create_or_update has a new signature
  - Operation MeshSecretOperations.delete has a new signature
  - Operation MeshSecretOperations.get has a new signature
  - Operation MeshSecretValueOperations.add_value has a new signature
  - Operation MeshSecretValueOperations.delete has a new signature
  - Operation MeshSecretValueOperations.get has a new signature
  - Operation MeshSecretValueOperations.list has a new signature
  - Operation MeshSecretValueOperations.show has a new signature
  - Operation MeshServiceOperations.get has a new signature
  - Operation MeshServiceOperations.list has a new signature
  - Operation MeshServiceReplicaOperations.get has a new signature
  - Operation MeshServiceReplicaOperations.list has a new signature
  - Operation MeshVolumeOperations.create_or_update has a new signature
  - Operation MeshVolumeOperations.delete has a new signature
  - Operation MeshVolumeOperations.get has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.add_configuration_parameter_overrides has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.backup_partition has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.cancel_operation has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.cancel_repair_task has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.commit_image_store_upload_session has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.copy_image_store_content has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.create_application has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.create_compose_deployment has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.create_name has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.create_repair_task has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.create_service has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.create_service_from_template has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.delete_application has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.delete_backup_policy has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.delete_image_store_content has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.delete_image_store_upload_session has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.delete_name has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.delete_property has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.delete_repair_task has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.delete_service has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.deploy_service_package_to_node has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.disable_application_backup has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.disable_node has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.disable_partition_backup has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.disable_service_backup has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.enable_application_backup has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.enable_node has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.enable_partition_backup has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.enable_service_backup has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.force_approve_repair_task has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_aad_metadata has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_application_backup_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_application_event_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_application_health has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_application_info has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_application_info_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_application_load_info has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_application_manifest has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_application_name_info has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_application_type_info_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_application_type_info_list_by_name has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_application_upgrade has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_applications_event_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_backup_policy_by_name has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_chaos has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_chaos_schedule has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_cluster_configuration has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_cluster_configuration_upgrade_status has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_cluster_event_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_cluster_health has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_cluster_health_chunk has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_cluster_health_using_policy has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_cluster_load has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_cluster_manifest has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_cluster_upgrade_progress has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_cluster_version has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_compose_deployment_status has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_compose_deployment_upgrade_progress has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_configuration_overrides has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_container_logs_deployed_on_node has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_containers_event_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_correlated_event_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_data_loss_progress has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_deployed_application_health has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_deployed_application_info has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_deployed_code_package_info_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_deployed_service_package_health has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_deployed_service_package_info_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_deployed_service_package_info_list_by_name has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_deployed_service_replica_detail_info has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_deployed_service_replica_detail_info_by_partition_id has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_deployed_service_replica_info_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_deployed_service_type_info_by_name has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_deployed_service_type_info_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_fault_operation_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_image_store_content has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_image_store_folder_size has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_image_store_info has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_image_store_root_content has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_image_store_root_folder_size has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_image_store_upload_session_by_id has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_image_store_upload_session_by_path has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_name_exists_info has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_node_event_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_node_health has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_node_info has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_node_load_info has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_node_transition_progress has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_nodes_event_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_partition_backup_configuration_info has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_partition_backup_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_partition_backup_progress has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_partition_event_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_partition_health has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_partition_info has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_partition_load_information has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_partition_replica_event_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_partition_replicas_event_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_partition_restart_progress has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_partition_restore_progress has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_partitions_event_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_property_info has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_provisioned_fabric_code_version_info_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_provisioned_fabric_config_version_info_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_quorum_loss_progress has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_repair_task_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_replica_health has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_replica_info has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_service_backup_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_service_description has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_service_event_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_service_health has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_service_info has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_service_manifest has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_service_name_info has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_service_type_info_by_name has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_service_type_info_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_services_event_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_unplaced_replica_information has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_upgrade_orchestration_service_state has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.invoke_container_api has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.invoke_infrastructure_command has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.invoke_infrastructure_query has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.move_primary_replica has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.move_secondary_replica has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.post_chaos_schedule has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.provision_application_type has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.provision_cluster has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.put_property has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.recover_all_partitions has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.recover_partition has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.recover_service_partitions has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.recover_system_partitions has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.remove_compose_deployment has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.remove_configuration_overrides has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.remove_node_state has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.remove_replica has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.report_application_health has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.report_cluster_health has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.report_deployed_application_health has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.report_deployed_service_package_health has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.report_node_health has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.report_partition_health has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.report_replica_health has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.report_service_health has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.reset_partition_load has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.resolve_service has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.restart_deployed_code_package has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.restart_replica has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.restore_partition has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.resume_application_backup has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.resume_application_upgrade has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.resume_cluster_upgrade has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.resume_partition_backup has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.resume_service_backup has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.rollback_application_upgrade has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.rollback_cluster_upgrade has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.set_upgrade_orchestration_service_state has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.start_application_upgrade has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.start_chaos has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.start_cluster_configuration_upgrade has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.start_cluster_upgrade has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.start_compose_deployment_upgrade has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.start_data_loss has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.start_node_transition has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.start_partition_restart has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.start_quorum_loss has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.start_rollback_compose_deployment_upgrade has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.stop_chaos has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.submit_property_batch has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.suspend_application_backup has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.suspend_partition_backup has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.suspend_service_backup has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.toggle_verbose_service_placement_health_reporting has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.unprovision_application_type has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.unprovision_cluster has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.update_application_upgrade has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.update_cluster_upgrade has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.update_repair_execution_state has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.update_repair_task_health_policy has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.update_service has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.upload_file has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.upload_file_chunk has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_application_health_using_policy has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_deployed_service_package_health_using_policy has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_replica_health_using_policy has a new signature
  - Operation MeshApplicationOperations.list has a new signature
  - Operation MeshSecretOperations.list has a new signature
  - Operation MeshNetworkOperations.list has a new signature
  - Operation MeshVolumeOperations.list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_sub_name_info_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.update_backup_policy has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_backups_from_backup_location has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_service_backup_configuration_info has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.restart_node has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_deployed_application_health_using_policy has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_node_info_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_application_backup_configuration_info has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_deployed_application_info_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_service_health_using_policy has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_backup_policy_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_all_entities_backed_up_by_policy has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.create_backup_policy has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_cluster_health_chunk_using_policy_and_advanced_filters has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_property_info_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_partition_health_using_policy has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_compose_deployment_status_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_replica_info_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_service_info_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_partition_info_list has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.update_partition_load has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_node_health_using_policy has a new signature
  - Operation ServiceFabricClientAPIsOperationsMixin.get_chaos_events has a new signature
  - Operation MeshGatewayOperations.list has a new signature
  - Model AverageServiceLoadScalingTrigger has a new required parameter use_only_primary_load

## 7.2.0.46 (2020-10-29)

**Features**

  - Added `update_partition_load` method to update the loads of provided partitions.

## 7.1.0.45 (2020-05-14)

**Bugfix**

  - Fix ContainerCodePackageProperties entrypoint to entry_point

## 7.0.0.0 (2019-12-13)

This is re-release of 6.6.0.0 to match the actual API version used
internally

## 6.6.0.0 (2019-12-07)

**Features**

  - Model StartClusterUpgradeDescription has a new parameter
    instance_close_delay_duration_in_seconds
  - Model Setting has a new parameter type
  - Model ApplicationUpgradeDescription has a new parameter
    instance_close_delay_duration_in_seconds
  - Model HealthEvent has a new parameter health_report_id
  - Model HealthInformation has a new parameter health_report_id
  - Model StatelessServiceDescription has a new parameter flags
  - Model StatelessServiceDescription has a new parameter
    min_instance_count
  - Model StatelessServiceDescription has a new parameter
    min_instance_percentage
  - Model StatelessServiceDescription has a new parameter
    instance_close_delay_duration_seconds
  - Model StatefulServiceDescription has a new parameter
    service_placement_time_limit_seconds
  - Model ImageRegistryCredential has a new parameter password_type
  - Model ContainerCodePackageProperties has a new parameter
    liveness_probe
  - Model ContainerCodePackageProperties has a new parameter
    readiness_probe
  - Model ServiceResourceDescription has a new parameter
    execution_policy
  - Model ServiceResourceDescription has a new parameter dns_name
  - Model StatefulServiceUpdateDescription has a new parameter
    service_placement_time_limit_seconds
  - Model EnvironmentVariable has a new parameter type
  - Model StatelessServicePartitionInfo has a new parameter
    min_instance_percentage
  - Model StatelessServicePartitionInfo has a new parameter
    min_instance_count
  - Model RollingUpgradeUpdateDescription has a new parameter
    instance_close_delay_duration_in_seconds
  - Model ServiceProperties has a new parameter execution_policy
  - Model ServiceProperties has a new parameter dns_name
  - Model StatelessServiceUpdateDescription has a new parameter
    min_instance_percentage
  - Model StatelessServiceUpdateDescription has a new parameter
    min_instance_count
  - Model StatelessServiceUpdateDescription has a new parameter
    instance_close_delay_duration_seconds
  - Added operation MeshApplicationOperations.get_upgrade_progress
  - Added operation
    ServiceFabricClientAPIsOperationsMixin.remove_configuration_overrides
  - Added operation
    ServiceFabricClientAPIsOperationsMixin.get_image_store_info
  - Added operation
    ServiceFabricClientAPIsOperationsMixin.get_configuration_overrides
  - Added operation
    ServiceFabricClientAPIsOperationsMixin.add_configuration_parameter_overrides

## 6.5.0.0 (2019-06-17)

**Features**

  - Model ApplicationDescription has a new parameter
    managed_application_identity
  - Model ApplicationUpgradeDescription has a new parameter sort_order
  - Model NodeLoadMetricInformation has a new parameter
    planned_node_load_removal
  - Model NodeLoadMetricInformation has a new parameter
    current_node_load
  - Model NodeLoadMetricInformation has a new parameter
    buffered_node_capacity_remaining
  - Model NodeLoadMetricInformation has a new parameter
    node_capacity_remaining
  - Model StartClusterUpgradeDescription has a new parameter sort_order
  - Model ApplicationResourceDescription has a new parameter identity
  - Model ServiceResourceDescription has a new parameter identity_refs
  - Model ClusterUpgradeDescriptionObject has a new parameter
    sort_order
  - Model ServiceProperties has a new parameter identity_refs

**Breaking changes**

  - Model ChaosStartedEvent no longer has parameter
    wait_time_between_fautls_in_seconds
  - Model ChaosStartedEvent has a new required parameter
    wait_time_between_faults_in_seconds

## 6.4.0.0 (2018-12-07)

**Bugfixes**

  - Numerous improvements to descriptions and help texts

**Features**

  - Add command to get cluster load
  - Add command to get cluster version
  - Add mesh gateway support
  - Add mesh support
  - Add command for rolling back compose deployment upgrades
  - Various new parameters added.

## 6.3.0.0 (2018-07-27)

**Bugfixes**

  - Numerous improvements to descriptions and help texts

**Features**

  - Add application health policies parameter for config upgrade
  - Query to get nodes now supports specification to limit number of
    returned items

## 6.2.0.0 (2018-05-10)

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

**Bugfixes**

  - Numerous fixes to descriptions and help text of entities
  - Compatibility of the sdist with wheel 0.31.0

**Features**

  - Add support for invoking container APIs
  - Add option to fetch container logs from exited containers
  - Query to get chaos events now supports specification to limit number
    of returned items
  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance

## 6.1.2.9 (2018-02-05)

**Bugfixes**

  - Numerous fixes to descriptions and help text of entities

**Features**

  - Chaos service now supports a target filter
  - Application types can now be provisioned and created in external
    stores
  - Added Orchestration Service internal support APIs
  - Added container deployment management APIs

## 6.1.1.9 (2018-01-23)

This version was broken and has been removed from PyPI.

## 6.0.2 (2017-10-26)

**Bugfixes**

  - remove application_type_version in
    get_application_type_info_list_by_name
  - fix application_type_definition_kind_filter default value from
    65535 to 0

**Features**

  - add create_name, get_name_exists_info, delete_name,
    get_sub_name_info_list, get_property_info_list,
    put_property, get_property_info, delete_property,
    submit_property_batch

## 6.0.1 (2017-09-28)

**Bug fix**

  - Fix some unexpected exceptions

## 6.0 (2017-09-22)

  - Stable 6.0 api

## 6.0.0rc1 (2017-09-16)

  - Release candidate for Service Fabric 6.0 runtime

## 5.6.130 (2017-05-04)

  - Initial Release
