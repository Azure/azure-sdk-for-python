# Release History

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
