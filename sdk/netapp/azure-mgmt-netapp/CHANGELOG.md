# Release History

## 7.0.0 (2022-03-15)

**Features**

  - Added operation SnapshotsOperations.begin_restore_files
  - Added operation group SubvolumesOperations
  - Model ActiveDirectory has a new parameter ldap_search_scope
  - Model BackupPolicy has a new parameter system_data
  - Model CapacityPool has a new parameter system_data
  - Model SnapshotPolicy has a new parameter system_data
  - Model Volume has a new parameter enable_subvolumes
  - Model Volume has a new parameter maximum_number_of_files
  - Model Volume has a new parameter system_data
  - Model VolumeGroupVolumeProperties has a new parameter enable_subvolumes
  - Model VolumeGroupVolumeProperties has a new parameter maximum_number_of_files
  - Model VolumePatch has a new parameter unix_permissions

**Breaking changes**

  - Operation VolumesOperations.begin_delete has a new signature

## 6.0.1 (2022-01-12)

**Fixes**

  - add support for Python 3.6

## 6.0.0 (2022-01-06)

**Features**

  - Added operation group VolumeGroupsOperations
  - Model ActiveDirectory has a new parameter encrypt_dc_connections
  - Model Volume has a new parameter capacity_pool_resource_id
  - Model Volume has a new parameter placement_rules
  - Model Volume has a new parameter proximity_placement_group
  - Model Volume has a new parameter t2_network
  - Model Volume has a new parameter volume_group_name
  - Model Volume has a new parameter volume_spec_name

**Breaking changes**

  - Model BackupPolicy no longer has parameter name_properties_name
  - Model BackupPolicyDetails no longer has parameter name_properties_name
  - Model BackupPolicyPatch no longer has parameter name_properties_name
  - Model SubscriptionQuotaItem no longer has parameter name_properties_name

## 5.1.0 (2021-09-22)

**Features**

  - Model ServiceSpecification has a new parameter log_specifications
  - Model MetricSpecification has a new parameter enable_regional_mdm_account
  - Model MetricSpecification has a new parameter is_internal
  - Model Volume has a new parameter network_sibling_set_id
  - Model Volume has a new parameter storage_to_network_proximity
  - Model Volume has a new parameter network_features
  - Added operation group NetAppResourceQuotaLimitsOperations

## 5.0.0 (2021-08-20)

**Features**

  - Model BackupPolicy has a new parameter etag
  - Model BackupPolicy has a new parameter backup_policy_id
  - Model BackupPolicyPatch has a new parameter backup_policy_id
  - Model NetAppAccount has a new parameter etag
  - Model VolumePatch has a new parameter is_default_quota_enabled
  - Model VolumePatch has a new parameter default_user_quota_in_ki_bs
  - Model VolumePatch has a new parameter default_group_quota_in_ki_bs
  - Model BackupPolicyDetails has a new parameter backup_policy_id
  - Model Volume has a new parameter clone_progress
  - Model Volume has a new parameter default_group_quota_in_ki_bs
  - Model Volume has a new parameter is_default_quota_enabled
  - Model Volume has a new parameter default_user_quota_in_ki_bs
  - Model Volume has a new parameter avs_data_store
  - Model Volume has a new parameter etag
  - Model MetricSpecification has a new parameter supported_aggregation_types
  - Model MetricSpecification has a new parameter supported_time_grain_types
  - Model MetricSpecification has a new parameter internal_metric_name
  - Model MetricSpecification has a new parameter source_mdm_namespace
  - Model MetricSpecification has a new parameter source_mdm_account
  - Model CapacityPool has a new parameter encryption_type
  - Model CapacityPool has a new parameter etag
  - Model SnapshotPolicy has a new parameter etag
  - Added operation AccountsOperations.list_by_subscription

**Breaking changes**

  - Model BackupPolicy no longer has parameter yearly_backups_to_keep
  - Model BackupPolicyPatch no longer has parameter yearly_backups_to_keep
  - Model BackupPolicyDetails no longer has parameter yearly_backups_to_keep

## 4.0.0 (2021-06-11)

**Features**

  - Model ExportPolicyRule has a new parameter chown_mode
  - Model BackupStatus has a new parameter last_transfer_size
  - Model BackupStatus has a new parameter total_transfer_bytes
  - Model BackupStatus has a new parameter last_transfer_type
  - Model Volume has a new parameter cool_access
  - Model Volume has a new parameter unix_permissions
  - Model Volume has a new parameter coolness_period
  - Model CapacityPool has a new parameter cool_access
  - Model ActiveDirectory has a new parameter administrators
  - Added operation BackupsOperations.get_volume_restore_status

**Breaking changes**

  - Operation NetAppResourceOperations.check_file_path_availability has a new signature

## 3.0.0 (2021-05-21)

**Features**

  - Model Backup has a new parameter use_existing_snapshot
  - Model VolumePatchPropertiesDataProtection has a new parameter snapshot
  - Model BackupPatch has a new parameter use_existing_snapshot
  - Added operation BackupPoliciesOperations.begin_update
  - Added operation BackupsOperations.get_status

**Breaking changes**

  - Removed operation BackupPoliciesOperations.update
  - Removed operation group VolumeBackupStatusOperations

## 2.0.0 (2021-03-16)

**Features**

  - Model Volume has a new parameter ldap_enabled
  - Model Backup has a new parameter volume_name
  - Model ActiveDirectory has a new parameter allow_local_nfs_users_with_ldap
  - Model BackupPatch has a new parameter volume_name
  - Added operation BackupsOperations.begin_update
  - Added operation group VolumeBackupStatusOperations

