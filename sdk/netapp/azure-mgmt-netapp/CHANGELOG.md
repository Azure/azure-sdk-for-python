# Release History

## 0.16.0 (2021-02-25)

**Features**

  - Model BackupPatch has a new parameter failure_reason
  - Model NetAppAccount has a new parameter encryption
  - Model NetAppAccount has a new parameter system_data
  - Model Backup has a new parameter failure_reason
  - Model Volume has a new parameter encryption_key_source
  - Model NetAppAccountPatch has a new parameter encryption
  - Model ActiveDirectory has a new parameter ldap_over_tls

## 0.15.0 (2021-01-05)

**Features**

  - Model Volume has a new parameter smb_encryption
  - Model Volume has a new parameter smb_continuously_available
  - Model ActiveDirectory has a new parameter security_operators


## 0.14.0 (2020-11-16)

**Features**

  - Model SnapshotPolicy has a new parameter provisioning_state
  - Model SnapshotPolicy has a new parameter name1
  - Model ActiveDirectory has a new parameter aes_encryption
  - Model ActiveDirectory has a new parameter ldap_signing
  - Model Backup has a new parameter backup_id
  - Model SnapshotPolicyDetails has a new parameter provisioning_state
  - Model SnapshotPolicyDetails has a new parameter name1
  - Model BackupPolicyPatch has a new parameter tags
  - Model BackupPolicyPatch has a new parameter type
  - Model BackupPolicyPatch has a new parameter id
  - Model BackupPolicyPatch has a new parameter name1
  - Model SnapshotPolicyPatch has a new parameter provisioning_state
  - Model SnapshotPolicyPatch has a new parameter name1
  - Model BackupPatch has a new parameter backup_id
  
## 0.13.0 (2020-08-31)

**Features**

  - Model ActiveDirectory has a new parameter ad_name
  - Model ActiveDirectory has a new parameter kdc_ip
  - Model ActiveDirectory has a new parameter server_root_ca_certificate
  - Model ActiveDirectory has a new parameter status_details
  - Model ExportPolicyRule has a new parameter kerberos5i_read_only
  - Model ExportPolicyRule has a new parameter kerberos5i_read_write
  - Model ExportPolicyRule has a new parameter has_root_access
  - Model ExportPolicyRule has a new parameter kerberos5_read_only
  - Model ExportPolicyRule has a new parameter kerberos5p_read_only
  - Model ExportPolicyRule has a new parameter kerberos5p_read_write
  - Model ExportPolicyRule has a new parameter kerberos5_read_write
  - Model CapacityPoolPatch has a new parameter qos_type
  - Model Volume has a new parameter security_style
  - Model Volume has a new parameter backup_id
  - Model Volume has a new parameter kerberos_enabled
  - Model Volume has a new parameter throughput_mibps
  - Model VolumePropertiesDataProtection has a new parameter backup
  - Model VolumePatch has a new parameter data_protection
  - Model VolumePatch has a new parameter throughput_mibps
  - Model CapacityPool has a new parameter total_throughput_mibps
  - Model CapacityPool has a new parameter qos_type
  - Model CapacityPool has a new parameter utilized_throughput_mibps
  - Added operation NetAppResourceOperations.check_quota_availability
  - Added operation VolumesOperations.re_initialize_replication
  - Added operation VolumesOperations.pool_change
  - Added operation group BackupPoliciesOperations
  - Added operation group AccountBackupsOperations
  - Added operation group SnapshotPoliciesOperations
  - Added operation group BackupsOperations
  - Added operation group VaultsOperations

**Breaking changes**

  - Operation VolumesOperations.break_replication has a new signature
  - Model CapacityPoolPatch no longer has parameter service_level
  - Model MountTarget no longer has parameter end_ip
  - Model MountTarget no longer has parameter netmask
  - Model MountTarget no longer has parameter subnet
  - Model MountTarget no longer has parameter gateway
  - Model MountTarget no longer has parameter start_ip
  - Model MountTargetProperties no longer has parameter end_ip
  - Model MountTargetProperties no longer has parameter netmask
  - Model MountTargetProperties no longer has parameter subnet
  - Model MountTargetProperties no longer has parameter gateway
  - Model MountTargetProperties no longer has parameter start_ip

## 0.12.0 (2020-07-30)

**Features**

  - Model ActiveDirectory has a new parameter backup_operators
  - Model VolumePropertiesDataProtection has a new parameter snapshot
  - Model Volume has a new parameter snapshot_directory_visible

**Breaking changes**

  - Operation SnapshotsOperations.create has a new signature
  - Model Snapshot no longer has parameter file_system_id


## 0.11.0 (2020-07-09)

**Breaking changes**

  - Volume parameter mount_targets changes type from MountTarget to MountTargetProperties

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
