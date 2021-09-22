# Release History

## 0.15.0 (2021-09-22)

**Features**

  - Model IaasVMRestoreWithRehydrationRequest has a new parameter identity_based_restore_details
  - Model AzureSqlProtectionPolicy has a new parameter resource_guard_operation_requests
  - Model MabProtectionPolicy has a new parameter resource_guard_operation_requests
  - Model AzureFileShareProtectionPolicy has a new parameter resource_guard_operation_requests
  - Model AzureIaaSComputeVMProtectedItem has a new parameter resource_guard_operation_requests
  - Model AzureVmWorkloadSAPAseDatabaseProtectedItem has a new parameter resource_guard_operation_requests
  - Model DPMProtectedItem has a new parameter resource_guard_operation_requests
  - Model MabFileFolderProtectedItem has a new parameter resource_guard_operation_requests
  - Model AzureVmWorkloadProtectionPolicy has a new parameter resource_guard_operation_requests
  - Model AzureVmWorkloadProtectedItem has a new parameter resource_guard_operation_requests
  - Model AzureVmWorkloadSAPHanaDatabaseProtectedItem has a new parameter resource_guard_operation_requests
  - Model AzureIaaSClassicComputeVMProtectedItem has a new parameter resource_guard_operation_requests
  - Model ProtectionPolicy has a new parameter resource_guard_operation_requests
  - Model AzureFileshareProtectedItem has a new parameter resource_guard_operation_requests
  - Model AzureIaaSVMProtectedItem has a new parameter resource_guard_operation_requests
  - Model BackupResourceVaultConfig has a new parameter resource_guard_operation_requests
  - Model AzureSqlProtectedItem has a new parameter resource_guard_operation_requests
  - Model ProtectedItem has a new parameter resource_guard_operation_requests
  - Model GenericProtectedItem has a new parameter resource_guard_operation_requests
  - Model AzureVmWorkloadSQLDatabaseProtectedItem has a new parameter resource_guard_operation_requests
  - Model GenericProtectionPolicy has a new parameter resource_guard_operation_requests
  - Model AzureIaaSVMProtectionPolicy has a new parameter resource_guard_operation_requests
  - Model IaasVMRestoreRequest has a new parameter identity_based_restore_details
  - Added operation group ResourceGuardProxiesOperations
  - Added operation group BackupResourceStorageConfigsNonCRROperations
  - Added operation group ResourceGuardProxyOperations

**Breaking changes**

  - Operation SecurityPINsOperations.get has a new signature

## 0.14.0 (2021-07-26)

**Breaking changes**

  - Removed operation group BackupResourceStorageConfigsNonCRROperations

## 0.13.0 (2021-07-22)

**Features**

  - Model AzureWorkloadRestoreRequest has a new parameter target_virtual_machine_id
  - Model AzureWorkloadPointInTimeRestoreRequest has a new parameter target_virtual_machine_id
  - Model AzureFileshareProtectedItem has a new parameter health_status
  - Model AzureWorkloadSAPHanaRestoreWithRehydrateRequest has a new parameter target_virtual_machine_id
  - Model AzureWorkloadSQLRestoreRequest has a new parameter target_virtual_machine_id
  - Model AzureWorkloadSAPHanaPointInTimeRestoreWithRehydrateRequest has a new parameter target_virtual_machine_id
  - Model IaasVMRestoreRequest has a new parameter identity_info
  - Model AzureWorkloadSQLPointInTimeRestoreRequest has a new parameter target_virtual_machine_id
  - Model AzureWorkloadSAPHanaRestoreRequest has a new parameter target_virtual_machine_id
  - Model AzureWorkloadSQLPointInTimeRestoreWithRehydrateRequest has a new parameter target_virtual_machine_id
  - Model AzureWorkloadSAPHanaPointInTimeRestoreRequest has a new parameter target_virtual_machine_id
  - Model IaasVMRestoreWithRehydrationRequest has a new parameter identity_info
  - Model AzureWorkloadSQLRestoreWithRehydrateRequest has a new parameter target_virtual_machine_id
  - Model Day has a new parameter date_property
  - Added operation PrivateEndpointConnectionOperations.delete
  - Added operation PrivateEndpointConnectionOperations.put
  - Added operation ProtectionPoliciesOperations.delete
  - Added operation CrossRegionRestoreOperations.trigger
  - Added operation RecoveryServicesBackupClientOperationsMixin.bms_trigger_data_move
  - Added operation RecoveryServicesBackupClientOperationsMixin.bms_prepare_data_move
  - Added operation RecoveryServicesBackupClientOperationsMixin.move_recovery_point
  - Added operation RestoresOperations.trigger
  - Added operation group BackupResourceStorageConfigsNonCRROperations

