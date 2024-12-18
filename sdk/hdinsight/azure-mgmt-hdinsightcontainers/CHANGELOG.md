# Release History

## 1.0.0b3 (2024-08-26)

### Features Added

  - The 'HDInsightContainersMgmtClient' client had operation group 'cluster_pool_upgrade_histories' added in the current version
  - The 'HDInsightContainersMgmtClient' client had operation group 'cluster_upgrade_histories' added in the current version
  - The 'HDInsightContainersMgmtClient' client had operation group 'cluster_libraries' added in the current version
  - The 'ClustersOperations' method 'begin_upgrade_manual_rollback' was added in the current version
  - The model or publicly exposed class 'ClusterLibrariesOperations' was added in the current version
  - The model or publicly exposed class 'ClusterPoolUpgradeHistoriesOperations' was added in the current version
  - The model or publicly exposed class 'ClusterUpgradeHistoriesOperations' was added in the current version
  - The model or publicly exposed class 'ClusterAvailableUpgradeType' had property 'PATCH_VERSION_UPGRADE' added in the current version
  - The model or publicly exposed class 'ClusterPoolComputeProfile' had property 'availability_zones' added in the current version
  - The model or publicly exposed class 'ClusterPoolProfile' had property 'public_ip_tag' added in the current version
  - The model or publicly exposed class 'ClusterPoolResourcePropertiesClusterPoolProfile' had property 'public_ip_tag' added in the current version
  - The model or publicly exposed class 'ClusterPoolResourcePropertiesComputeProfile' had property 'availability_zones' added in the current version
  - The model or publicly exposed class 'ClusterProfile' had property 'managed_identity_profile' added in the current version
  - The model or publicly exposed class 'ClusterUpgradeType' had property 'PATCH_VERSION_UPGRADE' added in the current version
  - The model or publicly exposed class 'ComputeProfile' had property 'availability_zones' added in the current version
  - The model or publicly exposed class 'SshProfile' had property 'vm_size' added in the current version
  - The model or publicly exposed class 'UpdatableClusterProfile' had property 'secrets_profile' added in the current version
  - The model or publicly exposed class 'UpdatableClusterProfile' had property 'trino_profile' added in the current version
  - The model or publicly exposed class 'Category' was added in the current version
  - The model or publicly exposed class 'ClusterAksPatchUpgradeHistoryProperties' was added in the current version
  - The model or publicly exposed class 'ClusterAvailableInPlaceUpgradeProperties' was added in the current version
  - The model or publicly exposed class 'ClusterAvailableUpgradePatchVersionUpgradeProperties' was added in the current version
  - The model or publicly exposed class 'ClusterHotfixUpgradeHistoryProperties' was added in the current version
  - The model or publicly exposed class 'ClusterHotfixUpgradeRollbackHistoryProperties' was added in the current version
  - The model or publicly exposed class 'ClusterInPlaceUpgradeHistoryProperties' was added in the current version
  - The model or publicly exposed class 'ClusterInPlaceUpgradeProperties' was added in the current version
  - The model or publicly exposed class 'ClusterLibrary' was added in the current version
  - The model or publicly exposed class 'ClusterLibraryList' was added in the current version
  - The model or publicly exposed class 'ClusterLibraryManagementOperation' was added in the current version
  - The model or publicly exposed class 'ClusterLibraryManagementOperationProperties' was added in the current version
  - The model or publicly exposed class 'ClusterLibraryProperties' was added in the current version
  - The model or publicly exposed class 'ClusterPatchVersionUpgradeHistoryProperties' was added in the current version
  - The model or publicly exposed class 'ClusterPatchVersionUpgradeProperties' was added in the current version
  - The model or publicly exposed class 'ClusterPatchVersionUpgradeRollbackHistoryProperties' was added in the current version
  - The model or publicly exposed class 'ClusterPoolAksPatchUpgradeHistoryProperties' was added in the current version
  - The model or publicly exposed class 'ClusterPoolNodeOsUpgradeHistoryProperties' was added in the current version
  - The model or publicly exposed class 'ClusterPoolUpgradeHistory' was added in the current version
  - The model or publicly exposed class 'ClusterPoolUpgradeHistoryListResult' was added in the current version
  - The model or publicly exposed class 'ClusterPoolUpgradeHistoryProperties' was added in the current version
  - The model or publicly exposed class 'ClusterPoolUpgradeHistoryType' was added in the current version
  - The model or publicly exposed class 'ClusterPoolUpgradeHistoryUpgradeResultType' was added in the current version
  - The model or publicly exposed class 'ClusterUpgradeHistory' was added in the current version
  - The model or publicly exposed class 'ClusterUpgradeHistoryListResult' was added in the current version
  - The model or publicly exposed class 'ClusterUpgradeHistoryProperties' was added in the current version
  - The model or publicly exposed class 'ClusterUpgradeHistorySeverityType' was added in the current version
  - The model or publicly exposed class 'ClusterUpgradeHistoryType' was added in the current version
  - The model or publicly exposed class 'ClusterUpgradeHistoryUpgradeResultType' was added in the current version
  - The model or publicly exposed class 'ClusterUpgradeRollback' was added in the current version
  - The model or publicly exposed class 'ClusterUpgradeRollbackProperties' was added in the current version
  - The model or publicly exposed class 'IpTag' was added in the current version
  - The model or publicly exposed class 'LibraryManagementAction' was added in the current version
  - The model or publicly exposed class 'ManagedIdentityProfile' was added in the current version
  - The model or publicly exposed class 'ManagedIdentitySpec' was added in the current version
  - The model or publicly exposed class 'ManagedIdentityType' was added in the current version
  - The model or publicly exposed class 'MavenLibraryProperties' was added in the current version
  - The model or publicly exposed class 'PyPiLibraryProperties' was added in the current version
  - The model or publicly exposed class 'Status' was added in the current version
  - The model or publicly exposed class 'Type' was added in the current version

