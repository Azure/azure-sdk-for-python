# Release History

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