**Breaking changes**

  - Operation RecoveryPointsRecommendedForMoveOperations.list has a new signature
  - Operation RecoveryPointsRecommendedForMoveOperations.list has a new signature
  - Operation SecurityPINsOperations.get has a new signature
  - Operation RecoveryPointsOperations.list has a new signature
  - Operation RecoveryPointsOperations.get_access_token has a new signature
  - Operation RecoveryPointsOperations.get has a new signature
  - Operation RecoveryPointsCrrOperations.list has a new signature
  - Operation ProtectionPolicyOperationStatusesOperations.get has a new signature
  - Operation ProtectionPolicyOperationResultsOperations.get has a new signature
  - Operation ProtectionPoliciesOperations.get has a new signature
  - Operation ProtectionPoliciesOperations.create_or_update has a new signature
  - Operation ProtectionIntentOperations.validate has a new signature
  - Operation ProtectionIntentOperations.get has a new signature
  - Operation ProtectionIntentOperations.delete has a new signature
  - Operation ProtectionIntentOperations.create_or_update has a new signature
  - Operation ProtectionContainersOperations.unregister has a new signature
  - Operation ProtectionContainersOperations.register has a new signature
  - Operation ProtectionContainersOperations.refresh has a new signature
  - Operation ProtectionContainersOperations.inquire has a new signature
  - Operation ProtectionContainersOperations.get has a new signature
  - Operation ProtectionContainerRefreshOperationResultsOperations.get has a new signature
  - Operation ProtectionContainerOperationResultsOperations.get has a new signature
  - Operation ProtectedItemsOperations.get has a new signature
  - Operation ProtectedItemsOperations.delete has a new signature
  - Operation ProtectedItemsOperations.create_or_update has a new signature
  - Operation ProtectedItemOperationStatusesOperations.get has a new signature
  - Operation ProtectedItemOperationResultsOperations.get has a new signature
  - Operation ProtectableContainersOperations.list has a new signature
  - Operation PrivateEndpointOperations.get_operation_status has a new signature
  - Operation PrivateEndpointConnectionOperations.get has a new signature
  - Operation OperationOperations.validate has a new signature
  - Operation JobsOperations.export has a new signature
  - Operation JobOperationResultsOperations.get has a new signature
  - Operation JobDetailsOperations.get has a new signature
  - Operation JobCancellationsOperations.trigger has a new signature
  - Operation ItemLevelRecoveryConnectionsOperations.revoke has a new signature
  - Operation ItemLevelRecoveryConnectionsOperations.provision has a new signature
  - Operation FeatureSupportOperations.validate has a new signature
  - Operation ExportJobsOperationResultsOperations.get has a new signature
  - Operation CrrOperationStatusOperations.get has a new signature
  - Operation CrrOperationResultsOperations.get has a new signature
  - Operation BackupsOperations.trigger has a new signature
  - Operation BackupWorkloadItemsOperations.list has a new signature
  - Operation BackupUsageSummariesOperations.list has a new signature
  - Operation BackupUsageSummariesCRROperations.list has a new signature
  - Operation BackupStatusOperations.get has a new signature
  - Operation BackupResourceVaultConfigsOperations.update has a new signature
  - Operation BackupResourceVaultConfigsOperations.put has a new signature
  - Operation BackupResourceVaultConfigsOperations.get has a new signature
  - Operation BackupResourceStorageConfigsOperations.update has a new signature
  - Operation BackupResourceStorageConfigsOperations.patch has a new signature
  - Operation BackupResourceStorageConfigsOperations.get has a new signature
  - Operation BackupResourceEncryptionConfigsOperations.update has a new signature
  - Operation BackupResourceEncryptionConfigsOperations.get has a new signature
  - Operation BackupProtectionIntentOperations.list has a new signature
  - Operation BackupProtectionContainersOperations.list has a new signature
  - Operation BackupProtectedItemsOperations.list has a new signature
  - Operation BackupProtectedItemsCrrOperations.list has a new signature
  - Operation BackupProtectableItemsOperations.list has a new signature
  - Operation BackupPoliciesOperations.list has a new signature
  - Operation BackupOperationStatusesOperations.get has a new signature
  - Operation BackupOperationResultsOperations.get has a new signature
  - Operation BackupJobsOperations.list has a new signature
  - Operation BackupEnginesOperations.list has a new signature
  - Operation BackupEnginesOperations.get has a new signature
  - Operation BMSPrepareDataMoveOperationResultOperations.get has a new signature
  - Operation AadPropertiesOperations.get has a new signature
  - Model Day no longer has parameter date
  - Operation BackupCrrJobsOperations.list has a new signature
  - Operation BackupCrrJobDetailsOperations.get has a new signature
  - Operation Operations.list has a new signature
  - Removed operation PrivateEndpointConnectionOperations.begin_delete
  - Removed operation PrivateEndpointConnectionOperations.begin_put
  - Removed operation ProtectionPoliciesOperations.begin_delete
  - Removed operation CrossRegionRestoreOperations.begin_trigger
  - Removed operation RecoveryServicesBackupClientOperationsMixin.begin_bms_prepare_data_move
  - Removed operation RecoveryServicesBackupClientOperationsMixin.begin_bms_trigger_data_move
  - Removed operation RecoveryServicesBackupClientOperationsMixin.begin_move_recovery_point
  - Removed operation RestoresOperations.begin_trigger

