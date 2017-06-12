# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import unittest

import azure.mgmt.recoveryservicesbackup
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import AzureMgmtTestCase
from tests.recoveryservicesbackup_testcase import MgmtRecoveryServicesBackupTestDefinition, MgmtRecoveryServicesBackupTestHelper


class MgmtRecoveryServicesBackupTests(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtRecoveryServicesBackupTests, self).setUp()
        self.client = self.create_mgmt_client(
            azure.mgmt.recoveryservicesbackup.RecoveryServicesBackupClient
        )

        # Using pre-existing vault until vault client is available
        self.resource_group = "PythonSDKBackupTestRg"
        self.vault_name = "PySDKBackupTestRsVault"
        self.test_definition = MgmtRecoveryServicesBackupTestDefinition(self.settings.SUBSCRIPTION_ID, self.vault_name, self.resource_group)
        self.test_helper = MgmtRecoveryServicesBackupTestHelper(self)

    @record
    def test_iaasvm_e2e(self):
        self.test_helper.enable_protection(self.test_definition.container_name, self.test_definition.vm_name, "DefaultPolicy")

        protected_items = self.test_helper.list_protected_items()
        self.assertIsNotNone(protected_items)
        protected_items = list(protected_items)
        protected_item = next(protected_item for protected_item in protected_items if protected_item.name.lower() == self.test_definition.container_name.lower()).properties

        # Trigger Backup
        backup_job_id = self.test_helper.trigger_backup(self.test_definition.container_name, self.test_definition.vm_name)
        # self.test_helper.wait_for_job_completion(backup_job_id)
        self.sleep(45 * 60)  # Sleep for 45 minutes to let backup complete
        # TODO: Once backup jobs API is fixed. Remove this hack

        recovery_points = self.test_helper.list_recovery_points(self.test_definition.container_name, self.test_definition.vm_name)
        self.assertIsNotNone(recovery_points)
        recovery_points = list(recovery_points)
        self.assertTrue(any(recovery_points))

        recovery_point = recovery_points[0]
        self.assertIsNotNone(recovery_point)

        # Trigger Restore
        restore_job_id = self.test_helper.trigger_restore(self.test_definition.container_name, self.test_definition.vm_name, recovery_point.name, protected_item.virtual_machine_id, self.test_definition.storage_account_id)
        # self.test_helper.wait_for_job_completion(restore_job_id)
        self.sleep(45 * 60)  # Sleep for 45 minutes to let restore complete
        # TODO: Once backup jobs API is fixed. Remove this hack

        # Provision ILR
        ilr_extended_info = self.test_helper.provision_item_level_recovery(self.test_definition.container_name, self.test_definition.vm_name, recovery_point.name, protected_item.virtual_machine_id)

        # Revoke ILR
        self.test_helper.revoke_item_level_recovery(self.test_definition.container_name, self.test_definition.vm_name, recovery_point.name)

        # Disable Protection
        self.test_helper.disable_protection(self.test_definition.container_name, self.test_definition.vm_name)

    @record
    def test_operations_api(self):
        operations = self.test_helper.list_operations()
        self.assertIsNotNone(operations)
        self.assertTrue(any(operations))
