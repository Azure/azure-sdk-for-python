# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import time

from datetime import datetime, timedelta

from azure.mgmt.recoveryservices.models import Sku, SkuName, Vault, VaultProperties

try:
    from urllib.parse import urlparse
except ImportError:
    # Python 2 compatibility
    from urlparse import urlparse

from azure.mgmt.recoveryservicesbackup.models import (AzureIaaSComputeVMProtectedItem, BackupRequestResource,
                                                      IaasVMBackupRequest,
                                                      IaasVMILRRegistrationRequest, IaasVMRestoreRequest,
                                                      ILRRequestResource, JobStatus,
                                                      OperationStatusValues, ProtectedItemResource, ProtectionState,
                                                      RecoveryType,
                                                      RestoreRequestResource,
                                                      BackupManagementType)
from msrestazure.azure_exceptions import CloudError


class MgmtRecoveryServicesBackupTestDefinition(object):

    vm_friendly_name = "swaggersdktest"
    vm_rg_name = "swaggersdktestrg"
    vm_type = "Compute"
    restore_storage_acc_name = "swaggersdktest"
    restore_storage_acc_rg_name = "swaggersdktestrg"
    fabric_name = "Azure"
    location = "southeastasia"
    
    def __init__(self, subscription_id, vault_name, vault_rg_name):
        self.subscription_id = subscription_id
        self.vault_name = vault_name
        self.vault_rg_name = vault_rg_name

    @property
    def container_type(self):
        return "iaasvmcontainerv2" if self.vm_type.lower() == "compute" else "iaasvmcontainer"

    @property
    def container_unique_name(self):
        return ";".join([self.container_type, self.vm_rg_name, self.vm_friendly_name])

    @property
    def container_name(self):
        return ";".join(["iaasvmcontainer", self.container_unique_name])

    @property
    def vm_name(self):
        return ";".join(["vm", self.container_unique_name])

    @property
    def storage_account_id(self):
        return "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Storage/storageAccounts/{}".format(
            self.subscription_id,
            self.restore_storage_acc_rg_name,
            self.restore_storage_acc_name,
            )


