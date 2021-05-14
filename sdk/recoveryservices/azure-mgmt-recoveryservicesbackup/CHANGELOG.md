# Release History

## 1.0.0 (2021-05-14)

**Features**

  - Model AzureWorkloadSQLPointInTimeRecoveryPoint has a new parameter recovery_point_tier_details
  - Model AzureWorkloadSQLPointInTimeRecoveryPoint has a new parameter recovery_point_move_readiness_info
  - Model AzureWorkloadSAPHanaRecoveryPoint has a new parameter recovery_point_tier_details
  - Model AzureWorkloadSAPHanaRecoveryPoint has a new parameter recovery_point_move_readiness_info
  - Model AzureWorkloadSQLRestoreRequest has a new parameter target_virtual_machine_id
  - Model AzureWorkloadSQLPointInTimeRestoreRequest has a new parameter target_virtual_machine_id
  - Model AzureWorkloadSAPHanaPointInTimeRestoreRequest has a new parameter target_virtual_machine_id
  - Model AzureWorkloadRecoveryPoint has a new parameter recovery_point_tier_details
  - Model AzureWorkloadRecoveryPoint has a new parameter recovery_point_move_readiness_info
  - Model AzureWorkloadPointInTimeRecoveryPoint has a new parameter recovery_point_tier_details
  - Model AzureWorkloadPointInTimeRecoveryPoint has a new parameter recovery_point_move_readiness_info
  - Model AzureWorkloadSAPHanaRestoreRequest has a new parameter target_virtual_machine_id
  - Model BMSRPQueryObject has a new parameter move_ready_rp_only
  - Model AzureWorkloadPointInTimeRestoreRequest has a new parameter target_virtual_machine_id
  - Model AzureWorkloadSQLRecoveryPoint has a new parameter recovery_point_tier_details
  - Model AzureWorkloadSQLRecoveryPoint has a new parameter recovery_point_move_readiness_info
  - Model IaasVMRecoveryPoint has a new parameter recovery_point_move_readiness_info
  - Model Day has a new parameter date
  - Model AzureWorkloadSAPHanaPointInTimeRecoveryPoint has a new parameter recovery_point_tier_details
  - Model AzureWorkloadSAPHanaPointInTimeRecoveryPoint has a new parameter recovery_point_move_readiness_info
  - Model AzureWorkloadRestoreRequest has a new parameter target_virtual_machine_id
  - Added operation PrivateEndpointConnectionOperations.begin_put
  - Added operation PrivateEndpointConnectionOperations.begin_delete
  - Added operation RecoveryServicesBackupClientOperationsMixin.begin_bms_trigger_data_move
  - Added operation RecoveryServicesBackupClientOperationsMixin.begin_move_recovery_point
  - Added operation RecoveryServicesBackupClientOperationsMixin.begin_bms_prepare_data_move
  - Added operation CrossRegionRestoreOperations.begin_trigger
  - Added operation ProtectionPoliciesOperations.begin_delete
  - Added operation RestoresOperations.begin_trigger
  - Added operation group RecoveryPointsRecommendedForMoveOperations