## 0.12.0 (2021-05-26)

**Features**

  - Model Day has a new parameter date_property
  - Model AzureFileshareProtectedItem has a new parameter health_status
  - Added operation ProtectionPoliciesOperations.delete
  - Added operation PrivateEndpointConnectionOperations.put
  - Added operation PrivateEndpointConnectionOperations.delete
  - Added operation RestoresOperations.trigger
  - Added operation CrossRegionRestoreOperations.trigger
  - Added operation RecoveryServicesBackupClientOperationsMixin.bms_trigger_data_move
  - Added operation RecoveryServicesBackupClientOperationsMixin.move_recovery_point
  - Added operation RecoveryServicesBackupClientOperationsMixin.bms_prepare_data_move
  - Added operation group BackupUsageSummariesCRROperations

**Breaking changes**

  - Operation RecoveryPointsRecommendedForMoveOperations.list has a new signature
  - Operation RecoveryPointsRecommendedForMoveOperations.list has a new signature
  - Operation SecurityPINsOperations.get has a new signature
  - Operation RecoveryPointsOperations.list has a new signature
  - Operation RecoveryPointsOperations.get_access_token has a new signature
  - Operation RecoveryPointsOperations.get has a new signature
  - Operation RecoveryPointsCrrOperations.list has a new signature
  - Operation ProtectionPolicyOperationStatusesOperations.get has a new signature
  - Operation ProtectionPolicyOperationResultsOperations.get has a new signature
  - Operation ProtectionPoliciesOperations.get has a new signature
  - Operation ProtectionPoliciesOperations.create_or_update has a new signature
  - Operation ProtectionIntentOperations.validate has a new signature
  - Operation ProtectionIntentOperations.get has a new signature
  - Operation ProtectionIntentOperations.delete has a new signature
  - Operation ProtectionIntentOperations.create_or_update has a new signature
  - Operation ProtectionContainersOperations.unregister has a new signature
  - Operation ProtectionContainersOperations.register has a new signature
  - Operation ProtectionContainersOperations.refresh has a new signature
  - Operation ProtectionContainersOperations.inquire has a new signature
  - Operation ProtectionContainersOperations.get has a new signature
  - Operation ProtectionContainerRefreshOperationResultsOperations.get has a new signature
  - Operation ProtectionContainerOperationResultsOperations.get has a new signature
  - Operation ProtectedItemsOperations.get has a new signature
  - Operation ProtectedItemsOperations.delete has a new signature
  - Operation ProtectedItemsOperations.create_or_update has a new signature
  - Operation ProtectedItemOperationStatusesOperations.get has a new signature
  - Operation ProtectedItemOperationResultsOperations.get has a new signature
  - Operation ProtectableContainersOperations.list has a new signature
  - Operation PrivateEndpointOperations.get_operation_status has a new signature
  - Operation PrivateEndpointConnectionOperations.get has a new signature
  - Operation OperationOperations.validate has a new signature
  - Operation JobsOperations.export has a new signature
  - Operation JobOperationResultsOperations.get has a new signature
  - Operation JobDetailsOperations.get has a new signature
  - Operation JobCancellationsOperations.trigger has a new signature
  - Operation ItemLevelRecoveryConnectionsOperations.revoke has a new signature
  - Operation ItemLevelRecoveryConnectionsOperations.provision has a new signature
  - Operation FeatureSupportOperations.validate has a new signature
  - Operation ExportJobsOperationResultsOperations.get has a new signature
  - Operation CrrOperationStatusOperations.get has a new signature
  - Operation CrrOperationResultsOperations.get has a new signature
  - Operation BackupsOperations.trigger has a new signature
  - Operation BackupWorkloadItemsOperations.list has a new signature
  - Operation BackupUsageSummariesOperations.list has a new signature
  - Operation BackupStatusOperations.get has a new signature
  - Operation BackupResourceVaultConfigsOperations.update has a new signature
  - Operation BackupResourceVaultConfigsOperations.put has a new signature
  - Operation BackupResourceVaultConfigsOperations.get has a new signature
  - Operation BackupResourceStorageConfigsOperations.update has a new signature
  - Operation BackupResourceStorageConfigsOperations.patch has a new signature
  - Operation BackupResourceStorageConfigsOperations.get has a new signature
  - Operation BackupResourceEncryptionConfigsOperations.update has a new signature
  - Operation BackupResourceEncryptionConfigsOperations.get has a new signature
  - Operation BackupProtectionIntentOperations.list has a new signature
  - Operation BackupProtectionContainersOperations.list has a new signature
  - Operation BackupProtectedItemsOperations.list has a new signature
  - Operation BackupProtectedItemsCrrOperations.list has a new signature
  - Operation BackupProtectableItemsOperations.list has a new signature
  - Operation BackupPoliciesOperations.list has a new signature
  - Operation BackupOperationStatusesOperations.get has a new signature
  - Operation BackupOperationResultsOperations.get has a new signature
  - Operation BackupJobsOperations.list has a new signature
  - Operation BackupEnginesOperations.list has a new signature
  - Operation BackupEnginesOperations.get has a new signature
  - Operation BMSPrepareDataMoveOperationResultOperations.get has a new signature
  - Operation AadPropertiesOperations.get has a new signature
  - Model Day no longer has parameter date
  - Operation BackupCrrJobDetailsOperations.get has a new signature
  - Operation Operations.list has a new signature
  - Operation BackupCrrJobsOperations.list has a new signature
  - Removed operation ProtectionPoliciesOperations.begin_delete
  - Removed operation PrivateEndpointConnectionOperations.begin_delete
  - Removed operation PrivateEndpointConnectionOperations.begin_put
  - Removed operation RestoresOperations.begin_trigger
  - Removed operation CrossRegionRestoreOperations.begin_trigger
  - Removed operation RecoveryServicesBackupClientOperationsMixin.begin_move_recovery_point
  - Removed operation RecoveryServicesBackupClientOperationsMixin.begin_bms_prepare_data_move
  - Removed operation RecoveryServicesBackupClientOperationsMixin.begin_bms_trigger_data_move