**Breaking changes**

  - Model SnapshotPolicyDetails no longer has parameter name_properties_name
  - Model SnapshotPolicyPatch no longer has parameter name_properties_name
  - Model Volume no longer has parameter name_properties_name
  - Model SnapshotPolicy no longer has parameter name_properties_name
  - Removed operation BackupsOperations.update

## 1.0.0 (2021-02-04)

**Features**

  - Model VolumeList has a new parameter next_link
  - Model BackupPatch has a new parameter failure_reason
  - Model Backup has a new parameter failure_reason
  - Model NetAppAccountList has a new parameter next_link
  - Model ActiveDirectory has a new parameter security_operators
  - Model ActiveDirectory has a new parameter ldap_over_tls
  - Model NetAppAccountPatch has a new parameter encryption
  - Model CapacityPoolList has a new parameter next_link
  - Model Volume has a new parameter encryption_key_source
  - Model Volume has a new parameter smb_encryption
  - Model Volume has a new parameter smb_continuously_available
  - Model Volume has a new parameter name_properties_name
  - Model NetAppAccount has a new parameter system_data
  - Model NetAppAccount has a new parameter encryption
  - Added operation SnapshotPoliciesOperations.begin_update

**Breaking changes**

  - Removed operation SnapshotPoliciesOperations.update

## 1.0.0b1 (2020-12-01)

This is beta preview version.

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
  - For a complete set of
  supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core-tracing-opentelemetry) for an overview.

## 0.10.0 (2020-04-21)

**Features**

  - Model MountTarget has a new parameter end_ip
  - Model MountTarget has a new parameter start_ip
  - Model MountTarget has a new parameter netmask
  - Model MountTarget has a new parameter gateway
  - Model MountTarget has a new parameter subnet

## 0.9.0 (2020-04-02)

**Features**

  - Model ActiveDirectory has a new parameter site
  - Added operation VolumesOperations.revert

**Breaking changes**

  - Operation SnapshotsOperations.update has a new signature
  - Operation SnapshotsOperations.update has a new signature
  - Operation SnapshotsOperations.create has a new signature
  - Model Snapshot no longer has parameter tags
  - Model MountTarget no longer has parameter netmask
  - Model MountTarget no longer has parameter subnet
  - Model MountTarget no longer has parameter start_ip
  - Model MountTarget no longer has parameter provisioning_state
  - Model MountTarget no longer has parameter gateway
  - Model MountTarget no longer has parameter end_ip
  - Removed operation group MountTargetsOperations

## 0.8.0 (2020-01-12)

**Features**

  - Model Volume has a new parameter is_restoring
  - Model ReplicationObject has a new parameter remote_volume_region
  - Added operation VolumesOperations.delete_replication
  - Added operation VolumesOperations.break_replication
  - Added operation VolumesOperations.resync_replication
  - Added operation VolumesOperations.authorize_replication
  - Added operation VolumesOperations.replication_status_method

## 0.7.0 (2019-11-12)

**Features**

  - Model MountTarget has a new parameter type
  - Model Volume has a new parameter data_protection
  - Model Volume has a new parameter volume_type
  - Added operation group NetAppResourceOperations

**Breaking changes**

  - Removed operation group
    AzureNetAppFilesManagementClientOperationsMixin

## 0.6.0 (2019-09-26)

**Features**

  - Model Snapshot has a new parameter created
  - Model ExportPolicyRule has a new parameter nfsv41
  - Added operation group
    AzureNetAppFilesManagementClientOperationsMixin

**Breaking changes**

  - Model Snapshot no longer has parameter creation_date
  - Model ExportPolicyRule no longer has parameter nfsv4

## 0.5.0 (2019-07-03)

**Features**

  - Model Volume has a new parameter protocol_types
  - Model Volume has a new parameter mount_targets

**Breaking changes**

  - Parameter subnet_id of model Volume is now required
  - Parameter usage_threshold of model Volume is now required
  - Parameter service_level of model CapacityPool is now required
  - Parameter size of model CapacityPool is now required

## 0.4.0 (2019-04-29)

**Features**

  - Model Volume has a new parameter baremetal_tenant_id
  - Model Volume has a new parameter snapshot_id

**Breaking changes**

  - Model ActiveDirectory fixing d_ns to dns, and s_mb_server_name
    to smb_server_name

## 0.3.0 (2019-03-25)

**Features**

  - Model VolumePatch has a new parameter export_policy
  - Model NetAppAccount has a new parameter active_directories
  - Model Volume has a new parameter export_policy
  - Model MountTarget has a new parameter smb_server_fqdn
  - Model MountTarget has a new parameter subnet

**Breaking changes**

  - Operation PoolsOperations.update has a new signature
  - Model MountTarget no longer has parameter vlan_id
  - Operation AccountsOperations.update has a new signature
  - Operation AccountsOperations.create_or_update has a new signature
  - Model CapacityPoolPatch has a new signature
  - Model NetAppAccountPatch has a new signature

## 0.2.0 (2019-03-04)

**Breaking changes**

  - The resource_group parameter in MountTargetsOperations.list has
    changed to resource_group_name
  - The resource_group parameter in SnapshotsOperations.get has changed
    to resource_group_name
  - The resource_group parameter in SnapshotsOperations.create has
    changed to resource_group_name
  - The resource_group parameter in SnapshotsOperations.list has
    changed to resource_group_name
  - The resource_group parameter in SnapshotsOperations.delete has
    changed to resource_group_name
  - The resource_group parameter in SnapshotsOperations.update has
    changed to resource_group_name

## 0.1.0 (2018-01-02)

  - Initial Release
