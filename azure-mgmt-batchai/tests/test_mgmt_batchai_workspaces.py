# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long
import pytest
from azure.mgmt.batchai import BatchAIManagementClient, models
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer
from msrestazure.azure_exceptions import CloudError

from helpers import Helpers


class WorkspaceTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(WorkspaceTestCase, self).setUp()
        self.client = Helpers.create_batchai_client(self)  # type: BatchAIManagementClient

    @ResourceGroupPreparer(location=Helpers.LOCATION)
    def test_creation_and_deletion(self, resource_group, location):
        name = 'testee'
        workspace = self.client.workspaces.create(resource_group.name, name, location).result()
        self.assertEqual(workspace.name, name)
        workspace_id = workspace.id
        # Check can get workspace info
        workspace = self.client.workspaces.get(resource_group.name, name)
        self.assertEqual(workspace.id, workspace_id)
        # Check workspace found when list under current subscription
        workspaces = self.client.workspaces.list()
        self.assertTrue(workspace_id in [w.id for w in workspaces])
        # Check workspace found when list under the resource group
        workspaces = self.client.workspaces.list_by_resource_group(resource_group.name)
        self.assertTrue(workspace_id in [w.id for w in workspaces])
        # Delete
        self.client.workspaces.delete(resource_group.name, name).result()
        # Check the workspace is actually deleted
        workspaces = self.client.workspaces.list_by_resource_group(resource_group.name)
        self.assertFalse(list(workspaces))

    @ResourceGroupPreparer(location=Helpers.LOCATION)
    def test_workspaces_isolation(self, resource_group, location):
        self.client.workspaces.create(resource_group.name, 'first', location).result()
        self.client.workspaces.create(resource_group.name, 'second', location).result()
        # Create a cluster, an experiment and a job in each workspace
        for workspace in ['first', 'second']:
            cluster = self.client.clusters.create(
                resource_group.name,
                workspace,
                'cluster',
                parameters=models.ClusterCreateParameters(
                    vm_size='STANDARD_D1',
                    scale_settings=models.ScaleSettings(
                        manual=models.ManualScaleSettings(target_node_count=0)),
                    user_account_settings=models.UserAccountSettings(
                        admin_user_name=Helpers.ADMIN_USER_NAME,
                        admin_user_password=Helpers.ADMIN_USER_PASSWORD
                    ),
                    vm_priority='lowpriority'
                )).result()
            self.client.experiments.create(resource_group.name, workspace, 'experiment').result()
            self.client.jobs.create(
                resource_group.name,
                workspace,
                'experiment',
                'job',
                parameters=models.JobCreateParameters(
                    cluster=models.ResourceId(id=cluster.id),
                    node_count=1,
                    std_out_err_path_prefix='$AZ_BATCHAI_MOUNT_ROOT',
                    custom_toolkit_settings=models.CustomToolkitSettings(
                        command_line='true'
                    )
                )
            ).result()
        # Delete the first workspace
        self.client.workspaces.delete(resource_group.name, 'first').result()
        # Ensure the workspace was actually deleted
        self.assertRaises(CloudError, lambda: self.client.workspaces.get(resource_group.name, 'first'))
        # Ensure the second workspace is not affected
        self.client.workspaces.get(resource_group.name, 'second')
        self.client.clusters.get(resource_group.name, 'second', 'cluster')
        self.client.experiments.get(resource_group.name, 'second', 'experiment')
        job = self.client.jobs.get(resource_group.name, 'second', 'experiment', 'job')
        # And check the job is not terminated
        self.assertEqual(job.execution_state, models.ExecutionState.queued)

    @ResourceGroupPreparer(location=Helpers.LOCATION)
    def test_update(self, resource_group, location):
        self.skipTest('Waiting for the server side fix')
        self.client.workspaces.create(resource_group.name, 'workspace', location).result()
        self.client.workspaces.update(resource_group.name, 'workspace', {'values': {'atag'}})
        workspace = self.client.workspaces.get(resource_group.name, 'workspace')  # type: models.Workspace
        self.assertEqual(workspace.tags['values'], {'atag'})