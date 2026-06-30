# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import pytest
from azure.core.exceptions import ResourceNotFoundError
from azure.mgmt.storagemover.aio import StorageMoverMgmtClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer
from devtools_testutils.aio import recorded_by_proxy_async

AZURE_LOCATION = "eastus"
STORAGE_MOVER_NAME = "testmoverjobrun"
PROJECT_NAME = "testprojectjobrun"
SOURCE_ENDPOINT_NAME = "testnfssrc"
TARGET_ENDPOINT_NAME = "testblobtarget"
JOB_DEFINITION_NAME = "testjobdef1"

FAKE_STORAGE_ACCOUNT_ID = (
    "/subscriptions/00000000-0000-0000-0000-000000000000"
    "/resourceGroups/fakeRg/providers/Microsoft.Storage/storageAccounts/fakeAccount"
)


class TestStorageMoverMgmtJobRunsOperationsAsync(AzureMgmtRecordedTestCase):
    """Read-only coverage for job_runs (list + get).

    Job runs are created by the agent when StartJob is invoked on a job
    definition. Without a registered agent we can't trigger a real run, so
    these tests verify the read paths return sensible defaults: list yields
    an empty page, and get on a non-existent run raises ResourceNotFoundError.
    """

    def setup_method(self, method):
        self.client = self.create_mgmt_client(StorageMoverMgmtClient, is_async=True)

    async def _provision_parents(self, resource_group_name):
        await self.client.storage_movers.create_or_update(
            resource_group_name=resource_group_name,
            storage_mover_name=STORAGE_MOVER_NAME,
            storage_mover={
                "location": AZURE_LOCATION,
                "properties": {"description": "Storage mover for job run tests"},
            },
        )
        await self.client.projects.create_or_update(
            resource_group_name=resource_group_name,
            storage_mover_name=STORAGE_MOVER_NAME,
            project_name=PROJECT_NAME,
            project={"properties": {"description": "Project for job run tests"}},
        )
        await self.client.endpoints.create_or_update(
            resource_group_name=resource_group_name,
            storage_mover_name=STORAGE_MOVER_NAME,
            endpoint_name=SOURCE_ENDPOINT_NAME,
            endpoint={
                "properties": {
                    "endpointType": "NfsMount",
                    "host": "10.0.0.1",
                    "export": "/nfsshare",
                    "nfsVersion": "NFSv3",
                    "description": "Source NFS endpoint",
                }
            },
        )
        await self.client.endpoints.create_or_update(
            resource_group_name=resource_group_name,
            storage_mover_name=STORAGE_MOVER_NAME,
            endpoint_name=TARGET_ENDPOINT_NAME,
            endpoint={
                "properties": {
                    "endpointType": "AzureStorageBlobContainer",
                    "storageAccountResourceId": FAKE_STORAGE_ACCOUNT_ID,
                    "blobContainerName": "testcontainer",
                    "description": "Target blob container endpoint",
                }
            },
        )
        await self.client.job_definitions.create_or_update(
            resource_group_name=resource_group_name,
            storage_mover_name=STORAGE_MOVER_NAME,
            project_name=PROJECT_NAME,
            job_definition_name=JOB_DEFINITION_NAME,
            job_definition={
                "properties": {
                    "copyMode": "Additive",
                    "sourceName": SOURCE_ENDPOINT_NAME,
                    "targetName": TARGET_ENDPOINT_NAME,
                    "description": "Job definition for job run tests",
                }
            },
        )

    # ----- JobRunTests.GetExistTest -----
    # .NET version does: get(known JobName) + foreach list + Exists(JobName) + second get.
    # JobRuns are produced by an agent's StartJob run; without a registered agent we
    # cannot create one, so we cover the equivalent read paths: list returns an empty
    # page, and get on an unknown name raises ResourceNotFoundError.

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_get_exist(self, resource_group):
        await self._provision_parents(resource_group.name)

        response = self.client.job_runs.list(
            resource_group_name=resource_group.name,
            storage_mover_name=STORAGE_MOVER_NAME,
            project_name=PROJECT_NAME,
            job_definition_name=JOB_DEFINITION_NAME,
        )
        result = [r async for r in response]
        assert result == []

        with pytest.raises(ResourceNotFoundError):
            await self.client.job_runs.get(
                resource_group_name=resource_group.name,
                storage_mover_name=STORAGE_MOVER_NAME,
                project_name=PROJECT_NAME,
                job_definition_name=JOB_DEFINITION_NAME,
                job_run_name="nonexistentrun",
            )