**Breaking changes**

  - Operation BMSPrepareDataMoveOperationResultOperations.get has a new signature
  - Operation BackupEnginesOperations.get has a new signature
  - Operation BackupEnginesOperations.list has a new signature
  - Operation BackupJobsOperations.list has a new signature
  - Operation BackupOperationResultsOperations.get has a new signature
  - Operation BackupOperationStatusesOperations.get has a new signature
  - Operation BackupPoliciesOperations.list has a new signature
  - Operation BackupProtectableItemsOperations.list has a new signature
  - Operation BackupProtectedItemsCrrOperations.list has a new signature
  - Operation BackupProtectedItemsOperations.list has a new signature
  - Operation BackupProtectionContainersOperations.list has a new signature
  - Operation BackupProtectionIntentOperations.list has a new signature
  - Operation BackupResourceEncryptionConfigsOperations.get has a new signature
  - Operation BackupResourceEncryptionConfigsOperations.update has a new signature
  - Operation BackupResourceStorageConfigsOperations.get has a new signature
  - Operation BackupResourceStorageConfigsOperations.patch has a new signature
  - Operation BackupResourceStorageConfigsOperations.update has a new signature
  - Operation BackupResourceVaultConfigsOperations.get has a new signature
  - Operation BackupResourceVaultConfigsOperations.put has a new signature
  - Operation BackupResourceVaultConfigsOperations.update has a new signature
  - Operation BackupStatusOperations.get has a new signature
  - Operation BackupUsageSummariesOperations.list has a new signature
  - Operation BackupWorkloadItemsOperations.list has a new signature
  - Operation BackupsOperations.trigger has a new signature
  - Operation CrrOperationResultsOperations.get has a new signature
  - Operation CrrOperationStatusOperations.get has a new signature
  - Operation ExportJobsOperationResultsOperations.get has a new signature
  - Operation FeatureSupportOperations.validate has a new signature
  - Operation ItemLevelRecoveryConnectionsOperations.provision has a new signature
  - Operation ItemLevelRecoveryConnectionsOperations.revoke has a new signature
  - Operation JobCancellationsOperations.trigger has a new signature
  - Operation JobDetailsOperations.get has a new signature
  - Operation JobOperationResultsOperations.get has a new signature
  - Operation JobsOperations.export has a new signature
  - Operation OperationOperations.validate has a new signature
  - Operation PrivateEndpointOperations.get_operation_status has a new signature
  - Operation ProtectableContainersOperations.list has a new signature
  - Operation ProtectedItemOperationResultsOperations.get has a new signature
  - Operation ProtectedItemOperationStatusesOperations.get has a new signature
  - Operation ProtectedItemsOperations.create_or_update has a new signature
  - Operation ProtectedItemsOperations.delete has a new signature
  - Operation ProtectedItemsOperations.get has a new signature
  - Operation ProtectionContainerOperationResultsOperations.get has a new signature
  - Operation ProtectionContainerRefreshOperationResultsOperations.get has a new signature
  - Operation ProtectionContainersOperations.get has a new signature
  - Operation ProtectionContainersOperations.inquire has a new signature
  - Operation ProtectionContainersOperations.refresh has a new signature
  - Operation ProtectionContainersOperations.register has a new signature
  - Operation ProtectionContainersOperations.unregister has a new signature
  - Operation ProtectionIntentOperations.create_or_update has a new signature
  - Operation ProtectionIntentOperations.delete has a new signature
  - Operation ProtectionIntentOperations.get has a new signature
  - Operation ProtectionIntentOperations.validate has a new signature
  - Operation ProtectionPolicyOperationResultsOperations.get has a new signature
  - Operation ProtectionPolicyOperationStatusesOperations.get has a new signature
  - Operation RecoveryPointsCrrOperations.list has a new signature
  - Operation RecoveryPointsOperations.get has a new signature
  - Operation RecoveryPointsOperations.get_access_token has a new signature
  - Operation RecoveryPointsOperations.list has a new signature
  - Operation SecurityPINsOperations.get has a new signature
  - Model Day no longer has parameter date_property
  - Model AzureFileshareProtectedItem no longer has parameter health_status
  - Operation BackupCrrJobDetailsOperations.get has a new signature
  - Operation AadPropertiesOperations.get has a new signature
  - Operation BackupCrrJobsOperations.list has a new signature
  - Operation Operations.list has a new signature
  - Model RecoveryPointTierInformation has a new signature
  - Removed operation PrivateEndpointConnectionOperations.delete
  - Removed operation PrivateEndpointConnectionOperations.put
  - Removed operation RecoveryServicesBackupClientOperationsMixin.bms_prepare_data_move
  - Removed operation RecoveryServicesBackupClientOperationsMixin.bms_trigger_data_move
  - Removed operation CrossRegionRestoreOperations.trigger
  - Removed operation ProtectionPoliciesOperations.delete
  - Removed operation RestoresOperations.trigger

## 0.1.0 (1970-01-01)

* Initial Release
