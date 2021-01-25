# Release History

## 2.2.0 (2021-01-25)

**Features**

  - Model ClusterIdentityUserAssignedIdentitiesValue has a new parameter tenant_id
  - Model Operation has a new parameter properties
  - Model Role has a new parameter encrypt_data_disks
  - Model OperationDisplay has a new parameter description
  - Model BillingResponseListResult has a new parameter vm_sizes_with_encryption_at_host
  - Model BillingResponseListResult has a new parameter vm_size_properties
  - Model ConnectivityEndpoint has a new parameter private_ip_address
  - Model ClusterGetProperties has a new parameter storage_profile
  - Model ClusterGetProperties has a new parameter excluded_services_config
  - Model ClusterGetProperties has a new parameter cluster_hdp_version
  - Model ApplicationGetEndpoint has a new parameter private_ip_address

## 2.1.0 (2020-12-21)

**Features**

  - Model ClusterGetProperties has a new parameter compute_isolation_properties
  - Model HostInfo has a new parameter effective_disk_encryption_key_url
  - Model HostInfo has a new parameter fqdn
  - Model ClusterCreateProperties has a new parameter compute_isolation_properties

## 2.0.0 (2020-10-20)

**Features**

  - Model ClusterGetProperties has a new parameter network_properties
  - Model ClusterGetProperties has a new parameter cluster_id
  - Model ClusterCreateProperties has a new parameter network_properties

**Breaking changes**

  - Model ClusterGetProperties no longer has parameter network_settings
  - Model ClusterCreateProperties no longer has parameter network_settings
  
## 1.7.0 (2020-08-13)

**Features**

  - Model DiskEncryptionProperties has a new parameter encryption_at_host

## 1.6.0 (2020-07-17)

**Features**

  - Added operation group VirtualMachinesOperations

## 1.5.1 (2020-06-11)

**Bugfixes**

  - Fix the List Response

## 1.5.0 (2020-05-29)

**Features**

  - Added operation group VirtualMachinesOperations

## 1.4.0 (2020-01-16)

**Features**

  - Model ClusterCreateProperties has a new parameter
    min_supported_tls_version
  - Model ClusterGetProperties has a new parameter
    min_supported_tls_version

## 1.3.0 (2019-12-07)

**Features**

  - Model ClusterGetProperties has a new parameter
    kafka_rest_properties
  - Model ClusterCreateProperties has a new parameter
    kafka_rest_properties

## 1.2.0 (2019-08-06)

**Features**

  - Model Role has a new parameter autoscale_configuration
  - Added operation LocationsOperations.list_billing_specs
  - Added operation LocationsOperations.get_capabilities

## 1.1.0 (2019-06-17)

**Features**

  - Model ApplicationGetHttpsEndpoint has a new parameter
    disable_gateway_auth
  - Model ApplicationGetHttpsEndpoint has a new parameter
    sub_domain_suffix

## 1.0.0 (2019-04-08)

Stable versionning of the 0.3.0 (no changes)

## 0.3.0 (2019-04-08)

**Features**

  - Added operation ConfigurationsOperations.list
  - Added operation ClustersOperations.get_gateway_settings
  - Added operation ClustersOperations.update_gateway_settings

## 0.2.1 (2019-01-28)

**Features**

  - Add MSI support

## 0.2.0 (2018-12-11)

**Features**

  - Model SecurityProfile has a new parameter msi_resource_id
  - Model SecurityProfile has a new parameter aadds_resource_id
  - Model ClusterCreateProperties has a new parameter
    disk_encryption_properties
  - Model ClusterGetProperties has a new parameter
    disk_encryption_properties
  - Model Cluster has a new parameter identity
  - Model ClusterCreateParametersExtended has a new parameter identity
  - Added operation ClustersOperations.rotate_disk_encryption_key
  - Added operation ScriptActionsOperations.list_by_cluster
  - Added operation ScriptExecutionHistoryOperations.list_by_cluster
  - Added operation ConfigurationsOperations.update
  - Added operation ApplicationsOperations.list_by_cluster
  - Added operation group ExtensionsOperations

**Breaking changes**

  - Model ApplicationProperties no longer has parameter
    additional_properties
  - Model ApplicationGetHttpsEndpoint no longer has parameter
    additional_properties
  - Removed operation ScriptActionsOperations.list_persisted_scripts
  - Removed operation ScriptExecutionHistoryOperations.list
  - Removed operation ConfigurationsOperations.update_http_settings
  - Removed operation ApplicationsOperations.list
  - Removed operation LocationsOperations.get_capabilities
  - Removed operation group ExtensionOperations

## 0.1.0 (2018-08-08)

  - Initial Release
