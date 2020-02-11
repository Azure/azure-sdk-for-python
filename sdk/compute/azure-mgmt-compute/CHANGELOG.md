# Release History

## 10.0.0 (2019-11-18)

**Features**

  - Model VirtualMachineScaleSetUpdate has a new parameter
    proximity_placement_group
  - Enum VirtualMachinePriorityTypes has new value Spot

**Breaking changes**

  - Operation ProximityPlacementGroupsOperations.get has a new signature

## 9.0.0 (2019-10-22)

**Features**

  - Model VirtualMachineScaleSetUpdateNetworkProfile has a new parameter
    health_probe
  - Model VirtualMachineScaleSetUpdate has a new parameter
    do_not_run_extensions_on_overprovisioned_vms
  - Model VirtualMachineScaleSetUpdate has a new parameter
    automatic_repairs_policy
  - Model VirtualMachineScaleSetManagedDiskParameters has a new
    parameter disk_encryption_set
  - Model ImageDataDisk has a new parameter disk_encryption_set
  - Model VirtualMachineScaleSet has a new parameter
    automatic_repairs_policy
  - Model ImageOSDisk has a new parameter disk_encryption_set
  - Model ManagedDiskParameters has a new parameter
    disk_encryption_set
  - Model Snapshot has a new parameter encryption
  - Model VirtualMachineScaleSetDataDisk has a new parameter
    disk_mbps_read_write
  - Model VirtualMachineScaleSetDataDisk has a new parameter
    disk_iops_read_write
  - Model Disk has a new parameter encryption
  - Model VirtualMachineScaleSetPublicIPAddressConfiguration has a new
    parameter public_ip_address_version
  - Model DataDisk has a new parameter disk_mbps_read_write
  - Model DataDisk has a new parameter disk_iops_read_write
  - Model OSProfile has a new parameter
    require_guest_provision_signal
  - Added operation VirtualMachinesOperations.reapply
  - Added operation group DiskEncryptionSetsOperations
  - Added operation group VirtualMachineScaleSetVMExtensionsOperations

**Breaking changes**

  - Operation VirtualMachinesOperations.list_all has a new signature
  - Operation ResourceSkusOperations.list has a new signature

## 8.0.0 (2019-09-12)

**Note**

  - Compute API version default is now 2019-07-01
  - New disks version 2019-03-01
  - New galleries version 2019-07-01

**Features**

  - Model GalleryImageVersionStorageProfile has a new parameter source
  - Model GalleryDiskImage has a new parameter source
  - Model Snapshot has new parameters: disk_size_bytes, unique_id,
    incremental
  - Model EncryptionSettingsCollection has a new parameter
    encryption_settings_version
  - Model CreationData has new parameters: source_unique_id,
    upload_size_bytes

**Breaking Changes**

  - Model GalleryImageVersionPublishingProfile no longer has parameter
    source

## 7.0.0 (2019-08-27)

**Features**

  - Model VirtualMachineScaleSetUpdateVMProfile has a new parameter
    scheduled_events_profile
  - Model VirtualMachineScaleSetUpdateVMProfile has a new parameter
    billing_profile
  - Model VirtualMachine has a new parameter
    virtual_machine_scale_set
  - Model VirtualMachine has a new parameter priority
  - Model VirtualMachine has a new parameter billing_profile
  - Model VirtualMachine has a new parameter eviction_policy
  - Model VirtualMachineScaleSetVMProfile has a new parameter
    scheduled_events_profile
  - Model VirtualMachineScaleSetVMProfile has a new parameter
    billing_profile
  - Model VirtualMachineImage has a new parameter hyper_vgeneration
  - Model VirtualMachineUpdate has a new parameter
    virtual_machine_scale_set
  - Model VirtualMachineUpdate has a new parameter priority
  - Model VirtualMachineUpdate has a new parameter billing_profile
  - Model VirtualMachineUpdate has a new parameter eviction_policy

**Breaking changes**

  - Operation VirtualMachineScaleSetVMsOperations.get has a new
    signature

## 6.0.0 (2019-07-20)

