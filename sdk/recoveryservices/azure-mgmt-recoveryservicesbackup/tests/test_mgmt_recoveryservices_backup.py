# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import time
import unittest
from contextlib import contextmanager

import azure.mgmt.recoveryservicesbackup
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer
from recoveryservicesbackup_testcase import MgmtRecoveryServicesBackupTestDefinition, MgmtRecoveryServicesBackupTestHelper


class MgmtRecoveryServicesBackupTests(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtRecoveryServicesBackupTests, self).setUp()

        self.vault_client = self.create_mgmt_client(
            azure.mgmt.recoveryservices.RecoveryServicesClient
        )
        self.backup_client = self.create_mgmt_client(
            azure.mgmt.recoveryservicesbackup.RecoveryServicesBackupClient
        )

        # Using pre-existing vault until vault client is available
        self.resource_group_name = "PythonSDKBackupTestRg"
        self.group_name = self.resource_group_name
        self.vault_name = "PySDKBackupTestRsVault"
        self.test_definition = MgmtRecoveryServicesBackupTestDefinition(self.settings.SUBSCRIPTION_ID, self.vault_name, self.resource_group_name)
        self.test_helper = MgmtRecoveryServicesBackupTestHelper(self)
        self.region = "southeastasia"

    def sleep(self, duration):
        if self.is_live:
            time.sleep(duration)

    @contextmanager
    def vault(self):
        self.test_helper.create_vault()
        yield
        self.test_helper.delete_vault()

    @ResourceGroupPreparer()
    def test_iaasvm_e2e(self, resource_group, location):
        raise unittest.SkipTest("Skipping IAA VM test")
        with self.vault():
            self.test_helper.enable_protection(self.test_definition.container_name, self.test_definition.vm_name, "DefaultPolicy")

            protected_items = self.test_helper.list_protected_items()
            self.assertIsNotNone(protected_items)
            protected_items = list(protected_items)
            protected_item = next(protected_item for protected_item in protected_items
                                  if protected_item.name.lower() == self.test_definition.vm_name.lower()).properties

            # Trigger Backup
            backup_job_id = self.test_helper.trigger_backup(self.test_definition.container_name, self.test_definition.vm_name)

            backup_jobs = self.test_helper.list_backup_jobs()
            self.assertIsNotNone(backup_jobs)
            backup_jobs = list(backup_jobs)
            self.assertTrue(any(backup_job_id == backup_job.name for backup_job in backup_jobs))

            self.test_helper.wait_for_job_completion(backup_job_id)

            recovery_points = self.test_helper.list_recovery_points(self.test_definition.container_name, self.test_definition.vm_name)
            self.assertIsNotNone(recovery_points)
            recovery_points = list(recovery_points)
            self.assertTrue(any(recovery_points))

            recovery_point = recovery_points[0]
            self.assertIsNotNone(recovery_point)

            # Trigger Restore
            restore_job_id = self.test_helper.trigger_restore(self.test_definition.container_name, self.test_definition.vm_name, recovery_point.name,
                                                              protected_item.virtual_machine_id, self.test_definition.storage_account_id)
            backup_jobs = self.test_helper.list_backup_jobs()
            self.assertIsNotNone(backup_jobs)
            backup_jobs = list(backup_jobs)
            self.assertTrue(any(restore_job_id == backup_job.name for backup_job in backup_jobs))

            self.test_helper.wait_for_job_completion(restore_job_id)

            # Provision ILR
            self.test_helper.provision_item_level_recovery(self.test_definition.container_name, self.test_definition.vm_name,
                                                                               recovery_point.name, protected_item.virtual_machine_id)

            # Revoke ILR
            self.test_helper.revoke_item_level_recovery(self.test_definition.container_name, self.test_definition.vm_name, recovery_point.name)

            self.test_helper.disable_protection_with_retain_data(self.test_definition.container_name, self.test_definition.vm_name, protected_item)

            # Disable Protection
            self.test_helper.delete_protection(self.test_definition.container_name, self.test_definition.vm_name)

    def test_operations_api(self):
        operations = self.test_helper.list_operations()
        self.assertIsNotNone(operations)
        self.assertTrue(any(operations))
