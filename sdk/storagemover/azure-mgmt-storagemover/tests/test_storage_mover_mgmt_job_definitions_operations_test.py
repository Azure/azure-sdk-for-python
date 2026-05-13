# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Sync scenario tests for job_definitions.

Mirrors .NET JobDefinitionJobRunTests + JobDefinitionScheduleTests at:
  Q:\\source\\azure-sdk-for-net\\sdk\\storagemover\\Azure.ResourceManager.StorageMover\\tests\\Scenario
"""
from datetime import datetime, timedelta, timezone

import pytest
from azure.core.exceptions import HttpResponseError
from azure.mgmt.storagemover import StorageMoverMgmtClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = "eastus"

FAKE_STORAGE_ACCOUNT_ID = (
    "/subscriptions/00000000-0000-0000-0000-000000000000"
    "/resourceGroups/fakeRg/providers/Microsoft.Storage/storageAccounts/fakeAccount"
)


class TestStorageMoverMgmtJobDefinitionsOperations(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(StorageMoverMgmtClient)

    def _provision_parents(self, rg, sm_name, project_name, source_endpoint, target_endpoint):
        self.client.storage_movers.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name,
            storage_mover={"location": AZURE_LOCATION},
        )
        self.client.projects.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
            project={},
        )
        self.client.endpoints.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=source_endpoint,
            endpoint={"properties": {
                "endpointType": "NfsMount",
                "host": "10.0.0.1",
                "export": "/",
                "nfsVersion": "NFSv3",
            }},
        )
        self.client.endpoints.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=target_endpoint,
            endpoint={"properties": {
                "endpointType": "AzureStorageBlobContainer",
                "storageAccountResourceId": FAKE_STORAGE_ACCOUNT_ID,
                "blobContainerName": "testcontainer",
            }},
        )

    # ----- JobDefinitionJobRunTests.JobDefinitionJobRunTest -----
    # .NET version creates a job def, gets/lists/exists, then StartJob/StopJob.
    # In Python we cover the create/get/list/exists path. Start/Stop require a
    # registered agent on the storage mover, so they will fail with 4xx; we
    # assert that the request is rejected as expected.

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_job_definition_job_run(self, resource_group):
        rg = resource_group.name
        sm_name = "testsm-jdjr"
        project_name = "testproj-jdjr"
        source_endpoint = "testnfsendpoint"
        target_endpoint = "testblobendpoint"
        self._provision_parents(rg, sm_name, project_name, source_endpoint, target_endpoint)

        jd_name = "jobdef-jdjr1"
        jd = self.client.job_definitions.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
            job_definition_name=jd_name,
            job_definition={"properties": {
                "copyMode": "Additive",
                "sourceName": source_endpoint,
                "targetName": target_endpoint,
            }},
        )
        assert jd.name == jd_name
        assert jd.properties.target_name == target_endpoint
        assert jd.properties.source_name == source_endpoint
        assert jd.properties.copy_mode == "Additive"

        jd = self.client.job_definitions.get(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
            job_definition_name=jd_name,
        )

        items = list(self.client.job_definitions.list(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
        ))
        assert len(items) >= 1

        # Equivalence between two get() invocations.
        jd2 = self.client.job_definitions.get(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
            job_definition_name=jd_name,
        )
        assert jd2.name == jd.name
        assert jd2.properties.target_name == jd.properties.target_name
        assert jd2.properties.source_name == jd.properties.source_name
        assert jd2.id == jd.id

        # StartJob / StopJob require a registered agent — the RP will reject
        # the call. Assert the failure is signalled.
        with pytest.raises(HttpResponseError):
            self.client.job_definitions.start_job(
                resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
                job_definition_name=jd_name,
            )
        with pytest.raises(HttpResponseError):
            self.client.job_definitions.stop_job(
                resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
                job_definition_name=jd_name,
            )

    # ----- JobDefinitionScheduleTests.CreateJobDefinitionWithWeeklyScheduleTest -----

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_create_with_weekly_schedule(self, resource_group, **kwargs):
        rg = resource_group.name
        sm_name = "testsm-jdwk"
        project_name = "testproj-jdwk"
        source_endpoint = "testnfsendpoint"
        target_endpoint = "testblobendpoint"
        self._provision_parents(rg, sm_name, project_name, source_endpoint, target_endpoint)

        jd_name = "jobdef-sched-wk"
        variables = kwargs.pop("variables", {})
        now = datetime.now(timezone.utc)
        start_date = variables.setdefault(
            "schedule_start", (now + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        end_date = variables.setdefault(
            "schedule_end", (now + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        body = {"properties": {
            "copyMode": "Additive",
            "sourceName": source_endpoint,
            "targetName": target_endpoint,
            "description": "Job definition with weekly schedule",
            "dataIntegrityValidation": "SaveVerifyFileMD5",
            "schedule": {
                "frequency": "Weekly",
                "isActive": True,
                "executionTime": {"hour": 2},
                "startDate": start_date,
                "endDate": end_date,
                "daysOfWeek": ["Monday", "Wednesday", "Friday"],
            },
        }}

        jd = self.client.job_definitions.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
            job_definition_name=jd_name, job_definition=body,
        )
        assert jd.name == jd_name
        assert jd.properties.source_name == source_endpoint
        assert jd.properties.target_name == target_endpoint
        assert jd.properties.copy_mode == "Additive"
        assert jd.properties.description == "Job definition with weekly schedule"

        assert jd.properties.schedule is not None
        assert jd.properties.schedule.frequency == "Weekly"
        assert jd.properties.schedule.is_active is True
        assert jd.properties.schedule.execution_time.hour == 2
        assert len(jd.properties.schedule.days_of_week) == 3

        jd = self.client.job_definitions.get(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
            job_definition_name=jd_name,
        )
        assert jd.properties.schedule.frequency == "Weekly"

        self.client.job_definitions.begin_delete(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
            job_definition_name=jd_name,
        ).result()

        return variables

    # ----- JobDefinitionScheduleTests.CreateJobDefinitionWithDailyScheduleAndPreservePermissionsTest -----

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_create_with_daily_schedule_and_preserve_permissions(self, resource_group, **kwargs):
        rg = resource_group.name
        sm_name = "testsm-jddl"
        project_name = "testproj-jddl"
        source_endpoint = "testnfsendpoint"
        target_endpoint = "testblobendpoint"
        self._provision_parents(rg, sm_name, project_name, source_endpoint, target_endpoint)

        jd_name = "jobdef-sched-daily"
        variables = kwargs.pop("variables", {})
        now = datetime.now(timezone.utc)
        start_date = variables.setdefault(
            "schedule_start", (now + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        end_date = variables.setdefault(
            "schedule_end", (now + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        body = {"properties": {
            "copyMode": "Mirror",
            "sourceName": source_endpoint,
            "targetName": target_endpoint,
            "description": "Job definition with daily schedule",
            "dataIntegrityValidation": "None",
            "preservePermissions": True,
            "schedule": {
                "frequency": "Daily",
                "isActive": True,
                "executionTime": {"hour": 0},
                "startDate": start_date,
                "endDate": end_date,
            },
        }}

        jd = self.client.job_definitions.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
            job_definition_name=jd_name, job_definition=body,
        )
        assert jd.name == jd_name
        assert jd.properties.copy_mode == "Mirror"
        assert jd.properties.schedule is not None
        assert jd.properties.schedule.frequency == "Daily"
        assert jd.properties.schedule.is_active is True

        self.client.job_definitions.begin_delete(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
            job_definition_name=jd_name,
        ).result()

        return variables

    # ----- JobDefinitionScheduleTests.CreateJobDefinitionWithOnetimeScheduleTest -----

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_create_with_onetime_schedule(self, resource_group, **kwargs):
        rg = resource_group.name
        sm_name = "testsm-jdot"
        project_name = "testproj-jdot"
        source_endpoint = "testnfsendpoint"
        target_endpoint = "testblobendpoint"
        self._provision_parents(rg, sm_name, project_name, source_endpoint, target_endpoint)

        jd_name = "jobdef-sched-once"
        variables = kwargs.pop("variables", {})
        now = datetime.now(timezone.utc)
        start_date = variables.setdefault(
            "schedule_start", (now + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        body = {"properties": {
            "copyMode": "Additive",
            "sourceName": source_endpoint,
            "targetName": target_endpoint,
            "description": "Job definition with one-time schedule",
            "schedule": {
                "frequency": "Onetime",
                "isActive": True,
                "executionTime": {"hour": 10},
                "startDate": start_date,
            },
        }}

        jd = self.client.job_definitions.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
            job_definition_name=jd_name, job_definition=body,
        )
        assert jd.name == jd_name
        assert jd.properties.schedule is not None
        assert jd.properties.schedule.frequency == "Onetime"
        assert jd.properties.schedule.is_active is True

        self.client.job_definitions.begin_delete(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
            job_definition_name=jd_name,
        ).result()

        return variables
