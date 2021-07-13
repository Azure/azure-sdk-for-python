# Release History

## 2.0.0 (2021-07-13)

**Features**

  - Model PrivateCloud has a new parameter external_cloud_links
  - Model MetricDimension has a new parameter internal_name
  - Model MetricDimension has a new parameter to_be_exported_for_shoebox
  - Added operation PrivateCloudsOperations.rotate_vcenter_password
  - Added operation PrivateCloudsOperations.rotate_nsxt_password
  - Added operation group ScriptExecutionsOperations
  - Added operation group DatastoresOperations
  - Added operation group CloudLinksOperations
  - Added operation group ScriptPackagesOperations
  - Added operation group WorkloadNetworksOperations
  - Added operation group ScriptCmdletsOperations
  - Added operation group AddonsOperations
  - Added operation group GlobalReachConnectionsOperations

**Breaking changes**

  - Operation HcxEnterpriseSitesOperations.create_or_update has a new signature
  - Operation AuthorizationsOperations.create_or_update has a new signature

## 1.0.0 (2020-11-11)

**Features**

  - Model Operation has a new parameter properties
  - Model Operation has a new parameter is_data_action
  - Model Operation has a new parameter origin
  - Model ManagementCluster has a new parameter provisioning_state

**Breaking changes**

  - Operation ClustersOperations.create_or_update has a new signature
  - Operation ClustersOperations.create_or_update has a new signature

## 1.0.0rc1 (2020-07-03)

**Features**

  - Model Endpoints has a new parameter hcx_cloud_manager
  - Model Cluster has a new parameter hosts
  - Model Cluster has a new parameter cluster_id
  - Model Cluster has a new parameter cluster_size
  - Model Cluster has a new parameter provisioning_state
  - Added operation group HcxEnterpriseSitesOperations
  - Added operation group AuthorizationsOperations

**Breaking changes**

  - Operation ClustersOperations.update has a new signature
  - Operation ClustersOperations.create_or_update has a new signature
  - Operation PrivateCloudsOperations.update has a new signature
  - Operation ClustersOperations.create_or_update has a new signature
  - Model Circuit no longer has parameter authorizations
  - Model Cluster no longer has parameter properties
  - Model Cluster has a new required parameter sku
  - Model PrivateCloud has a new signature
  - Model ExpressRouteAuthorization has a new signature

## 0.1.0 (2020-06-12)

* Initial Release
