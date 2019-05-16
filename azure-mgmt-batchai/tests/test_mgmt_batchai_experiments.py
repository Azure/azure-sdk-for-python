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


class ExperimentTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(ExperimentTestCase, self).setUp()
        self.client = Helpers.create_batchai_client(self)  # type: BatchAIManagementClient

    @ResourceGroupPreparer(location=Helpers.LOCATION)
    def test_creation_and_deletion(self, resource_group, location):
        name = 'testee'
        workspace_name = 'workspace'
        self.client.workspaces.create(resource_group.name, workspace_name, location).result()
        experiment = self.client.experiments.create(resource_group.name, workspace_name, name).result()
        self.assertEqual(experiment.name, name)
        experiment_id = experiment.id
        # Check can get experiment info
        experiment = self.client.experiments.get(resource_group.name, workspace_name, name)
        self.assertEqual(experiment.id, experiment_id)
        # Check experiment found in list results
        experiments = self.client.experiments.list_by_workspace(resource_group.name, workspace_name)
        self.assertTrue(experiment_id in [e.id for e in experiments])
        # Delete
        self.client.experiments.delete(resource_group.name, workspace_name, name).result()
        # Check the experiment is actually deleted
        self.assertRaises(CloudError, lambda: self.client.experiments.get(resource_group.name, workspace_name, name))

    @ResourceGroupPreparer(location=Helpers.LOCATION)
    def test_experiments_isolation(self, resource_group, location):
        self.client.workspaces.create(resource_group.name, 'first', location).result()
        self.client.workspaces.create(resource_group.name, 'second', location).result()
        # Create a cluster, two experiments and a job in each experiment
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
            for experiment in ['exp1', 'exp2']:
                self.client.experiments.create(resource_group.name, workspace, experiment).result()
                self.client.jobs.create(
                    resource_group.name,
                    workspace,
                    experiment,
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
        # Delete exp1 in the first workspace
        self.client.experiments.delete(resource_group.name, 'first', 'exp1').result()
        # Ensure the experiment was actually deleted
        self.assertRaises(CloudError, lambda: self.client.experiments.get(resource_group.name, 'first', 'exp1'))
        for workspace in ['first', 'second']:
            # Ensure the clusters are not affected
            self.client.clusters.get(resource_group.name, workspace, 'cluster')
            # Ensure the other experiments are not affected
            for experiment in ['exp1', 'exp2']:
                if workspace == 'first' and experiment == 'exp1':
                    continue
                self.client.experiments.get(resource_group.name, workspace, experiment)
                job = self.client.jobs.get(resource_group.name, workspace, experiment, 'job')
                # And check the job are not terminated
                self.assertEqual(job.execution_state, models.ExecutionState.queued)