## 0.11.0 (2020-12-28)

**Features**

  - Model IaasVMRecoveryPoint has a new parameter zones
  - Model IaasVMRestoreRequest has a new parameter zones

## 0.10.0 (2020-12-08)

**Features**

  - Model IaasVMRestoreRequest has a new parameter disk_encryption_set_id
  - Model IaasVMRestoreRequest has a new parameter restore_with_managed_disks
  - Model BackupResourceConfig has a new parameter cross_region_restore_flag
  - Model AzureFileshareProtectedItem has a new parameter health_status
  - Added operation RecoveryPointsOperations.get_access_token
  - Added operation group AadPropertiesOperations
  - Added operation group CrossRegionRestoreOperations
  - Added operation group BackupCrrJobDetailsOperations
  - Added operation group PrivateEndpointOperations
  - Added operation group BackupCrrJobsOperations
  - Added operation group RecoveryPointsCrrOperations
  - Added operation group CrrOperationResultsOperations
  - Added operation group CrrOperationStatusOperations
  - Added operation group BackupProtectedItemsCrrOperations

**Breaking changes**

  - Removed operation RecoveryServicesBackupClientOperationsMixin.get_operation_status1

## 0.9.0 (2020-12-07)

**Features**

  - Model AzureFileshareProtectedItem has a new parameter kpis_healths
  - Model AzureIaaSVMProtectedItem has a new parameter kpis_healths
  - Model AzureIaaSClassicComputeVMProtectedItem has a new parameter kpis_healths
  - Model AzureVmWorkloadProtectedItem has a new parameter kpis_healths
  - Model AzureVmWorkloadSAPHanaDatabaseProtectedItem has a new parameter kpis_healths
  - Model AzureIaaSComputeVMProtectedItem has a new parameter kpis_healths
  - Model AzureVmWorkloadSAPAseDatabaseProtectedItem has a new parameter kpis_healths
  - Model AzureVmWorkloadSQLDatabaseProtectedItem has a new parameter kpis_healths
  - Added operation RecoveryServicesBackupClientOperationsMixin.bms_prepare_data_move
  - Added operation RecoveryServicesBackupClientOperationsMixin.bms_trigger_data_move
  - Added operation RecoveryServicesBackupClientOperationsMixin.get_operation_status1
  - Added operation group BackupResourceEncryptionConfigsOperations
  - Added operation group BMSPrepareDataMoveOperationResultOperations

