# Release History

## 1.0.0b2 (2025-01-13)

### Features Added

  - Model `ConnectedCacheMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Model `AdditionalCacheNodeProperties` added property `issues_list`
  - Model `AdditionalCacheNodeProperties` added property `issues_count`
  - Model `AdditionalCacheNodeProperties` added property `current_tls_certificate`
  - Model `AdditionalCacheNodeProperties` added property `last_auto_update_info`
  - Model `AdditionalCacheNodeProperties` added property `creation_method`
  - Model `AdditionalCacheNodeProperties` added property `tls_status`
  - Model `CacheNodeInstallProperties` added property `tls_certificate_provisioning_key`
  - Model `CacheNodeInstallProperties` added property `drive_configuration`
  - Model `CacheNodeInstallProperties` added property `proxy_url_configuration`
  - Added model `MccCacheNodeAutoUpdateHistory`
  - Added model `MccCacheNodeAutoUpdateHistoryProperties`
  - Added model `MccCacheNodeAutoUpdateInfo`
  - Added model `MccCacheNodeIssueHistory`
  - Added model `MccCacheNodeIssueHistoryProperties`
  - Added model `MccCacheNodeTlsCertificate`
  - Added model `MccCacheNodeTlsCertificateHistory`
  - Added model `MccCacheNodeTlsCertificateProperties`
  - Added model `MccIssue`
  - Operation group `EnterpriseMccCacheNodesOperationsOperations` added method `get_cache_node_auto_update_history`
  - Operation group `EnterpriseMccCacheNodesOperationsOperations` added method `get_cache_node_mcc_issue_details_history`
  - Operation group `EnterpriseMccCacheNodesOperationsOperations` added method `get_cache_node_tls_certificate_history`
  - Operation group `IspCacheNodesOperationsOperations` added method `get_cache_node_auto_update_history`
  - Operation group `IspCacheNodesOperationsOperations` added method `get_cache_node_mcc_issue_details_history`

### Breaking Changes

  - Deleted or renamed client operation group `ConnectedCacheMgmtClient.enterprise_customer_operations`
  - Deleted or renamed client operation group `ConnectedCacheMgmtClient.cache_nodes_operations`
  - Model `AdditionalCacheNodeProperties` deleted or renamed its instance variable `proxy_url`
  - Model `AdditionalCacheNodeProperties` deleted or renamed its instance variable `update_cycle_type`
  - Model `AdditionalCustomerProperties` deleted or renamed its instance variable `peering_db_last_update_time`
  - Deleted or renamed model `CacheNodeOldResponse`
  - Deleted or renamed model `CacheNodePreviewResource`
  - Deleted or renamed model `CycleType`
  - Deleted or renamed model `EnterprisePreviewResource`

## 1.0.0b1 (2024-11-21)

### Other Changes

  - Initial version