### Breaking Changes

  - The model or publicly exposed class 'ClusterAvailableUpgradeHotfixUpgradeProperties' had its instance variable 'description' deleted or renamed in the current version
  - The model or publicly exposed class 'ClusterAvailableUpgradeHotfixUpgradeProperties' had its instance variable 'source_oss_version' deleted or renamed in the current version
  - The model or publicly exposed class 'ClusterAvailableUpgradeHotfixUpgradeProperties' had its instance variable 'source_cluster_version' deleted or renamed in the current version
  - The model or publicly exposed class 'ClusterAvailableUpgradeHotfixUpgradeProperties' had its instance variable 'source_build_number' deleted or renamed in the current version
  - The model or publicly exposed class 'ClusterAvailableUpgradeHotfixUpgradeProperties' had its instance variable 'target_oss_version' deleted or renamed in the current version
  - The model or publicly exposed class 'ClusterAvailableUpgradeHotfixUpgradeProperties' had its instance variable 'target_cluster_version' deleted or renamed in the current version
  - The model or publicly exposed class 'ClusterAvailableUpgradeHotfixUpgradeProperties' had its instance variable 'target_build_number' deleted or renamed in the current version
  - The model or publicly exposed class 'ClusterAvailableUpgradeHotfixUpgradeProperties' had its instance variable 'component_name' deleted or renamed in the current version
  - The model or publicly exposed class 'ClusterAvailableUpgradeHotfixUpgradeProperties' had its instance variable 'severity' deleted or renamed in the current version
  - The model or publicly exposed class 'ClusterAvailableUpgradeHotfixUpgradeProperties' had its instance variable 'extended_properties' deleted or renamed in the current version
  - The model or publicly exposed class 'ClusterAvailableUpgradeHotfixUpgradeProperties' had its instance variable 'created_time' deleted or renamed in the current version
  - The model or publicly exposed class 'ClusterHotfixUpgradeProperties' had its instance variable 'target_oss_version' deleted or renamed in the current version
  - The model or publicly exposed class 'ClusterHotfixUpgradeProperties' had its instance variable 'target_cluster_version' deleted or renamed in the current version
  - The model or publicly exposed class 'ClusterHotfixUpgradeProperties' had its instance variable 'target_build_number' deleted or renamed in the current version
  - The model or publicly exposed class 'ClusterHotfixUpgradeProperties' had its instance variable 'component_name' deleted or renamed in the current version
  - The model or publicly exposed class 'KafkaProfile' had its instance variable 'cluster_identity' deleted or renamed in the current version

## 1.0.0b2 (2024-04-07)