**Breaking changes**

  - Model AzureFileshareProtectedItem no longer has parameter health_status
  - Model AzureFileshareProtectedItem no longer has parameter health_details
  - Model AzureVmWorkloadProtectedItem no longer has parameter health_status
  - Model AzureVmWorkloadProtectedItem no longer has parameter health_details
  - Model AzureVmWorkloadSAPHanaDatabaseProtectedItem no longer has parameter health_status
  - Model AzureVmWorkloadSAPHanaDatabaseProtectedItem no longer has parameter health_details
  - Model AzureVmWorkloadSAPAseDatabaseProtectedItem no longer has parameter health_status
  - Model AzureVmWorkloadSAPAseDatabaseProtectedItem no longer has parameter health_details
  - Model AzureVmWorkloadSQLDatabaseProtectedItem no longer has parameter health_status
  - Model AzureVmWorkloadSQLDatabaseProtectedItem no longer has parameter health_details

## 0.8.0 (2020-06-05)

**Features**

  - Model AzureVmWorkloadSAPHanaDatabaseProtectedItem has a new parameter health_details
  - Model AzureVmWorkloadSAPHanaDatabaseProtectedItem has a new parameter health_status
  - Model AzureVmWorkloadSQLDatabaseProtectedItem has a new parameter health_details
  - Model AzureVmWorkloadSQLDatabaseProtectedItem has a new parameter health_status
  - Model AzureFileshareProtectedItem has a new parameter health_details
  - Model AzureVmWorkloadSAPAseDatabaseProtectedItem has a new parameter health_details
  - Model AzureVmWorkloadSAPAseDatabaseProtectedItem has a new parameter health_status
  - Model AzureVmWorkloadProtectedItem has a new parameter health_details
  - Model AzureVmWorkloadProtectedItem has a new parameter health_status

## 0.7.0 (2020-03-24)

**Features**

  - Added operation BackupResourceVaultConfigsOperations.put
  - Added operation group RecoveryServicesBackupClientOperationsMixin
  - Added operation group PrivateEndpointConnectionOperations

## 0.6.0 (2020-01-14)

**Features**

  - Model TargetRestoreInfo has a new parameter
    target_directory_for_file_restore
  - Model AzureIaaSVMProtectionPolicy has a new parameter
    instant_rp_details

## 0.5.0 (2019-11-21)

