# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Async scenario tests for job_definitions.

Mirrors .NET JobDefinitionJobRunTests + JobDefinitionScheduleTests at:
  Q:\\source\\azure-sdk-for-net\\sdk\\storagemover\\Azure.ResourceManager.StorageMover\\tests\\Scenario

Also implements cross-language matrix row #31
(`JobDefinitionJobRunTests.StartC2CJobWithPrivateSourceTest`) — see the sync
sibling file for the full rationale.
"""
import asyncio
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from azure.core.exceptions import HttpResponseError
from azure.mgmt.authorization.v2022_04_01.aio import AuthorizationManagementClient
from azure.mgmt.network.aio import NetworkManagementClient
from azure.mgmt.storage.aio import StorageManagementClient
from azure.mgmt.storagemover.aio import StorageMoverMgmtClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer
from devtools_testutils.aio import recorded_by_proxy_async

AZURE_LOCATION = "eastus"
# Matrix row #31 runs in westcentralus (shared PLS + storage account live there).
WCUS_LOCATION = "westcentralus"

FAKE_STORAGE_ACCOUNT_ID = (
    "/subscriptions/00000000-0000-0000-0000-000000000000"
    "/resourceGroups/fakeRg/providers/Microsoft.Storage/storageAccounts/fakeAccount"
)

# Shared team infra in XDataMove-Synthetics — do not recreate.
# Full inventory in the cross-language playbook
# (storage-mover-scenario-tests-cross-language, "Porter's reference" callout).
SYNTHETICS_SUBSCRIPTION_ID = "b6b34ad8-ca89-4f85-beb7-c2ec13702dac"

PLS_RESOURCE_GROUP = "E2E-Management-RGsyn"
PLS_NAME = "test-pls-wcs"
REAL_PRIVATE_LINK_SERVICE_ID = (
    "/subscriptions/" + SYNTHETICS_SUBSCRIPTION_ID
    + "/resourceGroups/" + PLS_RESOURCE_GROUP
    + "/providers/Microsoft.Network/privateLinkServices/" + PLS_NAME
)

STORAGE_ACCOUNT_RG = "CP_Mover_IN_WCUS"
STORAGE_ACCOUNT_NAME = "cpmoveraccount"
STORAGE_ACCOUNT_ID = (
    "/subscriptions/" + SYNTHETICS_SUBSCRIPTION_ID
    + "/resourceGroups/" + STORAGE_ACCOUNT_RG
    + "/providers/Microsoft.Storage/storageAccounts/" + STORAGE_ACCOUNT_NAME
)

MULTI_CLOUD_CONNECTOR_ID = (
    "/subscriptions/" + SYNTHETICS_SUBSCRIPTION_ID
    + "/resourceGroups/E2E-Management-RGsyn"
    + "/providers/Microsoft.HybridConnectivity/publicCloudConnectors/e2e-sm-rp-connector"
)
PRIVATE_S3_BUCKET_ID = (
    "/subscriptions/" + SYNTHETICS_SUBSCRIPTION_ID
    + "/resourceGroups/aws_640698235822"
    + "/providers/Microsoft.AWSConnector/s3Buckets/e2e-sm-rp-private-bucket"
)
AWS_PUBLIC_S3_BUCKET_ID = (
    "/subscriptions/" + SYNTHETICS_SUBSCRIPTION_ID
    + "/resourceGroups/aws_640698235822"
    + "/providers/Microsoft.AWSConnector/s3Buckets/e2e-sm-rp-bucket"
)

STORAGE_BLOB_DATA_CONTRIBUTOR_ROLE_DEF_GUID = "ba92f5b4-2d11-453d-a403-e96b0029c9fe"


class TestStorageMoverMgmtJobDefinitionsOperationsAsync(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(StorageMoverMgmtClient, is_async=True)

    async def _provision_parents(self, rg, sm_name, project_name, source_endpoint, target_endpoint):
        await self.client.storage_movers.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name,
            storage_mover={"location": AZURE_LOCATION},
        )
        await self.client.projects.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
            project={},
        )
        await self.client.endpoints.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=source_endpoint,
            endpoint={"properties": {
                "endpointType": "NfsMount",
                "host": "10.0.0.1",
                "export": "/",
                "nfsVersion": "NFSv3",
            }},
        )
        await self.client.endpoints.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=target_endpoint,
            endpoint={"properties": {
                "endpointType": "AzureStorageBlobContainer",
                "storageAccountResourceId": FAKE_STORAGE_ACCOUNT_ID,
                "blobContainerName": "testcontainer",
            }},
        )

    # ----- JobDefinitionJobRunTests.JobDefinitionJobRunTest (matrix row #10) -----
    # See the sync sibling for full rationale + design notes.

    @RandomNameResourceGroupPreparer(location=WCUS_LOCATION)
    @recorded_by_proxy_async
    async def test_job_definition_job_run(self, resource_group, **kwargs):
        rg = resource_group.name
        sm_name = "testsm-jdjr"
        project_name = "testproj-jdjr"
        source_endpoint = "testsrcep-mcc-pub"
        target_endpoint = "testtgtep-blob-pub"
        jd_name = "jobdef-jdjr-pub"

        variables = kwargs.pop("variables", {})
        container_name = variables.setdefault("container_name", "tc" + uuid.uuid4().hex[:10].lower())
        role_assignment_name = variables.setdefault("role_assignment_id", str(uuid.uuid4()))

        storage_client = self.create_client_from_credential(
            StorageManagementClient,
            self.get_credential(StorageManagementClient, is_async=True),
            subscription_id=SYNTHETICS_SUBSCRIPTION_ID,
        )
        authorization_client = self.create_client_from_credential(
            AuthorizationManagementClient,
            self.get_credential(AuthorizationManagementClient, is_async=True),
            subscription_id=SYNTHETICS_SUBSCRIPTION_ID,
        )

        container_created = False
        rbac_created = False
        container_scope = (
            STORAGE_ACCOUNT_ID + "/blobServices/default/containers/" + container_name
        )

        try:
            await self.client.storage_movers.create_or_update(
                resource_group_name=rg, storage_mover_name=sm_name,
                storage_mover={"location": WCUS_LOCATION},
            )
            await self.client.projects.create_or_update(
                resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
                project={},
            )

            await self.client.endpoints.create_or_update(
                resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=source_endpoint,
                endpoint={"properties": {
                    "endpointType": "AzureMultiCloudConnector",
                    "multiCloudConnectorId": MULTI_CLOUD_CONNECTOR_ID,
                    "awsS3BucketId": AWS_PUBLIC_S3_BUCKET_ID,
                    "endpointKind": "Source",
                    "description": "publicMccSourceForJobRun",
                }},
            )

            target = await self.client.endpoints.create_or_update(
                resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=target_endpoint,
                endpoint={
                    "identity": {"type": "SystemAssigned"},
                    "properties": {
                        "endpointType": "AzureStorageBlobContainer",
                        "storageAccountResourceId": STORAGE_ACCOUNT_ID,
                        "blobContainerName": container_name,
                        "description": "blobTargetForJobRun",
                    },
                },
            )
            assert target.identity is not None and target.identity.principal_id, (
                "Target blob endpoint did not get an auto-assigned MSI principalId"
            )
            target_msi_principal_id = target.identity.principal_id

            await storage_client.blob_containers.create(
                resource_group_name=STORAGE_ACCOUNT_RG, account_name=STORAGE_ACCOUNT_NAME,
                container_name=container_name, blob_container={},
            )
            container_created = True

            role_definition_id = (
                "/subscriptions/" + SYNTHETICS_SUBSCRIPTION_ID
                + "/providers/Microsoft.Authorization/roleDefinitions/"
                + STORAGE_BLOB_DATA_CONTRIBUTOR_ROLE_DEF_GUID
            )
            await authorization_client.role_assignments.create(
                scope=container_scope, role_assignment_name=role_assignment_name,
                parameters={"properties": {
                    "roleDefinitionId": role_definition_id,
                    "principalId": target_msi_principal_id,
                    "principalType": "ServicePrincipal",
                }},
            )
            rbac_created = True

            jd = await self.client.job_definitions.create_or_update(
                resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
                job_definition_name=jd_name,
                job_definition={"properties": {
                    "copyMode": "Additive",
                    "sourceName": source_endpoint,
                    "targetName": target_endpoint,
                    "jobType": "CloudToCloud",
                    "sourceSubpath": "/",
                    "targetSubpath": "/",
                    "description": "JobDefForJobRunTest",
                }},
            )
            assert jd.name == jd_name
            assert jd.properties.source_name == source_endpoint
            assert jd.properties.target_name == target_endpoint
            assert jd.properties.copy_mode == "Additive"

            jd_get = await self.client.job_definitions.get(
                resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
                job_definition_name=jd_name,
            )
            assert jd_get.id == jd.id

            items = [j async for j in self.client.job_definitions.list(
                resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
            )]
            assert len(items) >= 1
            assert jd_name in [j.name for j in items]

            start_result = await self.client.job_definitions.start_job(
                resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
                job_definition_name=jd_name,
            )
            assert start_result.job_run_resource_id, "start_job did not return jobRunResourceId"
            job_run_name = start_result.job_run_resource_id.rstrip("/").split("/")[-1]

            terminal_states = {"Succeeded", "Failed", "Cancelled", "PartialSucceeded"}
            final_status = None
            for _ in range(60):
                run = await self.client.job_runs.get(
                    resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
                    job_definition_name=jd_name, job_run_name=job_run_name,
                )
                current_status = (
                    getattr(run.properties, "status", None) if run.properties is not None else None
                )
                if current_status in terminal_states:
                    final_status = current_status
                    break
                if self.is_live:
                    await asyncio.sleep(30)
            assert final_status is not None, (
                "Job run did not reach a terminal state within 30 min"
            )
            assert final_status == "Succeeded", (
                "Expected job-run to Succeed with public bucket + target MSI RBAC, "
                "got: " + str(final_status)
            )

            jd_poller = await self.client.job_definitions.begin_delete(
                resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
                job_definition_name=jd_name,
            )
            await jd_poller.result()

        finally:
            if rbac_created:
                try:
                    await authorization_client.role_assignments.delete(
                        scope=container_scope, role_assignment_name=role_assignment_name,
                    )
                except Exception:  # noqa: BLE001
                    pass
            if container_created:
                try:
                    await storage_client.blob_containers.delete(
                        resource_group_name=STORAGE_ACCOUNT_RG, account_name=STORAGE_ACCOUNT_NAME,
                        container_name=container_name,
                    )
                except Exception:  # noqa: BLE001
                    pass
            for cli in (storage_client, authorization_client):
                try:
                    await cli.close()
                except Exception:  # noqa: BLE001
                    pass

        return variables

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_create_with_weekly_schedule(self, resource_group, **kwargs):
        rg = resource_group.name
        sm_name = "testsm-jdwk"
        project_name = "testproj-jdwk"
        source_endpoint = "testnfsendpoint"
        target_endpoint = "testblobendpoint"
        await self._provision_parents(rg, sm_name, project_name, source_endpoint, target_endpoint)

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

        jd = await self.client.job_definitions.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
            job_definition_name=jd_name, job_definition=body,
        )
        assert jd.name == jd_name
        assert jd.properties.description == "Job definition with weekly schedule"
        assert jd.properties.schedule.frequency == "Weekly"
        assert jd.properties.schedule.is_active is True
        assert jd.properties.schedule.execution_time.hour == 2
        assert len(jd.properties.schedule.days_of_week) == 3

        jd = await self.client.job_definitions.get(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
            job_definition_name=jd_name,
        )
        assert jd.properties.schedule.frequency == "Weekly"

        poller = await self.client.job_definitions.begin_delete(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
            job_definition_name=jd_name,
        )
        await poller.result()

        return variables

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_create_with_daily_schedule_and_preserve_permissions(self, resource_group, **kwargs):
        rg = resource_group.name
        sm_name = "testsm-jddl"
        project_name = "testproj-jddl"
        source_endpoint = "testnfsendpoint"
        target_endpoint = "testblobendpoint"
        await self._provision_parents(rg, sm_name, project_name, source_endpoint, target_endpoint)

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

        jd = await self.client.job_definitions.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
            job_definition_name=jd_name, job_definition=body,
        )
        assert jd.name == jd_name
        assert jd.properties.copy_mode == "Mirror"
        assert jd.properties.schedule.frequency == "Daily"
        assert jd.properties.schedule.is_active is True

        poller = await self.client.job_definitions.begin_delete(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
            job_definition_name=jd_name,
        )
        await poller.result()

        return variables

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_create_with_onetime_schedule(self, resource_group, **kwargs):
        rg = resource_group.name
        sm_name = "testsm-jdot"
        project_name = "testproj-jdot"
        source_endpoint = "testnfsendpoint"
        target_endpoint = "testblobendpoint"
        await self._provision_parents(rg, sm_name, project_name, source_endpoint, target_endpoint)

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

        jd = await self.client.job_definitions.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
            job_definition_name=jd_name, job_definition=body,
        )
        assert jd.name == jd_name
        assert jd.properties.schedule.frequency == "Onetime"
        assert jd.properties.schedule.is_active is True

        poller = await self.client.job_definitions.begin_delete(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
            job_definition_name=jd_name,
        )
        await poller.result()

        return variables

    # ----- JobDefinitionJobRunTests.StartC2CJobWithPrivateSourceTest (matrix row #31) -----
    # See the sync sibling file for the full step-by-step description; this is the
    # async mirror.

    @RandomNameResourceGroupPreparer(location=WCUS_LOCATION)
    @recorded_by_proxy_async
    async def test_start_c2c_job_with_private_source(self, resource_group, **kwargs):
        rg = resource_group.name
        sm_name = "testsm-c2cpvt"
        project_name = "testproj-c2cpvt"
        connection_name = "testconn-pvt"
        source_endpoint = "testsrcep-mcc-pvt"
        target_endpoint = "testtgtep-blob-pvt"
        job_definition_name = "testjobdef-c2cpvt"

        variables = kwargs.pop("variables", {})
        container_name = variables.setdefault("container_name", "tc" + uuid.uuid4().hex[:10].lower())
        role_assignment_name = variables.setdefault("role_assignment_id", str(uuid.uuid4()))

        network_client = self.create_client_from_credential(
            NetworkManagementClient,
            self.get_credential(NetworkManagementClient, is_async=True),
            subscription_id=SYNTHETICS_SUBSCRIPTION_ID,
        )
        storage_client = self.create_client_from_credential(
            StorageManagementClient,
            self.get_credential(StorageManagementClient, is_async=True),
            subscription_id=SYNTHETICS_SUBSCRIPTION_ID,
        )
        authorization_client = self.create_client_from_credential(
            AuthorizationManagementClient,
            self.get_credential(AuthorizationManagementClient, is_async=True),
            subscription_id=SYNTHETICS_SUBSCRIPTION_ID,
        )

        connection_created = False
        container_created = False
        rbac_created = False
        container_scope = (
            STORAGE_ACCOUNT_ID + "/blobServices/default/containers/" + container_name
        )

        try:
            await self.client.storage_movers.create_or_update(
                resource_group_name=rg, storage_mover_name=sm_name,
                storage_mover={"location": WCUS_LOCATION},
            )
            await self.client.projects.create_or_update(
                resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
                project={},
            )

            connection = await self.client.connections.create_or_update(
                resource_group_name=rg, storage_mover_name=sm_name, connection_name=connection_name,
                connection={"properties": {
                    "privateLinkServiceId": REAL_PRIVATE_LINK_SERVICE_ID,
                    "description": "ConnectionForPrivateBucketJobRun",
                }},
            )
            connection_created = True
            pe_resource_id = connection.properties.private_endpoint_resource_id
            assert pe_resource_id, "Connection create did not return privateEndpointResourceId"

            pe_connection_name = None
            for _ in range(10):
                async for pec in network_client.private_link_services.list_private_endpoint_connections(
                    resource_group_name=PLS_RESOURCE_GROUP, service_name=PLS_NAME,
                ):
                    pec_pe_id = (pec.private_endpoint.id if pec.private_endpoint else "") or ""
                    if pec_pe_id.lower() == pe_resource_id.lower():
                        pe_connection_name = pec.name
                        break
                if pe_connection_name:
                    break
                if self.is_live:
                    await asyncio.sleep(15)
            assert pe_connection_name, (
                "PE-connection for {} did not appear on PLS {} within 150s".format(
                    pe_resource_id, PLS_NAME,
                )
            )

            await network_client.private_link_services.update_private_endpoint_connection(
                resource_group_name=PLS_RESOURCE_GROUP, service_name=PLS_NAME,
                pe_connection_name=pe_connection_name,
                parameters={"properties": {
                    "privateLinkServiceConnectionState": {
                        "status": "Approved",
                        "description": "approved by storage-mover SDK live test",
                        "actionsRequired": "None",
                    },
                }},
            )

            approved = False
            for _ in range(10):
                conn_show = await self.client.connections.get(
                    resource_group_name=rg, storage_mover_name=sm_name,
                    connection_name=connection_name,
                )
                if (conn_show.properties is not None
                        and getattr(conn_show.properties, "connection_status", None) == "Approved"):
                    approved = True
                    break
                if self.is_live:
                    await asyncio.sleep(30)
            assert approved, "Storage Mover Connection did not reach Approved within 300s"

            target = await self.client.endpoints.create_or_update(
                resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=target_endpoint,
                endpoint={
                    "identity": {"type": "SystemAssigned"},
                    "properties": {
                        "endpointType": "AzureStorageBlobContainer",
                        "storageAccountResourceId": STORAGE_ACCOUNT_ID,
                        "blobContainerName": container_name,
                        "description": "blobTargetForJobRunWait",
                    },
                },
            )
            assert target.identity is not None and target.identity.principal_id, (
                "Target blob endpoint did not get an auto-assigned MSI principalId"
            )
            target_msi_principal_id = target.identity.principal_id

            await storage_client.blob_containers.create(
                resource_group_name=STORAGE_ACCOUNT_RG, account_name=STORAGE_ACCOUNT_NAME,
                container_name=container_name, blob_container={},
            )
            container_created = True

            role_definition_id = (
                "/subscriptions/" + SYNTHETICS_SUBSCRIPTION_ID
                + "/providers/Microsoft.Authorization/roleDefinitions/"
                + STORAGE_BLOB_DATA_CONTRIBUTOR_ROLE_DEF_GUID
            )
            await authorization_client.role_assignments.create(
                scope=container_scope, role_assignment_name=role_assignment_name,
                parameters={"properties": {
                    "roleDefinitionId": role_definition_id,
                    "principalId": target_msi_principal_id,
                    "principalType": "ServicePrincipal",
                }},
            )
            rbac_created = True

            await self.client.endpoints.create_or_update(
                resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=source_endpoint,
                endpoint={"properties": {
                    "endpointType": "AzureMultiCloudConnector",
                    "multiCloudConnectorId": MULTI_CLOUD_CONNECTOR_ID,
                    "awsS3BucketId": PRIVATE_S3_BUCKET_ID,
                    "endpointKind": "Source",
                    "description": "privateMccSourceForJobRunWait",
                }},
            )

            await self.client.job_definitions.create_or_update(
                resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
                job_definition_name=job_definition_name,
                job_definition={"properties": {
                    "copyMode": "Additive",
                    "sourceName": source_endpoint,
                    "targetName": target_endpoint,
                    "jobType": "CloudToCloud",
                    "sourceSubpath": "/",
                    "targetSubpath": "/",
                    "connections": [connection.id],
                    "description": "JobDefForJobRunWaitTest",
                }},
            )

            start_result = await self.client.job_definitions.start_job(
                resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
                job_definition_name=job_definition_name,
            )
            assert start_result.job_run_resource_id, "start_job did not return jobRunResourceId"
            job_run_name = start_result.job_run_resource_id.rstrip("/").split("/")[-1]

            terminal_states = {"Succeeded", "Failed", "Cancelled", "PartialSucceeded"}
            final_status = None
            for _ in range(60):
                run = await self.client.job_runs.get(
                    resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
                    job_definition_name=job_definition_name, job_run_name=job_run_name,
                )
                current_status = (
                    getattr(run.properties, "status", None) if run.properties is not None else None
                )
                if current_status in terminal_states:
                    final_status = current_status
                    break
                if self.is_live:
                    await asyncio.sleep(30)
            assert final_status is not None, (
                "Job run did not reach a terminal state within 30 min"
            )
            assert final_status == "Succeeded", (
                "Expected job-run to Succeed with approved connection + target MSI RBAC, "
                "got: " + str(final_status)
            )

            jd_poller = await self.client.job_definitions.begin_delete(
                resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
                job_definition_name=job_definition_name,
            )
            await jd_poller.result()

        finally:
            if rbac_created:
                try:
                    await authorization_client.role_assignments.delete(
                        scope=container_scope, role_assignment_name=role_assignment_name,
                    )
                except Exception:  # noqa: BLE001
                    pass
            if container_created:
                try:
                    await storage_client.blob_containers.delete(
                        resource_group_name=STORAGE_ACCOUNT_RG, account_name=STORAGE_ACCOUNT_NAME,
                        container_name=container_name,
                    )
                except Exception:  # noqa: BLE001
                    pass
            if connection_created:
                try:
                    conn_del_poller = await self.client.connections.begin_delete(
                        resource_group_name=rg, storage_mover_name=sm_name,
                        connection_name=connection_name,
                    )
                    await conn_del_poller.result()
                except Exception:  # noqa: BLE001
                    pass
            # Close async cross-sub clients to release resources.
            for cli in (network_client, storage_client, authorization_client):
                try:
                    await cli.close()
                except Exception:  # noqa: BLE001
                    pass

        return variables
