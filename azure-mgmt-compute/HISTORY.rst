.. :changelog:

Release History
===============

4.0.1 (2018-07-23)
++++++++++++++++++

**Bugfix**

- Fix incorrect import from azure.mgmt.compute.models

4.0.0 (2018-07-20)
++++++++++++++++++

**Features**

- Model VirtualMachineScaleSetIdentity has a new parameter user_assigned_identities
- Model VirtualMachineScaleSetIPConfiguration has a new parameter application_security_groups
- Model VirtualMachineScaleSetUpdateIPConfiguration has a new parameter application_security_groups
- Model VirtualMachineIdentity has a new parameter user_assigned_identities
- Model LinuxConfiguration has a new parameter provision_vm_agent
- Model OSProfile has a new parameter allow_extension_operations
- Added operation group GalleryImagesOperations
- Added operation group GalleryImageVersionsOperations
- Added operation group GalleriesOperations
- Model UpgradeOperationHistoricalStatusInfoProperties has a new parameter rollback_info
- Model UpgradePolicy has a new parameter auto_os_upgrade_policy
- Added operation AvailabilitySetsOperations.list_by_subscription

**Breaking changes**

- Model VirtualMachineScaleSetIdentity no longer has parameter identity_ids
- Model VirtualMachineScaleSetOSDisk no longer has parameter disk_size_gb
- Model VirtualMachineScaleSetVM no longer has parameter zones
- Model VirtualMachineScaleSetUpdateOSDisk no longer has parameter disk_size_gb
- Model VirtualMachineIdentity no longer has parameter identity_ids

New default API Version is now 2018-06-01

4.0.0rc2 (2018-04-17)
+++++++++++++++++++++

**Features**

- All clients now support Azure profiles.
- Add update operation to VirtualMachineExtension operations (all ApiVersions)
- Add get_extensions operation to VirtualMachine operations (all ApiVersions)
- Support eviction policy for virtual machines inside a low priority scale set (2017-12-01)
- Add get_os_upgrade_history to VMSS operations (2017-12-01)

**Bugfixes**

- Compatibility of the sdist with wheel 0.31.0
- Fix some invalid models in Python 3 (introduced in 4.0.0rc1)

4.0.0rc1 (2018-03-21)
+++++++++++++++++++++

**General Breaking changes**

This version uses a next-generation code generator that *might* introduce breaking changes.

- Model signatures now use only keyword-argument syntax. All positional arguments must be re-written as keyword-arguments.
  To keep auto-completion in most cases, models are now generated for Python 2 and Python 3. Python 3 uses the "*" syntax for keyword-only arguments.
- Enum types now use the "str" mixin (class AzureEnum(str, Enum)) to improve the behavior when unrecognized enum values are encountered.
  While this is not a breaking change, the distinctions are important, and are documented here:
  https://docs.python.org/3/library/enum.html#others
  At a glance:

  - "is" should not be used at all.
  - "format" will return the string value, where "%s" string formatting will return `NameOfEnum.stringvalue`. Format syntax should be prefered.

- New Long Running Operation:

  - Return type changes from `msrestazure.azure_operation.AzureOperationPoller` to `msrest.polling.LROPoller`. External API is the same.
  - Return type is now **always** a `msrest.polling.LROPoller`, regardless of the optional parameters used.
  - The behavior has changed when using `raw=True`. Instead of returning the initial call result as `ClientRawResponse`,
    without polling, now this returns an LROPoller. After polling, the final resource will be returned as a `ClientRawResponse`.
  - New `polling` parameter. The default behavior is `Polling=True` which will poll using ARM algorithm. When `Polling=False`,
    the response of the initial call will be returned without polling.
  - `polling` parameter accepts instances of subclasses of `msrest.polling.PollingMethod`.
  - `add_done_callback` will no longer raise if called after polling is finished, but will instead execute the callback right away.

**Compute features**

- Support zone resilient for image/snapshots (new ApiVersion 2018-04-01)
- Add "operations" operation group
- Add availability_set.update
- Add images.update
- Add virtual_machine.update

3.1.0rc3 (2018-11-01)
+++++++++++++++++++++

**Features**

- Add VirtualMachineScaleSetNetworkConfiguration -> enable_ip_forwarding
- Add VirtualMachineScaleSetUpdateNetworkConfiguration -> enable_ip_forwarding
- Add VirtualMachineScaleSetVMProfile -> priority
- Add ApiVersion 2017-12-01 of virtual_machine_run_commands (new default)