**Features**

  - Model AzureVmWorkloadProtectedItem has a new parameter
    deferred_delete_time_remaining
  - Model AzureVmWorkloadProtectedItem has a new parameter
    is_deferred_delete_schedule_upcoming
  - Model AzureVmWorkloadProtectedItem has a new parameter is_rehydrate
  - Model AzureVmWorkloadProtectedItem has a new parameter
    deferred_delete_time_in_utc
  - Model AzureVmWorkloadProtectedItem has a new parameter
    is_scheduled_for_deferred_delete
  - Model AzureFileshareProtectedItemExtendedInfo has a new parameter
    resource_state
  - Model AzureFileshareProtectedItemExtendedInfo has a new parameter
    resource_state_sync_time
  - Model AzureIaaSClassicComputeVMProtectedItem has a new parameter
    deferred_delete_time_remaining
  - Model AzureIaaSClassicComputeVMProtectedItem has a new parameter
    is_deferred_delete_schedule_upcoming
  - Model AzureIaaSClassicComputeVMProtectedItem has a new parameter
    extended_properties
  - Model AzureIaaSClassicComputeVMProtectedItem has a new parameter
    is_rehydrate
  - Model AzureIaaSClassicComputeVMProtectedItem has a new parameter
    deferred_delete_time_in_utc
  - Model AzureIaaSClassicComputeVMProtectedItem has a new parameter
    is_scheduled_for_deferred_delete
  - Model AzureWorkloadSAPHanaPointInTimeRestoreRequest has a new
    parameter recovery_mode
  - Model AzureVmWorkloadProtectionPolicy has a new parameter
    make_policy_consistent
  - Model AzureIaaSVMProtectedItem has a new parameter
    deferred_delete_time_remaining
  - Model AzureIaaSVMProtectedItem has a new parameter
    is_deferred_delete_schedule_upcoming
  - Model AzureIaaSVMProtectedItem has a new parameter
    extended_properties
  - Model AzureIaaSVMProtectedItem has a new parameter is_rehydrate
  - Model AzureIaaSVMProtectedItem has a new parameter
    deferred_delete_time_in_utc
  - Model AzureIaaSVMProtectedItem has a new parameter
    is_scheduled_for_deferred_delete
  - Model DPMProtectedItem has a new parameter
    deferred_delete_time_in_utc
  - Model DPMProtectedItem has a new parameter is_rehydrate
  - Model DPMProtectedItem has a new parameter
    deferred_delete_time_remaining
  - Model DPMProtectedItem has a new parameter
    is_deferred_delete_schedule_upcoming
  - Model AzureWorkloadRestoreRequest has a new parameter recovery_mode
  - Model AzureWorkloadSAPHanaRestoreRequest has a new parameter
    recovery_mode
  - Model ProtectedItem has a new parameter
    deferred_delete_time_remaining
  - Model ProtectedItem has a new parameter
    is_deferred_delete_schedule_upcoming
  - Model ProtectedItem has a new parameter is_rehydrate
  - Model ProtectedItem has a new parameter
    deferred_delete_time_in_utc
  - Model ProtectedItem has a new parameter
    is_scheduled_for_deferred_delete
  - Model AzureWorkloadSQLRestoreRequest has a new parameter
    recovery_mode
  - Model InquiryValidation has a new parameter additional_detail
  - Model AzureVmWorkloadSQLDatabaseProtectedItem has a new parameter
    deferred_delete_time_remaining
  - Model AzureVmWorkloadSQLDatabaseProtectedItem has a new parameter
    is_deferred_delete_schedule_upcoming
  - Model AzureVmWorkloadSQLDatabaseProtectedItem has a new parameter
    is_rehydrate
  - Model AzureVmWorkloadSQLDatabaseProtectedItem has a new parameter
    deferred_delete_time_in_utc
  - Model AzureVmWorkloadSQLDatabaseProtectedItem has a new parameter
    is_scheduled_for_deferred_delete
  - Model AzureVmWorkloadSAPAseDatabaseProtectedItem has a new parameter
    deferred_delete_time_remaining
  - Model AzureVmWorkloadSAPAseDatabaseProtectedItem has a new parameter
    is_deferred_delete_schedule_upcoming
  - Model AzureVmWorkloadSAPAseDatabaseProtectedItem has a new parameter
    is_rehydrate
  - Model AzureVmWorkloadSAPAseDatabaseProtectedItem has a new parameter
    deferred_delete_time_in_utc
  - Model AzureVmWorkloadSAPAseDatabaseProtectedItem has a new parameter
    is_scheduled_for_deferred_delete
  - Model AzureWorkloadSQLPointInTimeRestoreRequest has a new parameter
    recovery_mode
  - Model AzureIaaSComputeVMProtectedItem has a new parameter
    deferred_delete_time_remaining
  - Model AzureIaaSComputeVMProtectedItem has a new parameter
    is_deferred_delete_schedule_upcoming
  - Model AzureIaaSComputeVMProtectedItem has a new parameter
    extended_properties
  - Model AzureIaaSComputeVMProtectedItem has a new parameter
    is_rehydrate
  - Model AzureIaaSComputeVMProtectedItem has a new parameter
    deferred_delete_time_in_utc
  - Model AzureIaaSComputeVMProtectedItem has a new parameter
    is_scheduled_for_deferred_delete
  - Model IaasVMRestoreRequest has a new parameter
    restore_disk_lun_list
  - Model AzureFileShareRecoveryPoint has a new parameter
    recovery_point_size_in_gb
  - Model BackupResourceVaultConfig has a new parameter
    soft_delete_feature_state
  - Model AzureVmWorkloadSAPHanaDatabaseProtectedItem has a new
    parameter deferred_delete_time_remaining
  - Model AzureVmWorkloadSAPHanaDatabaseProtectedItem has a new
    parameter is_deferred_delete_schedule_upcoming
  - Model AzureVmWorkloadSAPHanaDatabaseProtectedItem has a new
    parameter is_rehydrate
  - Model AzureVmWorkloadSAPHanaDatabaseProtectedItem has a new
    parameter deferred_delete_time_in_utc
  - Model AzureVmWorkloadSAPHanaDatabaseProtectedItem has a new
    parameter is_scheduled_for_deferred_delete
  - Model MabFileFolderProtectedItem has a new parameter
    last_backup_time
  - Model MabFileFolderProtectedItem has a new parameter
    deferred_delete_time_remaining
  - Model MabFileFolderProtectedItem has a new parameter
    is_deferred_delete_schedule_upcoming
  - Model MabFileFolderProtectedItem has a new parameter is_rehydrate
  - Model MabFileFolderProtectedItem has a new parameter
    deferred_delete_time_in_utc
  - Model IaasVMRecoveryPoint has a new parameter
    recovery_point_disk_configuration
  - Model GenericProtectedItem has a new parameter
    deferred_delete_time_remaining
  - Model GenericProtectedItem has a new parameter
    is_deferred_delete_schedule_upcoming
  - Model GenericProtectedItem has a new parameter is_rehydrate
  - Model GenericProtectedItem has a new parameter
    deferred_delete_time_in_utc
  - Model GenericProtectedItem has a new parameter
    is_scheduled_for_deferred_delete
  - Model AzureWorkloadPointInTimeRestoreRequest has a new parameter
    recovery_mode
  - Model ExportJobsOperationResultInfo has a new parameter
    excel_file_blob_sas_key
  - Model ExportJobsOperationResultInfo has a new parameter
    excel_file_blob_url
  - Model AzureFileshareProtectedItem has a new parameter
    deferred_delete_time_remaining
  - Model AzureFileshareProtectedItem has a new parameter
    is_deferred_delete_schedule_upcoming
  - Model AzureFileshareProtectedItem has a new parameter is_rehydrate
  - Model AzureFileshareProtectedItem has a new parameter
    deferred_delete_time_in_utc
  - Model AzureFileshareProtectedItem has a new parameter
    is_scheduled_for_deferred_delete
  - Model AzureSqlProtectedItem has a new parameter
    deferred_delete_time_remaining
  - Model AzureSqlProtectedItem has a new parameter
    is_deferred_delete_schedule_upcoming
  - Model AzureSqlProtectedItem has a new parameter is_rehydrate
  - Model AzureSqlProtectedItem has a new parameter
    deferred_delete_time_in_utc
  - Model AzureSqlProtectedItem has a new parameter
    is_scheduled_for_deferred_delete

