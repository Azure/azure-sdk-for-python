# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Async scenario tests for job_definitions.

Mirrors .NET JobDefinitionJobRunTests + JobDefinitionScheduleTests at:
  https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/storagemover/Azure.ResourceManager.StorageMover/tests/Scenario

Also implements cross-language matrix row #31
(`JobDefinitionJobRunTests.StartC2CJobWithPrivateSourceTest`) — see the sync
sibling file for the full rationale.

NOTE: The cross-sub mgmt clients (azure-mgmt-network / -authorization / -storage)
are imported from their `.aio` namespaces so the test-proxy's async-transport
interception covers them. Older versions of these packages (in particular the
floors pinned by the `mindependency` CI leg) lack the `.aio` submodule — we
use `pytest.importorskip` so collection skips this whole module cleanly in
that environment.
"""

import asyncio
import os
import uuid
from datetime import datetime, timedelta, timezone

import pytest

# Skip the entire module if the cross-sub `.aio` submodules aren't present
# (happens in `mindependency` CI legs that pin very old transitive versions).
pytest.importorskip("azure.mgmt.network.aio")
pytest.importorskip("azure.mgmt.storage.aio")
pytest.importorskip("azure.mgmt.authorization.v2022_04_01.aio")

from azure.core.exceptions import HttpResponseError
from azure.mgmt.authorization.v2022_04_01.aio import AuthorizationManagementClient
from azure.mgmt.network.aio import NetworkManagementClient
from azure.mgmt.storage.aio import StorageManagementClient
from azure.mgmt.storagemover.aio import StorageMoverMgmtClient

from devtools_testutils import AzureMgmtRecordedTestCase, EnvironmentVariableLoader, RandomNameResourceGroupPreparer
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
# The subscription id is read from the environment for live runs and defaults to
# the sanitized zero-GUID so the real subscription is never committed.
SYNTHETICS_SUBSCRIPTION_ID = (
    os.environ.get("STORAGEMOVER_SYNTHETICS_SUBSCRIPTION_ID") or "00000000-0000-0000-0000-000000000000"
)

PLS_RESOURCE_GROUP = "E2E-Management-RGsyn"
PRIVATE_LINK_SERVICE_ID_PREFIX = (
    "/subscriptions/"
    + SYNTHETICS_SUBSCRIPTION_ID
    + "/resourceGroups/"
    + PLS_RESOURCE_GROUP
    + "/providers/Microsoft.Network/privateLinkServices/"
)

STORAGE_ACCOUNT_RG = "CP_Mover_IN_WCUS"
STORAGE_ACCOUNT_NAME = "cpmoveraccount"
STORAGE_ACCOUNT_ID = (
    "/subscriptions/"
    + SYNTHETICS_SUBSCRIPTION_ID
    + "/resourceGroups/"
    + STORAGE_ACCOUNT_RG
    + "/providers/Microsoft.Storage/storageAccounts/"
    + STORAGE_ACCOUNT_NAME
)

MULTI_CLOUD_CONNECTOR_ID = (
    "/subscriptions/"
    + SYNTHETICS_SUBSCRIPTION_ID
    + "/resourceGroups/E2E-Management-RGsyn"
    + "/providers/Microsoft.HybridConnectivity/publicCloudConnectors/e2e-sm-rp-connector"
)
PRIVATE_S3_BUCKET_ID = (
    "/subscriptions/"
    + SYNTHETICS_SUBSCRIPTION_ID
    + "/resourceGroups/aws_640698235822"
    + "/providers/Microsoft.AWSConnector/s3Buckets/e2e-sm-rp-private-bucket"
)
AWS_PUBLIC_S3_BUCKET_ID = (
    "/subscriptions/"
    + SYNTHETICS_SUBSCRIPTION_ID
    + "/resourceGroups/aws_640698235822"
    + "/providers/Microsoft.AWSConnector/s3Buckets/e2e-sm-rp-bucket"
)

STORAGE_BLOB_DATA_CONTRIBUTOR_ROLE_DEF_GUID = "ba92f5b4-2d11-453d-a403-e96b0029c9fe"

# Hourly schedules (matrix row #35) are only deployed in eastus2euap so far.
EUAP_LOCATION = "eastus2euap"

# Persistent PLS that the RP's own agentless E2E tests use in eastus2euap (matrix row #39).
ECY_PRIVATE_LINK_SERVICE_ID = PRIVATE_LINK_SERVICE_ID_PREFIX + "E2E-VPC-PLS-E2ETest.Test.ECY"

# Placeholder partner tenant for the cross-tenant validation cases (matrix row #43).
PARTNER_TENANT_ID = "11111111-2222-3333-4444-555555555555"
PARTNER_SUBSCRIPTION_ID = "22222222-2222-2222-2222-222222222222"
PARTNER_STORAGE_ACCOUNT_ID = (
    f"/subscriptions/{PARTNER_SUBSCRIPTION_ID}/resourceGroups/partner-rg"
    "/providers/Microsoft.Storage/storageAccounts/partnersa"
)


def _endpoint_id(subscription_id, rg, sm_name, endpoint_name):
    return (
        f"/subscriptions/{subscription_id}/resourceGroups/{rg}"
        f"/providers/Microsoft.StorageMover/storageMovers/{sm_name}/endpoints/{endpoint_name}"
    )


class TestStorageMoverMgmtJobDefinitionsOperationsAsync(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(StorageMoverMgmtClient, is_async=True)

    async def _provision_parents(self, rg, sm_name, project_name, source_endpoint, target_endpoint):
        await self.client.storage_movers.create_or_update(
            resource_group_name=rg,
            storage_mover_name=sm_name,
            storage_mover={"location": AZURE_LOCATION},
        )
        await self.client.projects.create_or_update(
            resource_group_name=rg,
            storage_mover_name=sm_name,
            project_name=project_name,
            project={},
        )
        await self.client.endpoints.create_or_update(
            resource_group_name=rg,
            storage_mover_name=sm_name,
            endpoint_name=source_endpoint,
            endpoint={
                "properties": {
                    "endpointType": "NfsMount",
                    "host": "10.0.0.1",
                    "export": "/",
                    "nfsVersion": "NFSv3",
                }
            },
        )
        await self.client.endpoints.create_or_update(
            resource_group_name=rg,
            storage_mover_name=sm_name,
            endpoint_name=target_endpoint,
            endpoint={
                "properties": {
                    "endpointType": "AzureStorageBlobContainer",
                    "storageAccountResourceId": FAKE_STORAGE_ACCOUNT_ID,
                    "blobContainerName": "testcontainer",
                }
            },
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

        # Async cross-sub clients (test-proxy's async-transport interception
        # covers them; sync clients here would bypass the proxy and hit live).
        # Pin api_version explicitly so playback stays stable as the underlying
        # mgmt packages bump default api-versions in future releases.
        storage_client = self.create_client_from_credential(
            StorageManagementClient,
            self.get_credential(StorageManagementClient, is_async=True),
            subscription_id=SYNTHETICS_SUBSCRIPTION_ID,
            api_version="2025-06-01",
        )
        authorization_client = self.create_client_from_credential(
            AuthorizationManagementClient,
            self.get_credential(AuthorizationManagementClient, is_async=True),
            subscription_id=SYNTHETICS_SUBSCRIPTION_ID,
        )

        container_created = False
        rbac_created = False
        container_scope = STORAGE_ACCOUNT_ID + "/blobServices/default/containers/" + container_name

        try:
            await self.client.storage_movers.create_or_update(
                resource_group_name=rg,
                storage_mover_name=sm_name,
                storage_mover={"location": WCUS_LOCATION},
            )
            await self.client.projects.create_or_update(
                resource_group_name=rg,
                storage_mover_name=sm_name,
                project_name=project_name,
                project={},
            )

            await self.client.endpoints.create_or_update(
                resource_group_name=rg,
                storage_mover_name=sm_name,
                endpoint_name=source_endpoint,
                endpoint={
                    "properties": {
                        "endpointType": "AzureMultiCloudConnector",
                        "multiCloudConnectorId": MULTI_CLOUD_CONNECTOR_ID,
                        "awsS3BucketId": AWS_PUBLIC_S3_BUCKET_ID,
                        "endpointKind": "Source",
                        "description": "publicMccSourceForJobRun",
                    }
                },
            )

            target = await self.client.endpoints.create_or_update(
                resource_group_name=rg,
                storage_mover_name=sm_name,
                endpoint_name=target_endpoint,
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
            assert (
                target.identity is not None and target.identity.principal_id
            ), "Target blob endpoint did not get an auto-assigned MSI principalId"
            target_msi_principal_id = target.identity.principal_id

            await storage_client.blob_containers.create(
                resource_group_name=STORAGE_ACCOUNT_RG,
                account_name=STORAGE_ACCOUNT_NAME,
                container_name=container_name,
                blob_container={},
            )
            container_created = True

            role_definition_id = (
                "/subscriptions/"
                + SYNTHETICS_SUBSCRIPTION_ID
                + "/providers/Microsoft.Authorization/roleDefinitions/"
                + STORAGE_BLOB_DATA_CONTRIBUTOR_ROLE_DEF_GUID
            )
            await authorization_client.role_assignments.create(
                scope=container_scope,
                role_assignment_name=role_assignment_name,
                parameters={
                    "properties": {
                        "roleDefinitionId": role_definition_id,
                        "principalId": target_msi_principal_id,
                        "principalType": "ServicePrincipal",
                    }
                },
            )
            rbac_created = True

            jd = await self.client.job_definitions.create_or_update(
                resource_group_name=rg,
                storage_mover_name=sm_name,
                project_name=project_name,
                job_definition_name=jd_name,
                job_definition={
                    "properties": {
                        "copyMode": "Additive",
                        "sourceName": source_endpoint,
                        "targetName": target_endpoint,
                        "jobType": "CloudToCloud",
                        "sourceSubpath": "/",
                        "targetSubpath": "/",
                        "description": "JobDefForJobRunTest",
                    }
                },
            )
            assert jd.name == jd_name
            assert jd.properties.source_name == source_endpoint
            assert jd.properties.target_name == target_endpoint
            assert jd.properties.copy_mode == "Additive"

            jd_get = await self.client.job_definitions.get(
                resource_group_name=rg,
                storage_mover_name=sm_name,
                project_name=project_name,
                job_definition_name=jd_name,
            )
            assert jd_get.id == jd.id

            items = [
                j
                async for j in self.client.job_definitions.list(
                    resource_group_name=rg,
                    storage_mover_name=sm_name,
                    project_name=project_name,
                )
            ]
            assert len(items) >= 1
            assert jd_name in [j.name for j in items]

            start_result = await self.client.job_definitions.start_job(
                resource_group_name=rg,
                storage_mover_name=sm_name,
                project_name=project_name,
                job_definition_name=jd_name,
            )
            assert start_result.job_run_resource_id, "start_job did not return jobRunResourceId"
            job_run_name = start_result.job_run_resource_id.rstrip("/").split("/")[-1]

            terminal_states = {"Succeeded", "Failed", "Cancelled", "PartialSucceeded"}
            final_status = None
            for _ in range(60):
                run = await self.client.job_runs.get(
                    resource_group_name=rg,
                    storage_mover_name=sm_name,
                    project_name=project_name,
                    job_definition_name=jd_name,
                    job_run_name=job_run_name,
                )
                current_status = getattr(run.properties, "status", None) if run.properties is not None else None
                if current_status in terminal_states:
                    final_status = current_status
                    break
                if self.is_live:
                    await asyncio.sleep(30)
            assert final_status is not None, "Job run did not reach a terminal state within 30 min"
            assert (
                final_status == "Succeeded"
            ), "Expected job-run to Succeed with public bucket + target MSI RBAC, " "got: " + str(final_status)

            jd_poller = await self.client.job_definitions.begin_delete(
                resource_group_name=rg,
                storage_mover_name=sm_name,
                project_name=project_name,
                job_definition_name=jd_name,
            )
            await jd_poller.result()

        finally:
            if rbac_created:
                try:
                    await authorization_client.role_assignments.delete(
                        scope=container_scope,
                        role_assignment_name=role_assignment_name,
                    )
                except Exception:  # noqa: BLE001
                    pass
            if container_created:
                try:
                    await storage_client.blob_containers.delete(
                        resource_group_name=STORAGE_ACCOUNT_RG,
                        account_name=STORAGE_ACCOUNT_NAME,
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
        start_date = variables.setdefault("schedule_start", (now + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ"))
        end_date = variables.setdefault("schedule_end", (now + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ"))
        body = {
            "properties": {
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
            }
        }

        jd = await self.client.job_definitions.create_or_update(
            resource_group_name=rg,
            storage_mover_name=sm_name,
            project_name=project_name,
            job_definition_name=jd_name,
            job_definition=body,
        )
        assert jd.name == jd_name
        assert jd.properties.description == "Job definition with weekly schedule"
        assert jd.properties.schedule.frequency == "Weekly"
        assert jd.properties.schedule.is_active is True
        assert jd.properties.schedule.execution_time.hour == 2
        assert len(jd.properties.schedule.days_of_week) == 3

        jd = await self.client.job_definitions.get(
            resource_group_name=rg,
            storage_mover_name=sm_name,
            project_name=project_name,
            job_definition_name=jd_name,
        )
        assert jd.properties.schedule.frequency == "Weekly"

        poller = await self.client.job_definitions.begin_delete(
            resource_group_name=rg,
            storage_mover_name=sm_name,
            project_name=project_name,
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
        start_date = variables.setdefault("schedule_start", (now + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ"))
        end_date = variables.setdefault("schedule_end", (now + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ"))
        body = {
            "properties": {
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
            }
        }

        jd = await self.client.job_definitions.create_or_update(
            resource_group_name=rg,
            storage_mover_name=sm_name,
            project_name=project_name,
            job_definition_name=jd_name,
            job_definition=body,
        )
        assert jd.name == jd_name
        assert jd.properties.copy_mode == "Mirror"
        assert jd.properties.schedule.frequency == "Daily"
        assert jd.properties.schedule.is_active is True

        poller = await self.client.job_definitions.begin_delete(
            resource_group_name=rg,
            storage_mover_name=sm_name,
            project_name=project_name,
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
        start_date = variables.setdefault("schedule_start", (now + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ"))
        body = {
            "properties": {
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
            }
        }

        jd = await self.client.job_definitions.create_or_update(
            resource_group_name=rg,
            storage_mover_name=sm_name,
            project_name=project_name,
            job_definition_name=jd_name,
            job_definition=body,
        )
        assert jd.name == jd_name
        assert jd.properties.schedule.frequency == "Onetime"
        assert jd.properties.schedule.is_active is True

        poller = await self.client.job_definitions.begin_delete(
            resource_group_name=rg,
            storage_mover_name=sm_name,
            project_name=project_name,
            job_definition_name=jd_name,
        )
        await poller.result()

        return variables

    # ----- JobDefinitionJobRunTests.StartC2CJobWithPrivateSourceTest (matrix row #31) -----
    # See the sync sibling file for the full step-by-step description; this is the
    # async mirror.

    @EnvironmentVariableLoader("storagemover", storagemover_private_link_service_name="test-pls-wcs")
    @RandomNameResourceGroupPreparer(location=WCUS_LOCATION)
    @recorded_by_proxy_async
    async def test_start_c2c_job_with_private_source(
        self, resource_group, storagemover_private_link_service_name, **kwargs
    ):
        rg = resource_group.name
        pls_name = storagemover_private_link_service_name
        private_link_service_id = PRIVATE_LINK_SERVICE_ID_PREFIX + pls_name
        sm_name = "testsm-c2cpvt"
        project_name = "testproj-c2cpvt"
        connection_name = "testconn-pvt"
        source_endpoint = "testsrcep-mcc-pvt"
        target_endpoint = "testtgtep-blob-pvt"
        job_definition_name = "testjobdef-c2cpvt"

        variables = kwargs.pop("variables", {})
        container_name = variables.setdefault("container_name", "tc" + uuid.uuid4().hex[:10].lower())
        role_assignment_name = variables.setdefault("role_assignment_id", str(uuid.uuid4()))

        # Async cross-sub clients (test-proxy's async-transport interception
        # covers them; sync clients here would bypass the proxy and hit live).
        # Pin api_version explicitly — see #10 above.
        network_client = self.create_client_from_credential(
            NetworkManagementClient,
            self.get_credential(NetworkManagementClient, is_async=True),
            subscription_id=SYNTHETICS_SUBSCRIPTION_ID,
            api_version="2025-05-01",
        )
        storage_client = self.create_client_from_credential(
            StorageManagementClient,
            self.get_credential(StorageManagementClient, is_async=True),
            subscription_id=SYNTHETICS_SUBSCRIPTION_ID,
            api_version="2025-06-01",
        )
        authorization_client = self.create_client_from_credential(
            AuthorizationManagementClient,
            self.get_credential(AuthorizationManagementClient, is_async=True),
            subscription_id=SYNTHETICS_SUBSCRIPTION_ID,
        )

        connection_created = False
        container_created = False
        rbac_created = False
        container_scope = STORAGE_ACCOUNT_ID + "/blobServices/default/containers/" + container_name

        try:
            await self.client.storage_movers.create_or_update(
                resource_group_name=rg,
                storage_mover_name=sm_name,
                storage_mover={"location": WCUS_LOCATION},
            )
            await self.client.projects.create_or_update(
                resource_group_name=rg,
                storage_mover_name=sm_name,
                project_name=project_name,
                project={},
            )

            connection = await self.client.connections.create_or_update(
                resource_group_name=rg,
                storage_mover_name=sm_name,
                connection_name=connection_name,
                connection={
                    "properties": {
                        "privateLinkServiceId": private_link_service_id,
                        "description": "ConnectionForPrivateBucketJobRun",
                    }
                },
            )
            connection_created = True
            pe_resource_id = connection.properties.private_endpoint_resource_id
            assert pe_resource_id, "Connection create did not return privateEndpointResourceId"

            pe_connection_name = None
            for _ in range(10):
                async for pec in network_client.private_link_services.list_private_endpoint_connections(
                    resource_group_name=PLS_RESOURCE_GROUP,
                    service_name=pls_name,
                ):
                    pec_pe_id = (pec.private_endpoint.id if pec.private_endpoint else "") or ""
                    if pec_pe_id.lower() == pe_resource_id.lower():
                        pe_connection_name = pec.name
                        break
                if pe_connection_name:
                    break
                if self.is_live:
                    await asyncio.sleep(15)
            assert pe_connection_name, "PE-connection for {} did not appear on PLS {} within 150s".format(
                pe_resource_id,
                pls_name,
            )

            await network_client.private_link_services.update_private_endpoint_connection(
                resource_group_name=PLS_RESOURCE_GROUP,
                service_name=pls_name,
                pe_connection_name=pe_connection_name,
                parameters={
                    "properties": {
                        "privateLinkServiceConnectionState": {
                            "status": "Approved",
                            "description": "approved by storage-mover SDK live test",
                            "actionsRequired": "None",
                        },
                    }
                },
            )

            approved = False
            for _ in range(10):
                conn_show = await self.client.connections.get(
                    resource_group_name=rg,
                    storage_mover_name=sm_name,
                    connection_name=connection_name,
                )
                if (
                    conn_show.properties is not None
                    and getattr(conn_show.properties, "connection_status", None) == "Approved"
                ):
                    approved = True
                    break
                if self.is_live:
                    await asyncio.sleep(30)
            assert approved, "Storage Mover Connection did not reach Approved within 300s"

            target = await self.client.endpoints.create_or_update(
                resource_group_name=rg,
                storage_mover_name=sm_name,
                endpoint_name=target_endpoint,
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
            assert (
                target.identity is not None and target.identity.principal_id
            ), "Target blob endpoint did not get an auto-assigned MSI principalId"
            target_msi_principal_id = target.identity.principal_id

            await storage_client.blob_containers.create(
                resource_group_name=STORAGE_ACCOUNT_RG,
                account_name=STORAGE_ACCOUNT_NAME,
                container_name=container_name,
                blob_container={},
            )
            container_created = True

            role_definition_id = (
                "/subscriptions/"
                + SYNTHETICS_SUBSCRIPTION_ID
                + "/providers/Microsoft.Authorization/roleDefinitions/"
                + STORAGE_BLOB_DATA_CONTRIBUTOR_ROLE_DEF_GUID
            )
            await authorization_client.role_assignments.create(
                scope=container_scope,
                role_assignment_name=role_assignment_name,
                parameters={
                    "properties": {
                        "roleDefinitionId": role_definition_id,
                        "principalId": target_msi_principal_id,
                        "principalType": "ServicePrincipal",
                    }
                },
            )
            rbac_created = True

            await self.client.endpoints.create_or_update(
                resource_group_name=rg,
                storage_mover_name=sm_name,
                endpoint_name=source_endpoint,
                endpoint={
                    "properties": {
                        "endpointType": "AzureMultiCloudConnector",
                        "multiCloudConnectorId": MULTI_CLOUD_CONNECTOR_ID,
                        "awsS3BucketId": PRIVATE_S3_BUCKET_ID,
                        "endpointKind": "Source",
                        "description": "privateMccSourceForJobRunWait",
                    }
                },
            )

            await self.client.job_definitions.create_or_update(
                resource_group_name=rg,
                storage_mover_name=sm_name,
                project_name=project_name,
                job_definition_name=job_definition_name,
                job_definition={
                    "properties": {
                        "copyMode": "Additive",
                        "sourceName": source_endpoint,
                        "targetName": target_endpoint,
                        "jobType": "CloudToCloud",
                        "sourceSubpath": "/",
                        "targetSubpath": "/",
                        "connections": [connection.id],
                        "description": "JobDefForJobRunWaitTest",
                    }
                },
            )

            start_result = await self.client.job_definitions.start_job(
                resource_group_name=rg,
                storage_mover_name=sm_name,
                project_name=project_name,
                job_definition_name=job_definition_name,
            )
            assert start_result.job_run_resource_id, "start_job did not return jobRunResourceId"
            job_run_name = start_result.job_run_resource_id.rstrip("/").split("/")[-1]

            terminal_states = {"Succeeded", "Failed", "Cancelled", "PartialSucceeded"}
            final_status = None
            for _ in range(60):
                run = await self.client.job_runs.get(
                    resource_group_name=rg,
                    storage_mover_name=sm_name,
                    project_name=project_name,
                    job_definition_name=job_definition_name,
                    job_run_name=job_run_name,
                )
                current_status = getattr(run.properties, "status", None) if run.properties is not None else None
                if current_status in terminal_states:
                    final_status = current_status
                    break
                if self.is_live:
                    await asyncio.sleep(30)
            assert final_status is not None, "Job run did not reach a terminal state within 30 min"
            assert (
                final_status == "Succeeded"
            ), "Expected job-run to Succeed with approved connection + target MSI RBAC, " "got: " + str(final_status)

            jd_poller = await self.client.job_definitions.begin_delete(
                resource_group_name=rg,
                storage_mover_name=sm_name,
                project_name=project_name,
                job_definition_name=job_definition_name,
            )
            await jd_poller.result()

        finally:
            if rbac_created:
                try:
                    await authorization_client.role_assignments.delete(
                        scope=container_scope,
                        role_assignment_name=role_assignment_name,
                    )
                except Exception:  # noqa: BLE001
                    pass
            if container_created:
                try:
                    await storage_client.blob_containers.delete(
                        resource_group_name=STORAGE_ACCOUNT_RG,
                        account_name=STORAGE_ACCOUNT_NAME,
                        container_name=container_name,
                    )
                except Exception:  # noqa: BLE001
                    pass
            if connection_created:
                try:
                    conn_del_poller = await self.client.connections.begin_delete(
                        resource_group_name=rg,
                        storage_mover_name=sm_name,
                        connection_name=connection_name,
                    )
                    await conn_del_poller.result()
                except Exception:  # noqa: BLE001
                    pass
            for cli in (network_client, storage_client, authorization_client):
                try:
                    await cli.close()
                except Exception:  # noqa: BLE001
                    pass

        return variables

    # ----- Matrix row #35: JobDefinitionScheduleTests.CreateJobDefinitionWithHourlyScheduleTest (API 2026-05-01) -----
    # See the sync sibling file; this is the async mirror.

    @RandomNameResourceGroupPreparer(location=EUAP_LOCATION)
    @recorded_by_proxy_async
    async def test_create_with_hourly_schedule(self, resource_group, **kwargs):
        rg = resource_group.name
        sm_name = "testsm-jdhr"
        project_name = "testproj-jdhr"
        source_endpoint = "testsrcfsendpoint"
        target_endpoint = "testtgtfsendpoint"
        jd_name = "jobdef-sched-hourly"

        await self.client.storage_movers.create_or_update(
            resource_group_name=rg,
            storage_mover_name=sm_name,
            storage_mover={"location": EUAP_LOCATION},
        )
        await self.client.projects.create_or_update(
            resource_group_name=rg,
            storage_mover_name=sm_name,
            project_name=project_name,
            project={},
        )
        for endpoint_name, endpoint_kind, file_share_name in (
            (source_endpoint, "Source", "srcshare"),
            (target_endpoint, "Target", "tgtshare"),
        ):
            await self.client.endpoints.create_or_update(
                resource_group_name=rg,
                storage_mover_name=sm_name,
                endpoint_name=endpoint_name,
                endpoint={
                    "properties": {
                        "endpointType": "AzureStorageSmbFileShare",
                        "storageAccountResourceId": FAKE_STORAGE_ACCOUNT_ID,
                        "fileShareName": file_share_name,
                        "endpointKind": endpoint_kind,
                    }
                },
            )

        variables = kwargs.pop("variables", {})
        now = datetime.now(timezone.utc)
        start_date = variables.setdefault("schedule_start", (now + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ"))
        end_date = variables.setdefault("schedule_end", (now + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ"))

        def job_definition(repeat_interval):
            return {
                "properties": {
                    "copyMode": "Additive",
                    "jobType": "CloudToCloud",
                    "sourceName": source_endpoint,
                    "targetName": target_endpoint,
                    "sourceSubpath": "/",
                    "targetSubpath": "/",
                    "description": "Job definition with hourly schedule",
                    "schedule": {
                        "frequency": "Hourly",
                        "repeatInterval": repeat_interval,
                        "isActive": True,
                        "executionTime": {"hour": 9, "minute": 0},
                        "startDate": start_date,
                        "endDate": end_date,
                    },
                }
            }

        jd = await self.client.job_definitions.create_or_update(
            resource_group_name=rg,
            storage_mover_name=sm_name,
            project_name=project_name,
            job_definition_name=jd_name,
            job_definition=job_definition("4h"),
        )
        assert jd.name == jd_name
        assert jd.properties.schedule.frequency == "Hourly"
        assert jd.properties.schedule.repeat_interval == "4h"
        assert jd.properties.schedule.is_active is True

        jd = await self.client.job_definitions.get(
            resource_group_name=rg,
            storage_mover_name=sm_name,
            project_name=project_name,
            job_definition_name=jd_name,
        )
        assert jd.properties.schedule.frequency == "Hourly"
        assert jd.properties.schedule.repeat_interval == "4h"

        # A partial schedule PATCH is merged with the stored schedule.
        jd = await self.client.job_definitions.update(
            resource_group_name=rg,
            storage_mover_name=sm_name,
            project_name=project_name,
            job_definition_name=jd_name,
            job_definition={"properties": {"schedule": {"repeatInterval": "6h"}}},
        )
        assert jd.properties.schedule.frequency == "Hourly"
        assert jd.properties.schedule.repeat_interval == "6h"
        assert jd.properties.schedule.is_active is True

        jd = await self.client.job_definitions.update(
            resource_group_name=rg,
            storage_mover_name=sm_name,
            project_name=project_name,
            job_definition_name=jd_name,
            job_definition={"properties": {"schedule": {"isActive": False}}},
        )
        assert jd.properties.schedule.is_active is False
        assert jd.properties.schedule.repeat_interval == "6h"

        with pytest.raises(HttpResponseError) as exc_info:
            await self.client.job_definitions.create_or_update(
                resource_group_name=rg,
                storage_mover_name=sm_name,
                project_name=project_name,
                job_definition_name="jobdef-sched-hourly-bad",
                job_definition=job_definition("5h"),
            )
        assert exc_info.value.status_code == 400
        assert exc_info.value.error.code == "InvalidRequestPropertyValue"

        poller = await self.client.job_definitions.begin_delete(
            resource_group_name=rg,
            storage_mover_name=sm_name,
            project_name=project_name,
            job_definition_name=jd_name,
        )
        await poller.result()

        return variables

    # ----- Matrix row #43: CrossTenantTests.CrossTenantJobValidationTest (API 2026-05-01) -----
    # See the sync sibling file; this is the async mirror.

    @RandomNameResourceGroupPreparer(location=WCUS_LOCATION)
    @recorded_by_proxy_async
    async def test_cross_tenant_job_validation(self, resource_group):
        rg = resource_group.name
        sm_name = "testsm-xtval"
        project_name = "testproj-xtval"
        source_endpoint = "testsrcep-blob"
        partner_endpoint = "partner-tgtep"

        await self.client.storage_movers.create_or_update(
            resource_group_name=rg,
            storage_mover_name=sm_name,
            storage_mover={"location": WCUS_LOCATION},
        )
        await self.client.projects.create_or_update(
            resource_group_name=rg,
            storage_mover_name=sm_name,
            project_name=project_name,
            project={},
        )
        await self.client.endpoints.create_or_update(
            resource_group_name=rg,
            storage_mover_name=sm_name,
            endpoint_name=source_endpoint,
            endpoint={
                "properties": {
                    "endpointType": "AzureStorageBlobContainer",
                    "storageAccountResourceId": FAKE_STORAGE_ACCOUNT_ID,
                    "blobContainerName": "testcontainer",
                    "endpointKind": "Source",
                    "enableCrossTenantTransfer": True,
                    "allowedStorageAccounts": [PARTNER_STORAGE_ACCOUNT_ID],
                }
            },
        )

        cross_tenant_job = {
            "copyMode": "Additive",
            "jobType": "CloudToCloud",
            "sourceName": source_endpoint,
            "targetName": partner_endpoint,
            "isCrossTenantJob": True,
            "crossTenantEndpointTenantId": PARTNER_TENANT_ID,
            "crossTenantEndpointResourceId": _endpoint_id(
                PARTNER_SUBSCRIPTION_ID, "partner-rg", "partner-sm", partner_endpoint
            ),
        }

        def without(key):
            return {k: v for k, v in cross_tenant_job.items() if k != key}

        host_subscription_id = self.get_settings_value("SUBSCRIPTION_ID")
        invalid_jobs = {
            "jobdef-xt-no-tenant": without("crossTenantEndpointTenantId"),
            "jobdef-xt-no-resource": without("crossTenantEndpointResourceId"),
            "jobdef-xt-no-flag": without("isCrossTenantJob"),
            "jobdef-xt-not-c2c": {**cross_tenant_job, "jobType": "OnPremToCloud"},
            "jobdef-xt-same-sub": {
                **cross_tenant_job,
                "crossTenantEndpointResourceId": _endpoint_id(host_subscription_id, rg, sm_name, partner_endpoint),
            },
        }
        for jd_name, properties in invalid_jobs.items():
            with pytest.raises(HttpResponseError) as exc_info:
                await self.client.job_definitions.create_or_update(
                    resource_group_name=rg,
                    storage_mover_name=sm_name,
                    project_name=project_name,
                    job_definition_name=jd_name,
                    job_definition={"properties": properties},
                )
            assert exc_info.value.status_code == 400, jd_name
            assert exc_info.value.error.code == "InvalidRequestPropertyValue", jd_name

        # None of the rejected requests left a job definition behind.
        remaining = [
            jd
            async for jd in self.client.job_definitions.list(
                resource_group_name=rg,
                storage_mover_name=sm_name,
                project_name=project_name,
            )
        ]
        assert not remaining

    # ----- Matrix row #39: JobDefinitionTests.CreateAgentlessJobDefinitionTest (API 2026-05-01) -----
    # See the sync sibling file; this is the async mirror.

    @RandomNameResourceGroupPreparer(location=EUAP_LOCATION)
    @recorded_by_proxy_async
    async def test_create_agentless_job_definition(self, resource_group):
        rg = resource_group.name
        sm_name = "testsm-agentless"
        project_name = "testproj-agentless"
        connection_name = "testconn-agentless"
        source_endpoint = "testsrcep-smb"
        target_endpoint = "testtgtep-smbfs"
        jd_name = "jobdef-agentless"

        await self.client.storage_movers.create_or_update(
            resource_group_name=rg,
            storage_mover_name=sm_name,
            storage_mover={"location": EUAP_LOCATION},
        )
        await self.client.projects.create_or_update(
            resource_group_name=rg,
            storage_mover_name=sm_name,
            project_name=project_name,
            project={},
        )
        await self.client.endpoints.create_or_update(
            resource_group_name=rg,
            storage_mover_name=sm_name,
            endpoint_name=source_endpoint,
            endpoint={
                "properties": {
                    "endpointType": "SmbMount",
                    "host": "10.0.0.1",
                    "shareName": "testshare",
                    "credentials": {
                        "type": "AzureKeyVaultSmb",
                        "usernameUri": "https://examples-azureKeyVault.vault.azure.net/secrets/examples-username",
                        "passwordUri": "https://examples-azureKeyVault.vault.azure.net/secrets/examples-password",
                    },
                }
            },
        )
        await self.client.endpoints.create_or_update(
            resource_group_name=rg,
            storage_mover_name=sm_name,
            endpoint_name=target_endpoint,
            endpoint={
                "properties": {
                    "endpointType": "AzureStorageSmbFileShare",
                    "storageAccountResourceId": FAKE_STORAGE_ACCOUNT_ID,
                    "fileShareName": "testfileshare",
                }
            },
        )

        job_properties = {
            "copyMode": "Additive",
            "jobType": "OnPremToCloudAgentLess",
            "sourceName": source_endpoint,
            "targetName": target_endpoint,
            "sourceSubpath": "/",
            "targetSubpath": "/",
        }

        # Agentless jobs must reference at least one connection.
        with pytest.raises(HttpResponseError) as exc_info:
            await self.client.job_definitions.create_or_update(
                resource_group_name=rg,
                storage_mover_name=sm_name,
                project_name=project_name,
                job_definition_name=jd_name,
                job_definition={"properties": job_properties},
            )
        assert exc_info.value.status_code == 400
        assert exc_info.value.error.code == "InvalidRequestPropertyValue"

        connection = await self.client.connections.create_or_update(
            resource_group_name=rg,
            storage_mover_name=sm_name,
            connection_name=connection_name,
            connection={
                "properties": {
                    "privateLinkServiceId": ECY_PRIVATE_LINK_SERVICE_ID,
                    "description": "ConnectionForAgentlessJob",
                }
            },
        )
        try:
            assert connection.properties.connection_status in ("Pending", "Approved")

            jd = await self.client.job_definitions.create_or_update(
                resource_group_name=rg,
                storage_mover_name=sm_name,
                project_name=project_name,
                job_definition_name=jd_name,
                job_definition={"properties": {**job_properties, "connections": [connection.id]}},
            )
            assert jd.name == jd_name
            assert jd.properties.job_type == "OnPremToCloudAgentLess"
            assert jd.properties.connections == [connection.id]
            assert not jd.properties.agent_name

            jd = await self.client.job_definitions.get(
                resource_group_name=rg,
                storage_mover_name=sm_name,
                project_name=project_name,
                job_definition_name=jd_name,
            )
            assert jd.properties.job_type == "OnPremToCloudAgentLess"
            assert jd.properties.connections == [connection.id]

            poller = await self.client.job_definitions.begin_delete(
                resource_group_name=rg,
                storage_mover_name=sm_name,
                project_name=project_name,
                job_definition_name=jd_name,
            )
            await poller.result()
        finally:
            poller = await self.client.connections.begin_delete(
                resource_group_name=rg,
                storage_mover_name=sm_name,
                connection_name=connection_name,
            )
            await poller.result()