**Features**

  - Model VirtualMachine has a new parameter host
  - Model VirtualMachineUpdate has a new parameter host
  - Model VirtualMachineInstanceView has a new parameter
    hyper_vgeneration
  - Added operation group GalleryApplicationVersionsOperations
  - Added operation group GalleryApplicationsOperations
  - Added operation group DedicatedHostsOperations
  - Added operation group DedicatedHostGroupsOperations

**Breaking changes**

  - Model GalleryArtifactPublishingProfileBase has a new signature

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes if you were importing from the v20xx_yy_zz
API folders. In summary, some modules were incorrectly
visible/importable and have been renamed. This fixed several issues
caused by usage of classes that were not supposed to be used in the
first place.

  - ComputeManagementClient cannot be imported from
    `azure.mgmt.compute.v20xx_yy_zz.compute_management_client`
    anymore (import from `azure.mgmt.compute.v20xx_yy_zz` works like
    before)
  - ComputeManagementClientConfiguration import has been moved from
    `azure.mgmt.compute.v20xx_yy_zz.compute_management_client` to
    `azure.mgmt.compute.v20xx_yy_zz`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.compute.v20xx_yy_zz.models.my_class`
    (import from `azure.mgmt.compute.v20xx_yy_zz.models` works like
    before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.compute.v20xx_yy_zz.operations.my_class_operations`
    (import from `azure.mgmt.compute.v20xx_yy_zz.operations` works
    like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 5.0.0 (2019-04-26)

**Features**

  - Model ImageUpdate has a new parameter hyper_vgeneration
  - Model Image has a new parameter hyper_vgeneration
  - Model AvailabilitySet has a new parameter
    proximity_placement_group
  - Model VirtualMachine has a new parameter proximity_placement_group
  - Model VirtualMachineUpdate has a new parameter
    proximity_placement_group
  - Model VirtualMachineScaleSet has a new parameter
    proximity_placement_group
  - Model VirtualMachineScaleSet has a new parameter
    additional_capabilities
  - Model VirtualMachineScaleSetUpdate has a new parameter
    additional_capabilities
  - Model AvailabilitySetUpdate has a new parameter
    proximity_placement_group
  - Added operation group ProximityPlacementGroupsOperations
  - Model DataDisk has a new parameter to_be_detached
  - Model ResourceSkuLocationInfo has a new output zone_details

**Breaking changes**

  - Model VirtualMachineScaleSetVMProfile no longer has parameter
    additional_capabilities
  - Latest version of disks/snapshot renamed the enum
    StorageAccountTypes to DiskStorageAccountTypes
  - images.create_or_update requires hyper_vgeneration parameter if
    disk is OS type

## 4.6.2 (2019-04-22)

**Bugfix**

  - Revert "images" API version introduced in 4.6.0 from 2019-03-01 to
    2018-10-01 for backward compatiblity #4891

## 4.6.1 (2019-04-18)

**Bugfixes**

  - Make enum declarations in Compute package consistent, for the sake
    of code inspection.

## 4.6.0 (2019-04-12)

**Features**

  - Model VirtualMachineScaleSet has a new parameter
    do_not_run_extensions_on_overprovisioned_vms
  - Model VirtualMachineScaleSetVM has a new parameter
    network_profile_configuration
  - Model VirtualMachineScaleSetVM has a new parameter
    protection_policy
  - Model VirtualMachineScaleSetVM has a new parameter
    model_definition_applied
  - Added operation
    VirtualMachineScaleSetsOperations.convert_to_single_placement_group
  - Operation VirtualMachineScaleSetVMsOperations.power_off has a new
    signature and can now skip_shutdown
  - Operation VirtualMachinesOperations.power_off has a new signature
    and can now skip_shutdown
  - Operation VirtualMachineScaleSetsOperations.power_off has a new
    signature and can now skip_shutdown

## 4.5.1 (2019-03-29)

**Bugfixes**

  - Fix regression in direct import from models

## 4.5.0 (2019-03-28)

**New version of Managed Disks**

  - Disks/Snapshots have a new optional property HyperVGeneration which
    may be set to V1 or V2.
  - EncryptionSettings on a disk are now a collection instead of a
    single value. This allows multiple volumes on an encrypted disk.
  - There is a new CreateOption (Upload) for disks. To upload disks
    customers

>   - PUT a disk with CreateOption.Upload.
>   - Use GrantAccess API with AccessLevel.Write to a get a write SAS to
>     the disk. This is a new access level and it can only be used when
>     uploading to a new disk. Customers can then use storage API to
>     upload the bits for the disk.
>   - There are new DiskStates (DiskState.ReadyToUpload and
>     DiskState.ActiveUpload) that are associated with the upload
>     process.

## 4.4.0 (2018-01-04)

**Features**

  - Model VirtualMachineScaleSetExtension has a new parameter
    provision_after_extensions
  - Operation VirtualMachineScaleSetVMsOperations.reimage has a new
    parameter temp_disk
  - Operation VirtualMachineScaleSetsOperations.reimage has a new
    parameter temp_disk
  - Added operation VirtualMachinesOperations.reimage

## 4.3.1 (2018-10-15)

**Bugfix**

  - Fix sdist broken in 4.3.0. No code change.

## 4.3.0 (2018-10-02)

**Note**

  - Compute API version default is now 2018-10-01

**Features/BreakingChanges**

  - This version updates the access to properties realted to automatic
    OS upgrade introduced in 4.0.0

## 4.2.0 (2018-09-25)

**Features**

  - Model OSDisk has a new parameter diff_disk_settings
  - Model BootDiagnosticsInstanceView has a new parameter status
  - Model VirtualMachineScaleSetOSDisk has a new parameter
    diff_disk_settings
  - Added operation VirtualMachinesOperations.list_by_location

**Note**

  - azure-mgmt-nspkg is not installed anymore on Python 3 (PEP420-based
    namespace package)

## 4.1.0 (2018-09-12)

2018-06-01 for 'disks' and 'snapshots' (new default)

**Features**

  - Model DiskUpdate has a new parameter disk_iops_read_write
  - Model DiskUpdate has a new parameter disk_mbps_read_write
  - Model VirtualMachineUpdate has a new parameter
    additional_capabilities (ultraSSDEnabled attribute)
  - Model VirtualMachineScaleSetVM has a new parameter
    additional_capabilities (ultraSSDEnabled attribute)
  - Model VirtualMachineScaleSetPublicIPAddressConfiguration has a new
    parameter public_ip_prefix
  - Model Disk has a new parameter disk_iops_read_write
  - Model Disk has a new parameter disk_mbps_read_write
  - Model VirtualMachineScaleSetVMProfile has a new parameter
    additional_capabilities (ultraSSDEnabled attribute)
  - Model VirtualMachine has a new parameter additional_capabilities
    (ultraSSDEnabled attribute)
  - Added operation
    VirtualMachineScaleSetRollingUpgradesOperations.start_extension_upgrade
  - New enum value UltraSSD_LRS for StorageAccountTypes

## 4.0.1 (2018-07-23)

**Bugfix**

  - Fix incorrect import from azure.mgmt.compute.models

## 4.0.0 (2018-07-20)

**Features**

  - Model VirtualMachineScaleSetIdentity has a new parameter
    user_assigned_identities
  - Model VirtualMachineScaleSetIPConfiguration has a new parameter
    application_security_groups
  - Model VirtualMachineScaleSetUpdateIPConfiguration has a new
    parameter application_security_groups
  - Model VirtualMachineIdentity has a new parameter
    user_assigned_identities
  - Model LinuxConfiguration has a new parameter provision_vm_agent
  - Model OSProfile has a new parameter allow_extension_operations
  - Added operation group GalleryImagesOperations
  - Added operation group GalleryImageVersionsOperations
  - Added operation group GalleriesOperations
  - Model UpgradeOperationHistoricalStatusInfoProperties has a new
    parameter rollback_info
  - Model UpgradePolicy has a new parameter auto_os_upgrade_policy
  - Added operation AvailabilitySetsOperations.list_by_subscription

**Breaking changes**

  - Model VirtualMachineScaleSetIdentity no longer has parameter
    identity_ids
  - Model VirtualMachineScaleSetOSDisk no longer has parameter
    disk_size_gb
  - Model VirtualMachineScaleSetVM no longer has parameter zones
  - Model VirtualMachineScaleSetUpdateOSDisk no longer has parameter
    disk_size_gb
  - Model VirtualMachineIdentity no longer has parameter identity_ids

New default API Version is now 2018-06-01

## 4.0.0rc2 (2018-04-17)

**Features**

  - All clients now support Azure profiles.
  - Add update operation to VirtualMachineExtension operations (all
    ApiVersions)
  - Add get_extensions operation to VirtualMachine operations (all
    ApiVersions)
  - Support eviction policy for virtual machines inside a low priority
    scale set (2017-12-01)
  - Add get_os_upgrade_history to VMSS operations (2017-12-01)

**Bugfixes**

  - Compatibility of the sdist with wheel 0.31.0
  - Fix some invalid models in Python 3 (introduced in 4.0.0rc1)

## 4.0.0rc1 (2018-03-21)

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes.

  - Model signatures now use only keyword-argument syntax. All
    positional arguments must be re-written as keyword-arguments. To
    keep auto-completion in most cases, models are now generated for
    Python 2 and Python 3. Python 3 uses the "*" syntax for
    keyword-only arguments.
  - Enum types now use the "str" mixin (class AzureEnum(str, Enum)) to
    improve the behavior when unrecognized enum values are encountered.
    While this is not a breaking change, the distinctions are important,
    and are documented here:
    <https://docs.python.org/3/library/enum.html#others> At a glance:
      - "is" should not be used at all.
      - "format" will return the string value, where "%s" string
        formatting will return `NameOfEnum.stringvalue`. Format syntax
        should be prefered.
  - New Long Running Operation:
      - Return type changes from
        `msrestazure.azure_operation.AzureOperationPoller` to
        `msrest.polling.LROPoller`. External API is the same.
      - Return type is now **always** a `msrest.polling.LROPoller`,
        regardless of the optional parameters used.
      - The behavior has changed when using `raw=True`. Instead of
        returning the initial call result as `ClientRawResponse`,
        without polling, now this returns an LROPoller. After polling,
        the final resource will be returned as a `ClientRawResponse`.
      - New `polling` parameter. The default behavior is
        `Polling=True` which will poll using ARM algorithm. When
        `Polling=False`, the response of the initial call will be
        returned without polling.
      - `polling` parameter accepts instances of subclasses of
        `msrest.polling.PollingMethod`.
      - `add_done_callback` will no longer raise if called after
        polling is finished, but will instead execute the callback right
        away.

**Compute features**

  - Support zone resilient for image/snapshots (new ApiVersion
    2018-04-01)
  - Add "operations" operation group
  - Add availability_set.update
  - Add images.update
  - Add virtual_machine.update

## 3.1.0rc3 (2018-11-01)

**Features**

  - Add VirtualMachineScaleSetNetworkConfiguration ->
    enable_ip_forwarding
  - Add VirtualMachineScaleSetUpdateNetworkConfiguration ->
    enable_ip_forwarding
  - Add VirtualMachineScaleSetVMProfile -> priority
  - Add ApiVersion 2017-12-01 of virtual_machine_run_commands (new
    default)

## 3.1.0rc2 (2017-12-14)

**Features**

  - Add User Assigned Identity parameters to VM/VMSS creation

**Bugfixes**

  - Add RestrictionInfo to SKUs list (2017-09-01)
  - Restore virtual_machines.run_commands (broken in rc1)

## 3.1.0rc1 (2017-11-27)

**Disclaimer**

This version supports Azure Profile. Meaning, you can specify specific
API versions to support for each operation groups.

The default API versions of this package are now: - 2017-03-30 for
'disks', 'virtual_machine_run_commands' and 'snapshots' - 2017-09-01
for 'resource_skus' - 2017-12-01 for everything else

**Python features**

  - ComputeManagementClient has now a "profile" parameter, which is a
    dict from operation groups name to API version
  - Operation groups now have access to their own models. For instance,
    assuming you have variable called "client", you can access the
    models for this opeations groups (according to your loaded profiles)
    using `client.virtual_machines.models`
  - azure.mgmt.compute.models is deprecated. See
    <https://aka.ms/pysdkmodels> for details.

**Azure features**

  - 'resource_skus' has improved 'location_info' field

## 3.0.1 (2017-09-26)

**Bugfix**

  - Add missing virtual_machine_scale_set_rolling_upgrades
    operation group alias

## 3.0.0 (2017-09-26)

**Features**

  - Availability Zones
  - VMSS Rolling upgrade / patch / health status
  - VM instance view APIs

**Breaking changes**

  - "azure.mgmt.compute.compute" namespace is now simply
    "azure.mgmt.compute". If you were already using "azure.mgmt.compute"
    before, you code should still work exactly the same.
  - ContainerService has now be removed and exported in
    azure-mgmt-containerservice

## 2.1.0 (2017-07-19)

**Features in 2017-03-30**

  - Expose 'enableAcceleratedNetworking' for virtual machine and virtual
    machine SS. Windows GA, Linux in preview.
  - Expose 'forceUpdateTag' to ensure extension gets reinstalled even
    there are no configuration change.

## 2.0.0 (2017-06-29)

**Features**

Compute default Api Version is now 2017-03-30.

New operation groups:

  - resources_skus
  - virtual_machine_scale_set_extensions
  - virtual_machine_run_commands

New methods in VM:

  - perform_maintenance
  - run_command

Several improvements and modifications in Managed Disks.

**Breaking changes**

  - ContainerService: fixed typo in class name
    (ContainerServiceOchestratorTypes is now
    ContainerServiceOrchestratorTypes)
  - Compute: breaking changes in Managed Disk API:
      - Managed field removed from Create AV Set API
      - Account Type replaced with SKU in PUT and GET Managed Disk
        Create API
      - OwnerId replaced by ManagedBy in GET Managed Disk API

Note that you can get the behavior of v1.0.0 by forcing the Api Version
to "2016-04-30-preview" to update your package but not the code:

> ComputeManagementClient(credentials, subscription_id,
> api_version="2016-04-30-preview")

## 1.0.0 (2017-05-15)

  - Tag 1.0.0rc2 as stable (same content)

## 1.0.0rc2 (2017-05-12)

**Features**

  - Add Compute ApiVersion 2016-03-30 (AzureStack default)

## 1.0.0rc1 (2017-04-11)

**Breaking Changes**

  - Container service is now in it's own client ContainerServiceClient

**Features**

To help customers with sovereign clouds (not general Azure), this
version has official multi ApiVersion support for the following resource
type:

  - Compute: 2015-06-15 and 2016-04-30-preview

The following resource types support one ApiVersion:

  - ContainerService: 2017-01-31

## 0.33.0 (2017-02-03)

**Features**

This release adds Managed Disk to compute. This changes the default disk
creation behavior to use the new Managed Disk feature instead of
Storage.

## 0.32.1 (2016-11-14)

  - Add "Kubernetes" on Containers
  - Improve technical documentation

## 0.32.0 (2016-11-02)

**Breaking change**

New APIVersion for "container" 2016-09-30.

  - several parameters (e.g. "username") now dynamically check before
    REST calls validity against a regexp. Exception will be TypeError
    and not CloudError anymore.

## 0.31.0 (2016-11-01)

**Breaking change**

We renamed some "container" methods to follow Azure SDK conventions

  - "container" attribute on the client is now "containers"
  - "list" changed behavior, now listing containers in subscription and
    lost its parameter
  - "list_by_resource_group" new method with the old "list" behavior

## 0.30.0 (2016-10-17)

  - Initial preview release. Based on API version 2016-03-30.

## 0.20.0 (2015-08-31)

  - Initial preview release. Based on API version 2015-05-01-preview.