**General Breaking changes**

This version uses a next-generation code generator that might introduce
breaking changes if from some import. In summary, some modules were
incorrectly visible/importable and have been renamed. This fixed several
issues caused by usage of classes that were not supposed to be used in
the first place. RecoveryServicesBackupClient cannot be imported from
azure.mgmt.recoveryservicesbackup.recovery_services_backup_client
anymore (import from azure.mgmt.recoveryservicesbackup works like
before) RecoveryServicesBackupClientConfiguration import has been moved
from
azure.mgmt.recoveryservicesbackup.recovery_services_backup_client to
azure.mgmt.recoveryservicesbackup A model MyClass from a "models"
sub-module cannot be imported anymore using
azure.mgmt.recoveryservicesbackup.models.my_class (import from
azure.mgmt.recoveryservicesbackup.models works like before) An operation
class MyClassOperations from an operations sub-module cannot be imported
anymore using
azure.mgmt.recoveryservicesbackup.operations.my_class_operations
(import from azure.mgmt.recoveryservicesbackup.operations works like
before) Last but not least, HTTP connection pooling is now enabled by
default. You should always use a client as a context manager, or call
close(), or use no more than one client per process.

## 0.4.0 (2019-05-21)

**Features**

  - Model AzureWorkloadRestoreRequest has a new parameter target_info
  - Model AzureVmWorkloadSAPHanaDatabaseProtectableItem has a new
    parameter is_auto_protected
  - Model AzureVmWorkloadSAPHanaSystemProtectableItem has a new
    parameter is_auto_protected
  - Model AzureIaaSVMJobTaskDetails has a new parameter
    task_execution_details
  - Model AzureWorkloadContainer has a new parameter operation_type
  - Model AzureVmWorkloadSQLInstanceProtectableItem has a new parameter
    is_auto_protected
  - Model AzureIaaSVMJobExtendedInfo has a new parameter
    estimated_remaining_duration
  - Model AzureVmWorkloadSQLAvailabilityGroupProtectableItem has a new
    parameter is_auto_protected
  - Model AzureVmWorkloadProtectableItem has a new parameter
    is_auto_protected
  - Model AzureVMAppContainerProtectionContainer has a new parameter
    operation_type
  - Model AzureSQLAGWorkloadContainerProtectionContainer has a new
    parameter operation_type
  - Model AzureVmWorkloadSQLDatabaseProtectableItem has a new parameter
    is_auto_protected
  - Added operation BackupResourceStorageConfigsOperations.patch
  - Added operation ProtectionIntentOperations.delete
  - Added operation ProtectionIntentOperations.get
  - Added operation group BackupProtectionIntentOperations
  - Added operation group OperationOperations

