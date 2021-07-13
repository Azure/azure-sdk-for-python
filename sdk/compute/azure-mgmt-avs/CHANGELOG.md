# Release History

## 2.0.0 (2021-07-13)

**Features**

  - Model MetricDimension has a new parameter to_be_exported_for_shoebox
  - Model MetricDimension has a new parameter internal_name
  - Model PrivateCloud has a new parameter external_cloud_links
  - Added operation PrivateCloudsOperations.begin_create_or_update
  - Added operation PrivateCloudsOperations.begin_rotate_vcenter_password
  - Added operation PrivateCloudsOperations.begin_delete
  - Added operation PrivateCloudsOperations.begin_update
  - Added operation PrivateCloudsOperations.begin_rotate_nsxt_password
  - Added operation ClustersOperations.begin_delete
  - Added operation ClustersOperations.begin_create_or_update
  - Added operation ClustersOperations.begin_update
  - Added operation AuthorizationsOperations.begin_delete
  - Added operation AuthorizationsOperations.begin_create_or_update
  - Added operation group ScriptExecutionsOperations
  - Added operation group WorkloadNetworksOperations
  - Added operation group DatastoresOperations
  - Added operation group GlobalReachConnectionsOperations
  - Added operation group ScriptPackagesOperations
  - Added operation group ScriptCmdletsOperations
  - Added operation group AddonsOperations
  - Added operation group CloudLinksOperations

**Breaking changes**

  - Operation AuthorizationsOperations.get has a new signature
  - Operation AuthorizationsOperations.list has a new signature
  - Operation ClustersOperations.get has a new signature
  - Operation ClustersOperations.list has a new signature
  - Operation HcxEnterpriseSitesOperations.create_or_update has a new signature
  - Operation HcxEnterpriseSitesOperations.delete has a new signature
  - Operation HcxEnterpriseSitesOperations.get has a new signature
  - Operation HcxEnterpriseSitesOperations.list has a new signature
  - Operation LocationsOperations.check_quota_availability has a new signature
  - Operation LocationsOperations.check_trial_availability has a new signature
  - Operation PrivateCloudsOperations.get has a new signature
  - Operation PrivateCloudsOperations.list has a new signature
  - Operation PrivateCloudsOperations.list_admin_credentials has a new signature
  - Operation Operations.list has a new signature
  - Operation PrivateCloudsOperations.list_in_subscription has a new signature
  - Removed operation PrivateCloudsOperations.delete
  - Removed operation PrivateCloudsOperations.update
  - Removed operation PrivateCloudsOperations.create_or_update
  - Removed operation ClustersOperations.delete
  - Removed operation ClustersOperations.update
  - Removed operation ClustersOperations.create_or_update
  - Removed operation AuthorizationsOperations.delete
  - Removed operation AuthorizationsOperations.create_or_update

## 0.1.0 (1970-01-01)

* Initial Release
