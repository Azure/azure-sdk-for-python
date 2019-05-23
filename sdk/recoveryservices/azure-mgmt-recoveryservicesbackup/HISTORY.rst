.. :changelog:

Release History
===============

0.4.0 (2019-05-21)
++++++++++++++++++

**Features**

- Model AzureWorkloadRestoreRequest has a new parameter target_info
- Model AzureVmWorkloadSAPHanaDatabaseProtectableItem has a new parameter is_auto_protected
- Model AzureVmWorkloadSAPHanaSystemProtectableItem has a new parameter is_auto_protected
- Model AzureIaaSVMJobTaskDetails has a new parameter task_execution_details
- Model AzureWorkloadContainer has a new parameter operation_type
- Model AzureVmWorkloadSQLInstanceProtectableItem has a new parameter is_auto_protected
- Model AzureIaaSVMJobExtendedInfo has a new parameter estimated_remaining_duration
- Model AzureVmWorkloadSQLAvailabilityGroupProtectableItem has a new parameter is_auto_protected
- Model AzureVmWorkloadProtectableItem has a new parameter is_auto_protected
- Model AzureVMAppContainerProtectionContainer has a new parameter operation_type
- Model AzureSQLAGWorkloadContainerProtectionContainer has a new parameter operation_type
- Model AzureVmWorkloadSQLDatabaseProtectableItem has a new parameter is_auto_protected
- Added operation BackupResourceStorageConfigsOperations.patch
- Added operation ProtectionIntentOperations.delete
- Added operation ProtectionIntentOperations.get
- Added operation group BackupProtectionIntentOperations
- Added operation group OperationOperations

0.3.0 (2018-06-27)
++++++++++++++++++

**Features**

- SAP HANA contract changes (new filters added to existing API's.). This feature is still in development phase and not open for usage yet.
- Instant RP field added in create policy.
- Comments added for some contracts.

**Python details**

- Model DPMProtectedItem has a new parameter create_mode
- Model MabFileFolderProtectedItem has a new parameter create_mode
- Model AzureIaaSClassicComputeVMProtectedItem has a new parameter create_mode
- Model AzureWorkloadContainer has a new parameter workload_type
- Model AzureIaaSVMProtectionPolicy has a new parameter instant_rp_retention_range_in_days
- Model AzureFileshareProtectedItem has a new parameter create_mode
- Model AzureSQLAGWorkloadContainerProtectionContainer has a new parameter workload_type
- Model AzureSqlProtectedItem has a new parameter create_mode
- Model AzureIaaSVMJobExtendedInfo has a new parameter internal_property_bag
- Model KeyAndSecretDetails has a new parameter encryption_mechanism
- Model AzureIaaSVMProtectedItem has a new parameter create_mode
- Model AzureVMAppContainerProtectionContainer has a new parameter workload_type
- Model AzureVmWorkloadSQLDatabaseProtectedItem has a new parameter create_mode
- Model IaasVMRecoveryPoint has a new parameter os_type
- Model ProtectionPolicyQueryObject has a new parameter workload_type
- Model AzureIaaSComputeVMProtectedItem has a new parameter create_mode
- Model Settings has a new parameter is_compression
- Model GenericProtectedItem has a new parameter create_mode
- Model AzureWorkloadJob has a new parameter workload_type
- Model ProtectedItem has a new parameter create_mode
- Operation ProtectionContainersOperations.inquire has a new "filter" parameter

0.2.0 (2018-05-25)
++++++++++++++++++

**Features**

- Client class can be used as a context manager to keep the underlying HTTP session open for performance

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

**Bugfixes**

- Compatibility of the sdist with wheel 0.31.0

0.1.2 (2019-03-12)
++++++++++++++++++

* Updating permissible versions of the msrestazure package to unblock `Azure/azure-cli#6973 <https://github.com/Azure/azure-cli/issues/6973>`_.


0.1.1 (2017-08-09)
++++++++++++++++++

**Bug fixes**

* Fix duration parsing (#1214)

0.1.0 (2017-06-05)
++++++++++++++++++

* Initial Release