class MgmtRecoveryServicesBackupTestHelper(object):

    def __init__(self, test_context):
        self.context = test_context
        self.vault_client = self.context.vault_client  # type: azure.mgmt.recoveryservices.RecoveryServicesClient
        self.backup_client = self.context.backup_client  # type: azure.mgmt.recoveryservicesbackup.RecoveryServicesBackupClient
        self.test_definition = self.context.test_definition
        self.vault_name = self.test_definition.vault_name
        self.resource_group = self.test_definition.vault_rg_name
        self.fabric_name = self.test_definition.fabric_name

    def create_vault(self):
        vault = Vault(
            location='southeastasia',
            sku=Sku(
                name=SkuName.standard,
            ),
            properties=VaultProperties()
        )
        self.vault_client.vaults.create_or_update(self.resource_group, self.vault_name, vault)

    def delete_vault(self):
        return self.vault_client.vaults.delete(self.resource_group, self.vault_name)

    def enable_protection(self, container_name, protected_item_name, policy_name):
        policy = self.get_policy_with_retries(policy_name)
        self.context.assertIsNotNone(policy)

        response = self.backup_client.protection_containers.refresh(self.vault_name, self.resource_group, self.test_definition.fabric_name, raw=True)
        self._validate_operation_response(response)

        self._get_operation_response(
            response,
            lambda operation_id: self.backup_client.protection_container_refresh_operation_results.get(
                self.vault_name, self.resource_group, self.fabric_name, operation_id, raw=True,
            ),
            None,
        )

        iaasvm_odata_filter = "backupManagementType eq '{}'".format(BackupManagementType.azure_iaas_vm.value)
        protectable_items = self.backup_client.backup_protectable_items.list(self.vault_name, self.resource_group, filter=iaasvm_odata_filter)
        
        desired_protectable_item = next(protectable_item for protectable_item in protectable_items if protectable_item.name.lower() in container_name.lower()).properties
        self.context.assertIsNotNone(desired_protectable_item)

        protected_item_resource = ProtectedItemResource(
            properties=AzureIaaSComputeVMProtectedItem(policy_id=policy.id, source_resource_id=desired_protectable_item.virtual_machine_id)
            )

        response = self.backup_client.protected_items.create_or_update(self.vault_name, self.resource_group, self.fabric_name, container_name,
                                                                       protected_item_name, protected_item_resource, raw=True)
        self._validate_operation_response(response)

        job_response = self._get_operation_response(
            response,
            lambda operation_id: self.backup_client.protected_item_operation_results.get(
                self.vault_name, self.resource_group, self.fabric_name, container_name, protected_item_name, operation_id, raw=True,
                ),
            lambda operation_id: self.backup_client.protected_item_operation_statuses.get(
                self.vault_name, self.resource_group, self.fabric_name, container_name, protected_item_name, operation_id,
                ),
            )

        self.context.assertIsNotNone(job_response.job_id)
        return job_response.job_id

    def list_protected_items(self):
        return self.backup_client.backup_protected_items.list(self.vault_name, self.resource_group)

    def trigger_backup(self, container_name, protected_item_name):
        expiry_time = datetime.utcnow() + timedelta(days=2)

        backup_request = BackupRequestResource(
            properties=IaasVMBackupRequest(recovery_point_expiry_time_in_utc=expiry_time),
            )

        response = self.backup_client.backups.trigger(self.vault_name, self.resource_group, self.fabric_name, container_name, protected_item_name,
                                                      backup_request, raw=True)
        self._validate_operation_response(response)

        job_response = self._get_operation_response(
            response,
            lambda operation_id: self.backup_client.protected_item_operation_results.get(
                self.vault_name, self.resource_group, self.fabric_name, container_name, protected_item_name, operation_id, raw=True,
                ),
            lambda operation_id: self.backup_client.protected_item_operation_statuses.get(
                self.vault_name, self.resource_group, self.fabric_name, container_name, protected_item_name, operation_id,
                ),
            )

        self.context.assertIsNotNone(job_response.job_id)
        return job_response.job_id

    def list_backup_jobs(self):
        return self.backup_client.backup_jobs.list(self.vault_name, self.resource_group)

    def list_recovery_points(self, container_name, protected_item_name):
        return self.backup_client.recovery_points.list(self.vault_name, self.resource_group, self.fabric_name, container_name, protected_item_name)

    def trigger_restore(self, container_name, protected_item_name, recovery_point_name, source_resource_id, storage_account_id):
        restore_request = RestoreRequestResource(
            properties=IaasVMRestoreRequest(
                recovery_point_id=recovery_point_name,
                recovery_type=RecoveryType.restore_disks,
                source_resource_id=source_resource_id,
                storage_account_id=storage_account_id,
                region=self.test_definition.location,
                create_new_cloud_service=False,
                )
            )

        response = self.backup_client.restores.trigger(self.vault_name, self.resource_group, self.fabric_name, container_name, protected_item_name,
                                                       recovery_point_name, restore_request, raw=True)
        self._validate_operation_response(response)

        job_response = self._get_operation_response(
            response,
            lambda operation_id: self.backup_client.protected_item_operation_results.get(
                self.vault_name, self.resource_group, self.test_definition.fabric_name, container_name, protected_item_name, operation_id, raw=True,
                ),
            lambda operation_id: self.backup_client.protected_item_operation_statuses.get(
                self.vault_name, self.resource_group, self.test_definition.fabric_name, container_name, protected_item_name, operation_id,
                ),
            )

        self.context.assertIsNotNone(job_response.job_id)
        return job_response.job_id

    def disable_protection_with_retain_data(self, container_name, protected_item_name, protected_item):

        protected_item_resource = ProtectedItemResource(
            properties=AzureIaaSComputeVMProtectedItem(source_resource_id=protected_item.virtual_machine_id,
                                                       protection_state=ProtectionState.protection_stopped,
                                                       )
        )

        response = self.backup_client.protected_items.create_or_update(
            self.vault_name, self.resource_group, self.fabric_name, container_name, protected_item_name,
            protected_item_resource, raw=True
        )

        self._validate_operation_response(response)

        job_response = self._get_operation_response(
            response,
            lambda operation_id: self.backup_client.protected_item_operation_results.get(
                self.vault_name, self.resource_group, self.fabric_name, container_name, protected_item_name, operation_id, raw=True,
            ),
            lambda operation_id: self.backup_client.protected_item_operation_statuses.get(
                self.vault_name, self.resource_group, self.fabric_name, container_name, protected_item_name, operation_id,
            ),
        )

        self.context.assertIsNotNone(job_response.job_id)
        return job_response.job_id

    def delete_protection(self, container_name, protected_item_name):
        response = self.backup_client.protected_items.delete(
            self.vault_name, self.resource_group, self.fabric_name, container_name, protected_item_name, raw=True)
        self._validate_operation_response(response)

        job_response = self._get_operation_status(
            response,
            lambda operation_id: self.backup_client.backup_operation_statuses.get(self.vault_name, self.resource_group, operation_id),
        )

        self.context.assertIsNotNone(job_response.job_id)
        return job_response.job_id

    def provision_item_level_recovery(self, container_name, protected_item_name, recovery_point_name, source_resource_id):
        ilr_request = ILRRequestResource(
            properties=IaasVMILRRegistrationRequest(
                recovery_point_id=recovery_point_name,
                virtual_machine_id=source_resource_id,
                initiator_name="Hello World",
                renew_existing_registration=True,
                )
            )

        response = self.backup_client.item_level_recovery_connections.provision(
            self.vault_name, self.resource_group, self.fabric_name, container_name, protected_item_name, recovery_point_name, ilr_request, raw=True,
            )
        self._validate_operation_response(response)

        ilr_response_extended_info = self._get_operation_response(
            response,
            lambda operation_id: self.backup_client.protected_item_operation_results.get(
                self.vault_name, self.resource_group, self.test_definition.fabric_name, container_name, protected_item_name, operation_id, raw=True,
                ),
            lambda operation_id: self.backup_client.protected_item_operation_statuses.get(
                self.vault_name, self.resource_group, self.test_definition.fabric_name, container_name, protected_item_name, operation_id,
                ),
            )

        self.context.assertIsNotNone(ilr_response_extended_info)
        self.context.assertIsNotNone(ilr_response_extended_info.recovery_target)
        self.context.assertIsNotNone(ilr_response_extended_info.recovery_target.client_scripts)
        self.context.assertTrue(len(ilr_response_extended_info.recovery_target.client_scripts) > 0)
        return ilr_response_extended_info

    def revoke_item_level_recovery(self, container_name, protected_item_name, recovery_point_name):

        response = self.backup_client.item_level_recovery_connections.revoke(
            self.vault_name, self.resource_group, self.fabric_name, container_name, protected_item_name, recovery_point_name, raw=True,
            )
        self._validate_operation_response(response)

        job_response = self._get_operation_response(
            response,
            lambda operation_id: self.backup_client.protected_item_operation_results.get(
                self.vault_name, self.resource_group, self.test_definition.fabric_name, container_name, protected_item_name, operation_id, raw=True,
                ),
            lambda operation_id: self.backup_client.protected_item_operation_statuses.get(
                self.vault_name, self.resource_group, self.test_definition.fabric_name, container_name, protected_item_name, operation_id,
                ),
            )

    def wait_for_job_completion(self, job_id):
        self.retry_action_with_timeout(
            lambda: self.get_job_status(job_id),
            lambda job_status: not self.is_job_in_progress(job_status),
            3 * 60 * 60,  # 3 Hours
            lambda status_code: self._dummy_wait_and_return_true,
            )

    def get_job_status(self, job_id):
        response = self.backup_client.job_details.get(self.vault_name, self.resource_group, job_id)
        self.context.assertIsNotNone(response)
        return response.properties.status

    def is_job_in_progress(self, job_status):
        in_progress = job_status in [JobStatus.in_progress.value, JobStatus.cancelling.value]
        if in_progress:
            self.context.sleep(60)
        return in_progress

    def get_policy_with_retries(self, policy_name):
        
        return self.retry_action_with_timeout(
            lambda: self.backup_client.protection_policies.get(self.vault_name, self.resource_group, policy_name),
            lambda result: result is not None,
            5 * 60,
            self._resource_not_synced_retry_logic
            )

    @staticmethod
    def retry_action_with_timeout(action, validator, timeout, should_retry):
        
        end_time = time.time() + timeout
        result = None
        validator_result = False if result is None else validator(result)

        while time.time() < end_time and not validator_result:
            try:
                result = action()
                validator_result = validator(result)
            except CloudError as ex:
                if not should_retry(ex.response.status_code):
                    raise

        return result

    def list_operations(self):
        operations = self.backup_client.operations.list()
        return operations

    def _resource_not_synced_retry_logic(self, status_code):
        should_retry = status_code == 200 or status_code == 404
        if should_retry:
            self.context.sleep(30)
        return should_retry

    def _dummy_wait_and_return_true(self, timeout_in_sec):
        self.context.sleep(timeout_in_sec)
        return True

    def _validate_operation_response(self, raw_response):
        self.context.assertIsNotNone(raw_response)
        self.context.assertEqual(raw_response.response.status_code, 202)
        self.context.assertTrue("Location" in raw_response.response.headers or "Azure-AsyncOperation" in raw_response.response.headers)
        self.context.assertTrue("Retry-After" in raw_response.response.headers)

    def _get_operation_status(self, raw_response, get_operation_status_func):
        operation_id_path = urlparse(raw_response.response.headers["Azure-AsyncOperation"]).path
        operation_id = operation_id_path.rsplit("/")[-1]
        operation_response = get_operation_status_func(operation_id)

        while operation_response.status == OperationStatusValues.in_progress.value:
            self.context.sleep(5)
            operation_response = get_operation_status_func(operation_id)

        operation_response = get_operation_status_func(operation_id)
        self.context.assertEqual(OperationStatusValues.succeeded.value, operation_response.status)
        return operation_response.properties

    def _get_operation_response(self, raw_response, get_operation_result_func, get_operation_status_func):
        operation_id_path = urlparse(raw_response.response.headers["Location"]).path
        operation_id = operation_id_path.rsplit("/")[-1]
        operation_response = get_operation_result_func(operation_id)

        while operation_response.response.status_code == 202:
            self.context.sleep(5)
            operation_response = get_operation_result_func(operation_id)

        if get_operation_status_func:
            operation_status_response = get_operation_status_func(operation_id)
            return operation_status_response.properties

        return operation_response
