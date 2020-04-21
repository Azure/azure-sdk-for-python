# Release History

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