3.1.0rc2 (2017-12-14)
+++++++++++++++++++++

**Features**

- Add User Assigned Identity parameters to VM/VMSS creation

**Bugfixes**

- Add RestrictionInfo to SKUs list (2017-09-01)
- Restore virtual_machines.run_commands (broken in rc1)

3.1.0rc1 (2017-11-27)
+++++++++++++++++++++

**Disclaimer**

This version supports Azure Profile. Meaning, you can specify specific API versions to support for each operation groups.

The default API versions of this package are now:
- 2017-03-30 for 'disks', 'virtual_machine_run_commands' and 'snapshots'
- 2017-09-01 for 'resource_skus'
- 2017-12-01 for everything else

**Python features**

- ComputeManagementClient has now a "profile" parameter, which is a dict from operation groups name to API version
- Operation groups now have access to their own models. For instance, assuming you have variable called "client",
  you can access the models for this opeations groups (according to your loaded profiles) using
  `client.virtual_machines.models`
- azure.mgmt.compute.models is deprecated. See https://aka.ms/pysdkmodels for details.

**Azure features**

- 'resource_skus' has improved 'location_info' field

3.0.1 (2017-09-26)
++++++++++++++++++

**Bugfix**

- Add missing virtual_machine_scale_set_rolling_upgrades operation group alias

3.0.0 (2017-09-26)
++++++++++++++++++

**Features**

- Availability Zones
- VMSS Rolling upgrade / patch / health status
- VM instance view APIs

**Breaking changes**

- "azure.mgmt.compute.compute" namespace is now simply "azure.mgmt.compute". If you were
  already using "azure.mgmt.compute" before, you code should still work exactly the same.
- ContainerService has now be removed and exported in azure-mgmt-containerservice

2.1.0 (2017-07-19)
++++++++++++++++++

**Features in 2017-03-30**

- Expose 'enableAcceleratedNetworking' for virtual machine and virtual machine SS. Windows GA, Linux in preview.
- Expose 'forceUpdateTag' to ensure extension gets reinstalled even there are no configuration change.

2.0.0 (2017-06-29)
++++++++++++++++++

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

- ContainerService: fixed typo in class name (ContainerServiceOchestratorTypes is now ContainerServiceOrchestratorTypes)

- Compute: breaking changes in Managed Disk API:

  - Managed field removed from Create AV Set API
  - Account Type replaced with SKU in PUT and GET Managed Disk Create API
  - OwnerId replaced by ManagedBy in GET Managed Disk API

Note that you can get the behavior of v1.0.0 by forcing the Api Version to "2016-04-30-preview" to update your package but not the code:

    ComputeManagementClient(credentials, subscription_id, api_version="2016-04-30-preview")

1.0.0 (2017-05-15)
++++++++++++++++++

- Tag 1.0.0rc2 as stable (same content)

1.0.0rc2 (2017-05-12)
+++++++++++++++++++++

**Features**

- Add Compute ApiVersion 2016-03-30 (AzureStack default)

1.0.0rc1 (2017-04-11)
+++++++++++++++++++++

**Breaking Changes**

- Container service is now in it's own client ContainerServiceClient

**Features**

To help customers with sovereign clouds (not general Azure),
this version has official multi ApiVersion support for the following resource type:

- Compute: 2015-06-15 and 2016-04-30-preview

The following resource types support one ApiVersion:

- ContainerService: 2017-01-31

0.33.0 (2017-02-03)
+++++++++++++++++++

**Features**

This release adds Managed Disk to compute. This changes the default disk creation behavior
to use the new Managed Disk feature instead of Storage.

0.32.1 (2016-11-14)
+++++++++++++++++++

* Add "Kubernetes" on Containers
* Improve technical documentation

0.32.0 (2016-11-02)
+++++++++++++++++++

**Breaking change**

New APIVersion for "container" 2016-09-30.

* several parameters (e.g. "username") now dynamically check before REST calls validity
  against a regexp. Exception will be TypeError and not CloudError anymore.

0.31.0 (2016-11-01)
+++++++++++++++++++

**Breaking change**

We renamed some "container" methods to follow Azure SDK conventions

* "container" attribute on the client is now "containers"
* "list" changed behavior, now listing containers in subscription and lost its parameter
* "list_by_resource_group" new method with the old "list" behavior

0.30.0 (2016-10-17)
+++++++++++++++++++

* Initial preview release. Based on API version 2016-03-30.


0.20.0 (2015-08-31)
+++++++++++++++++++

* Initial preview release. Based on API version 2015-05-01-preview.
