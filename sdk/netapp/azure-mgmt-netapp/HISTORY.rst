.. :changelog:

Release History
===============

0.6.0 (2019-09-26)
++++++++++++++++++

**Features**

- Model Snapshot has a new parameter created
- Model ExportPolicyRule has a new parameter nfsv41
- Added operation group AzureNetAppFilesManagementClientOperationsMixin

**Breaking changes**

- Model Snapshot no longer has parameter creation_date
- Model ExportPolicyRule no longer has parameter nfsv4

0.5.0 (2019-07-03)
++++++++++++++++++

**Features**

- Model Volume has a new parameter protocol_types
- Model Volume has a new parameter mount_targets

**Breaking changes**

- Parameter subnet_id of model Volume is now required
- Parameter usage_threshold of model Volume is now required
- Parameter service_level of model CapacityPool is now required
- Parameter size of model CapacityPool is now required

0.4.0 (2019-04-29)
++++++++++++++++++

**Features**

- Model Volume has a new parameter baremetal_tenant_id
- Model Volume has a new parameter snapshot_id

**Breaking changes**

- Model ActiveDirectory fixing d_ns to dns, and s_mb_server_name to smb_server_name

0.3.0 (2019-03-25)
++++++++++++++++++

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

0.2.0 (2019-03-04)
++++++++++++++++++

**Breaking changes**

- The resource_group parameter in MountTargetsOperations.list has changed to resource_group_name
- The resource_group parameter in SnapshotsOperations.get has changed to resource_group_name
- The resource_group parameter in SnapshotsOperations.create has changed to resource_group_name
- The resource_group parameter in SnapshotsOperations.list has changed to resource_group_name
- The resource_group parameter in SnapshotsOperations.delete has changed to resource_group_name
- The resource_group parameter in SnapshotsOperations.update has changed to resource_group_name

0.1.0 (2018-01-02)
++++++++++++++++++

* Initial Release