## 0.3.0 (2018-06-27)

**Features**

  - SAP HANA contract changes (new filters added to existing API's.).
    This feature is still in development phase and not open for usage
    yet.
  - Instant RP field added in create policy.
  - Comments added for some contracts.

**Python details**

  - Model DPMProtectedItem has a new parameter create_mode
  - Model MabFileFolderProtectedItem has a new parameter create_mode
  - Model AzureIaaSClassicComputeVMProtectedItem has a new parameter
    create_mode
  - Model AzureWorkloadContainer has a new parameter workload_type
  - Model AzureIaaSVMProtectionPolicy has a new parameter
    instant_rp_retention_range_in_days
  - Model AzureFileshareProtectedItem has a new parameter create_mode
  - Model AzureSQLAGWorkloadContainerProtectionContainer has a new
    parameter workload_type
  - Model AzureSqlProtectedItem has a new parameter create_mode
  - Model AzureIaaSVMJobExtendedInfo has a new parameter
    internal_property_bag
  - Model KeyAndSecretDetails has a new parameter encryption_mechanism
  - Model AzureIaaSVMProtectedItem has a new parameter create_mode
  - Model AzureVMAppContainerProtectionContainer has a new parameter
    workload_type
  - Model AzureVmWorkloadSQLDatabaseProtectedItem has a new parameter
    create_mode
  - Model IaasVMRecoveryPoint has a new parameter os_type
  - Model ProtectionPolicyQueryObject has a new parameter workload_type
  - Model AzureIaaSComputeVMProtectedItem has a new parameter
    create_mode
  - Model Settings has a new parameter is_compression
  - Model GenericProtectedItem has a new parameter create_mode
  - Model AzureWorkloadJob has a new parameter workload_type
  - Model ProtectedItem has a new parameter create_mode
  - Operation ProtectionContainersOperations.inquire has a new "filter"
    parameter

## 0.2.0 (2018-05-25)

**Features**

  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance

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

**Bugfixes**

  - Compatibility of the sdist with wheel 0.31.0

## 0.1.2 (2019-03-12)

  - Updating permissible versions of the msrestazure package to unblock
    [Azure/azure-cli#6973](https://github.com/Azure/azure-cli/issues/6973).

## 0.1.1 (2017-08-09)

**Bug fixes**

  - Fix duration parsing (#1214)

## 0.1.0 (2017-06-05)

  - Initial Release