### Features Added

  - Added operation ClusterPoolsOperations.begin_upgrade
  - Added operation ClustersOperations.begin_upgrade
  - Added operation group ClusterAvailableUpgradesOperations
  - Added operation group ClusterPoolAvailableUpgradesOperations
  - Model Cluster has a new parameter properties
  - Model ClusterPatch has a new parameter properties
  - Model ClusterPool has a new parameter properties
  - Model ClusterPoolNetworkProfile has a new parameter api_server_authorized_ip_ranges
  - Model ClusterPoolNetworkProfile has a new parameter enable_private_api_server
  - Model ClusterPoolNetworkProfile has a new parameter outbound_type
  - Model ClusterPoolResourcePropertiesNetworkProfile has a new parameter api_server_authorized_ip_ranges
  - Model ClusterPoolResourcePropertiesNetworkProfile has a new parameter enable_private_api_server
  - Model ClusterPoolResourcePropertiesNetworkProfile has a new parameter outbound_type
  - Model ClusterPoolVersion has a new parameter properties
  - Model ClusterProfile has a new parameter cluster_access_profile
  - Model ClusterProfile has a new parameter ranger_plugin_profile
  - Model ClusterProfile has a new parameter ranger_profile
  - Model ClusterResizeData has a new parameter properties
  - Model ClusterVersion has a new parameter properties
  - Model ConnectivityProfileWeb has a new parameter private_fqdn
  - Model FlinkHiveCatalogOption has a new parameter metastore_db_connection_authentication_mode
  - Model FlinkJobProperties has a new parameter run_id
  - Model FlinkProfile has a new parameter deployment_mode
  - Model FlinkProfile has a new parameter job_spec
  - Model HiveCatalogOption has a new parameter metastore_db_connection_authentication_mode
  - Model ServiceConfigResult has a new parameter properties
  - Model SparkMetastoreSpec has a new parameter db_connection_authentication_mode
  - Model SshConnectivityEndpoint has a new parameter private_ssh_endpoint
  - Model TrinoCoordinator has a new parameter debug
  - Model TrinoWorker has a new parameter debug
  - Model UpdatableClusterProfile has a new parameter ranger_plugin_profile
  - Model UpdatableClusterProfile has a new parameter ranger_profile
  - Model WebConnectivityEndpoint has a new parameter private_fqdn
  - Operation ClusterJobsOperations.list has a new optional parameter filter

### Breaking Changes

  - Model Cluster no longer has parameter cluster_profile
  - Model Cluster no longer has parameter cluster_type
  - Model Cluster no longer has parameter compute_profile
  - Model Cluster no longer has parameter deployment_id
  - Model Cluster no longer has parameter provisioning_state
  - Model Cluster no longer has parameter status
  - Model ClusterInstanceViewResult has a new required parameter properties
  - Model ClusterInstanceViewResult no longer has parameter service_statuses
  - Model ClusterInstanceViewResult no longer has parameter status
  - Model ClusterPatch no longer has parameter cluster_profile
  - Model ClusterPatch no longer has parameter id
  - Model ClusterPatch no longer has parameter location
  - Model ClusterPatch no longer has parameter name
  - Model ClusterPatch no longer has parameter system_data
  - Model ClusterPatch no longer has parameter type
  - Model ClusterPool no longer has parameter aks_cluster_profile
  - Model ClusterPool no longer has parameter aks_managed_resource_group_name
  - Model ClusterPool no longer has parameter cluster_pool_profile
  - Model ClusterPool no longer has parameter compute_profile
  - Model ClusterPool no longer has parameter deployment_id
  - Model ClusterPool no longer has parameter log_analytics_profile
  - Model ClusterPool no longer has parameter managed_resource_group_name
  - Model ClusterPool no longer has parameter network_profile
  - Model ClusterPool no longer has parameter provisioning_state
  - Model ClusterPool no longer has parameter status
  - Model ClusterPoolVersion no longer has parameter aks_version
  - Model ClusterPoolVersion no longer has parameter cluster_pool_version
  - Model ClusterPoolVersion no longer has parameter is_preview
  - Model ClusterResizeData no longer has parameter target_worker_node_count
  - Model ClusterVersion no longer has parameter cluster_pool_version
  - Model ClusterVersion no longer has parameter cluster_type
  - Model ClusterVersion no longer has parameter cluster_version
  - Model ClusterVersion no longer has parameter components
  - Model ClusterVersion no longer has parameter is_preview
  - Model ClusterVersion no longer has parameter oss_version
  - Model ServiceConfigResult no longer has parameter component_name
  - Model ServiceConfigResult no longer has parameter content
  - Model ServiceConfigResult no longer has parameter custom_keys
  - Model ServiceConfigResult no longer has parameter default_keys
  - Model ServiceConfigResult no longer has parameter file_name
  - Model ServiceConfigResult no longer has parameter path
  - Model ServiceConfigResult no longer has parameter service_name
  - Model ServiceConfigResult no longer has parameter type
  - Model TrinoCoordinator no longer has parameter enable
  - Model TrinoCoordinator no longer has parameter port
  - Model TrinoCoordinator no longer has parameter suspend
  - Model TrinoWorker no longer has parameter enable
  - Model TrinoWorker no longer has parameter port
  - Model TrinoWorker no longer has parameter suspend

## 1.0.0b1 (2023-08-18)

* Initial Release
