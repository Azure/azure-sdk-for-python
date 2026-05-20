# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Sync scenario tests for job_definitions.

Mirrors .NET JobDefinitionJobRunTests + JobDefinitionScheduleTests at:
  Q:\\source\\azure-sdk-for-net\\sdk\\storagemover\\Azure.ResourceManager.StorageMover\\tests\\Scenario

Also implements cross-language matrix row #31
(`JobDefinitionJobRunTests.StartC2CJobWithPrivateSourceTest`) — the full
private-bucket CloudToCloud E2E using the shared `test-pls-wcs` PLS, mirroring
RP `Storage-XDataMove-RP/test/E2ETest/C2CTest/StartJobTest.cs::StartC2CJobWithPrivateSourceAsyncSuccessPathTest`.
"""
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from azure.core.exceptions import HttpResponseError
from azure.mgmt.storagemover import StorageMoverMgmtClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

# Detect whether the cross-sub mgmt clients are "modern enough" to flow through
# azure-core's RequestsTransport (which the test-proxy intercepts). The pre-20.0
# generations of azure-mgmt-storage / azure-mgmt-network / azure-mgmt-authorization
# use msrestazure's transport, bypass the proxy, and hit live ARM. The presence
# of the `.aio` submodule + the `v2022_04_01` authorization API version is a
# reliable signal of "post-modernization".
# The `mindependency` CI leg pins those packages to very old floors that lack
# these — skip the two cross-sub tests cleanly in that environment.
try:
    from azure.mgmt.authorization.v2022_04_01 import AuthorizationManagementClient
    from azure.mgmt.network import NetworkManagementClient
    from azure.mgmt.storage import StorageManagementClient
    import azure.mgmt.network.aio  # noqa: F401  (modernization signal)
    import azure.mgmt.storage.aio  # noqa: F401  (modernization signal)
    _CROSS_SUB_CLIENTS_MODERN = True
except ImportError:
    AuthorizationManagementClient = None  # type: ignore[assignment]
    NetworkManagementClient = None  # type: ignore[assignment]
    StorageManagementClient = None  # type: ignore[assignment]
    _CROSS_SUB_CLIENTS_MODERN = False

_SKIP_IF_CROSS_SUB_CLIENTS_OLD = pytest.mark.skipif(
    not _CROSS_SUB_CLIENTS_MODERN,
    reason=(
        "Cross-sub mgmt clients too old: pre-modernization versions of "
        "azure-mgmt-{storage,network,authorization} use msrestazure transport "
        "and bypass the test-proxy, hitting live ARM. Bump those packages to "
        "their post-azure-core releases (storage>=20, network>=19, authorization>=2) "
        "to enable this test."
    ),
)

AZURE_LOCATION = "eastus"
# Matrix row #31 runs in westcentralus because the shared PLS + storage account
# live there. Other tests in this file keep the default eastus location.
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

# Built-in role definition for "Storage Blob Data Contributor".
STORAGE_BLOB_DATA_CONTRIBUTOR_ROLE_DEF_GUID = "ba92f5b4-2d11-453d-a403-e96b0029c9fe"


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

    # ----- JobDefinitionJobRunTests.JobDefinitionJobRunTest (matrix row #10) -----
    # Original .NET version: create + get + list + StartJob + StopJob (no wait).
    # Python extension (2026-05-20, mirrors the CLI port's
    # `test_storage_mover_job_run_scenarios` enhancement): the full C2C
    # data-plane round-trip is exercised — source = MCC over the **public**
    # AWS S3 bucket `e2e-sm-rp-bucket`, target = blob container under shared
    # `cpmoveraccount` with the target endpoint's SystemAssigned MSI granted
    # Storage Blob Data Contributor, job-run polled until Succeeded.
    #
    # StopJob is NOT exercised after the Succeeded poll: the RP returns HTTP
    # 412 JobTerminated on already-terminal runs. The .NET equivalent calls
    # StartJob/StopJob without waiting; the SDK port favours Succeeded-validation
    # over StopJob API-surface coverage (which row #31 also skips).
    #
    # Unlike row #31 (private-bucket E2E), this row needs no Storage Mover
    # Connection / PrivateLinkService approval — the public bucket is reachable
    # via the MCC directly.

    @_SKIP_IF_CROSS_SUB_CLIENTS_OLD
    @RandomNameResourceGroupPreparer(location=WCUS_LOCATION)
    @recorded_by_proxy
    def test_job_definition_job_run(self, resource_group, **kwargs):
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
            StorageManagementClient, self.get_credential(StorageManagementClient),
            subscription_id=SYNTHETICS_SUBSCRIPTION_ID,
        )
        authorization_client = self.create_client_from_credential(
            AuthorizationManagementClient, self.get_credential(AuthorizationManagementClient),
            subscription_id=SYNTHETICS_SUBSCRIPTION_ID,
        )

        container_created = False
        rbac_created = False
        container_scope = (
            STORAGE_ACCOUNT_ID + "/blobServices/default/containers/" + container_name
        )

        try:
            # Provision mover + project (WCUS — required by cpmoveraccount).
            self.client.storage_movers.create_or_update(
                resource_group_name=rg, storage_mover_name=sm_name,
                storage_mover={"location": WCUS_LOCATION},
            )
            self.client.projects.create_or_update(
                resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
                project={},
            )

            # Source MCC endpoint over the PUBLIC AWS S3 bucket.
            self.client.endpoints.create_or_update(
                resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=source_endpoint,
                endpoint={"properties": {
                    "endpointType": "AzureMultiCloudConnector",
                    "multiCloudConnectorId": MULTI_CLOUD_CONNECTOR_ID,
                    "awsS3BucketId": AWS_PUBLIC_S3_BUCKET_ID,
                    "endpointKind": "Source",
                    "description": "publicMccSourceForJobRun",
                }},
            )

            # Target blob endpoint with explicit SystemAssigned MSI.
            target = self.client.endpoints.create_or_update(
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

            # Cross-sub: create target container.
            storage_client.blob_containers.create(
                resource_group_name=STORAGE_ACCOUNT_RG, account_name=STORAGE_ACCOUNT_NAME,
                container_name=container_name, blob_container={},
            )
            container_created = True

            # Cross-sub: grant target MSI Storage Blob Data Contributor on container scope.
            role_definition_id = (
                "/subscriptions/" + SYNTHETICS_SUBSCRIPTION_ID
                + "/providers/Microsoft.Authorization/roleDefinitions/"
                + STORAGE_BLOB_DATA_CONTRIBUTOR_ROLE_DEF_GUID
            )
            authorization_client.role_assignments.create(
                scope=container_scope, role_assignment_name=role_assignment_name,
                parameters={"properties": {
                    "roleDefinitionId": role_definition_id,
                    "principalId": target_msi_principal_id,
                    "principalType": "ServicePrincipal",
                }},
            )
            rbac_created = True

            # Create the job definition (C2C, no `connections` since no PLS).
            jd = self.client.job_definitions.create_or_update(
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
            # CRUD assertions (mirrors .NET matrix #10 spec).
            assert jd.name == jd_name
            assert jd.properties.source_name == source_endpoint
            assert jd.properties.target_name == target_endpoint
            assert jd.properties.copy_mode == "Additive"

            jd_get = self.client.job_definitions.get(
                resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
                job_definition_name=jd_name,
            )
            assert jd_get.id == jd.id

            items = list(self.client.job_definitions.list(
                resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
            ))
            assert len(items) >= 1
            assert jd_name in [j.name for j in items]

            # Start the job.
            start_result = self.client.job_definitions.start_job(
                resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
                job_definition_name=jd_name,
            )
            assert start_result.job_run_resource_id, "start_job did not return jobRunResourceId"
            job_run_name = start_result.job_run_resource_id.rstrip("/").split("/")[-1]

            # Poll job_runs.get every 30s up to 30 min until terminal.
            terminal_states = {"Succeeded", "Failed", "Cancelled", "PartialSucceeded"}
            final_status = None
            for _ in range(60):
                run = self.client.job_runs.get(
                    resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
                    job_definition_name=jd_name, job_run_name=job_run_name,
                )
                current_status = (
                    getattr(run.properties, "status", None) if run.properties is not None else None
                )
                if current_status in terminal_states:
                    final_status = current_status
                    break
                self.sleep(30)
            assert final_status is not None, (
                "Job run did not reach a terminal state within 30 min"
            )
            assert final_status == "Succeeded", (
                "Expected job-run to Succeed with public bucket + target MSI RBAC, "
                "got: " + str(final_status)
            )

            self.client.job_definitions.begin_delete(
                resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
                job_definition_name=jd_name,
            ).result()

        finally:
            if rbac_created:
                try:
                    authorization_client.role_assignments.delete(
                        scope=container_scope, role_assignment_name=role_assignment_name,
                    )
                except Exception:  # noqa: BLE001
                    pass
            if container_created:
                try:
                    storage_client.blob_containers.delete(
                        resource_group_name=STORAGE_ACCOUNT_RG, account_name=STORAGE_ACCOUNT_NAME,
                        container_name=container_name,
                    )
                except Exception:  # noqa: BLE001
                    pass

        return variables

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

    # ----- JobDefinitionJobRunTests.StartC2CJobWithPrivateSourceTest (matrix row #31) -----
    # Full private-bucket CloudToCloud E2E mirroring the RP test
    # Storage-XDataMove-RP/test/E2ETest/C2CTest/StartJobTest.cs::StartC2CJobWithPrivateSourceAsyncSuccessPathTest
    # 1) self-provision RG + mover + project in westcentralus
    # 2) create Storage Mover Connection -> capture PE id
    # 3) approve the auto-created PE-connection on the PLS (cross-sub)
    # 4) poll the storage mover Connection until properties.connectionStatus == Approved
    # 5) create target Blob endpoint, capture its system-assigned MSI principalId
    # 6) create the target container under the shared cpmoveraccount (cross-sub)
    # 7) grant the endpoint MSI Storage Blob Data Contributor on the container scope (cross-sub)
    # 8) create source MCC endpoint over the PRIVATE AWS S3 bucket
    # 9) create C2C job definition wired to the connection
    # 10) start_job -> poll job_runs.get every 30s up to 30 min, assert Succeeded
    # 11) cleanup (best-effort) of all cross-sub side effects
    # See the "Porter's reference" callout in the cross-language playbook
    # (storage-mover-scenario-tests-cross-language) for the canonical step-by-step.

    @_SKIP_IF_CROSS_SUB_CLIENTS_OLD
    @RandomNameResourceGroupPreparer(location=WCUS_LOCATION)
    @recorded_by_proxy
    def test_start_c2c_job_with_private_source(self, resource_group, **kwargs):
        rg = resource_group.name
        sm_name = "testsm-c2cpvt"
        project_name = "testproj-c2cpvt"
        connection_name = "testconn-pvt"
        source_endpoint = "testsrcep-mcc-pvt"
        target_endpoint = "testtgtep-blob-pvt"
        job_definition_name = "testjobdef-c2cpvt"

        # Recording-stable derived values — round-tripped via the `variables` dict
        # so playback uses the same names the recording captured.
        variables = kwargs.pop("variables", {})
        container_name = variables.setdefault("container_name", "tc" + uuid.uuid4().hex[:10].lower())
        role_assignment_name = variables.setdefault("role_assignment_id", str(uuid.uuid4()))

        # Cross-sub mgmt clients (override subscription_id at construction).
        network_client = self.create_client_from_credential(
            NetworkManagementClient, self.get_credential(NetworkManagementClient),
            subscription_id=SYNTHETICS_SUBSCRIPTION_ID,
        )
        storage_client = self.create_client_from_credential(
            StorageManagementClient, self.get_credential(StorageManagementClient),
            subscription_id=SYNTHETICS_SUBSCRIPTION_ID,
        )
        authorization_client = self.create_client_from_credential(
            AuthorizationManagementClient, self.get_credential(AuthorizationManagementClient),
            subscription_id=SYNTHETICS_SUBSCRIPTION_ID,
        )

        # Flags to drive best-effort cross-sub cleanup in finally.
        connection_created = False
        container_created = False
        rbac_created = False
        container_scope = (
            STORAGE_ACCOUNT_ID + "/blobServices/default/containers/" + container_name
        )

        try:
            # 1. Self-provision storage mover + project.
            self.client.storage_movers.create_or_update(
                resource_group_name=rg, storage_mover_name=sm_name,
                storage_mover={"location": WCUS_LOCATION},
            )
            self.client.projects.create_or_update(
                resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
                project={},
            )

            # 2. Create the Storage Mover Connection. The RP synchronously provisions
            #    a private endpoint on the PLS in Pending state and returns its id.
            connection = self.client.connections.create_or_update(
                resource_group_name=rg, storage_mover_name=sm_name, connection_name=connection_name,
                connection={"properties": {
                    "privateLinkServiceId": REAL_PRIVATE_LINK_SERVICE_ID,
                    "description": "ConnectionForPrivateBucketJobRun",
                }},
            )
            connection_created = True
            pe_resource_id = connection.properties.private_endpoint_resource_id
            assert pe_resource_id, "Connection create did not return privateEndpointResourceId"

            # 3. Wait for the auto-created PE-connection to appear on the PLS, then
            #    approve it via PLS PEC update (cross-sub call).
            pe_connection_name = None
            for _ in range(10):
                for pec in network_client.private_link_services.list_private_endpoint_connections(
                    resource_group_name=PLS_RESOURCE_GROUP, service_name=PLS_NAME,
                ):
                    pec_pe_id = (pec.private_endpoint.id if pec.private_endpoint else "") or ""
                    if pec_pe_id.lower() == pe_resource_id.lower():
                        pe_connection_name = pec.name
                        break
                if pe_connection_name:
                    break
                self.sleep(15)
            assert pe_connection_name, (
                "PE-connection for {} did not appear on PLS {} within 150s".format(
                    pe_resource_id, PLS_NAME,
                )
            )

            network_client.private_link_services.update_private_endpoint_connection(
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

            # 4. Poll Storage Mover Connection until connection_status == Approved.
            #    The storagemover side mirrors PLS state with up to ~5 min lag.
            approved = False
            for _ in range(10):
                conn_show = self.client.connections.get(
                    resource_group_name=rg, storage_mover_name=sm_name,
                    connection_name=connection_name,
                )
                if (conn_show.properties is not None
                        and getattr(conn_show.properties, "connection_status", None) == "Approved"):
                    approved = True
                    break
                self.sleep(30)
            assert approved, "Storage Mover Connection did not reach Approved within 300s"

            # 5. Create the target blob endpoint. Explicitly request a SystemAssigned
            #    MSI — unlike the CLI's `endpoint create-for-storage-container` command
            #    (which auto-injects identity), the raw SDK PUT does not set identity
            #    by default. Capture principalId so we can grant data-plane RBAC.
            target = self.client.endpoints.create_or_update(
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

            # 6. Cross-sub: create the target blob container under cpmoveraccount.
            storage_client.blob_containers.create(
                resource_group_name=STORAGE_ACCOUNT_RG, account_name=STORAGE_ACCOUNT_NAME,
                container_name=container_name, blob_container={},
            )
            container_created = True

            # 7. Cross-sub: grant the endpoint MSI Storage Blob Data Contributor on
            #    the container scope.
            role_definition_id = (
                "/subscriptions/" + SYNTHETICS_SUBSCRIPTION_ID
                + "/providers/Microsoft.Authorization/roleDefinitions/"
                + STORAGE_BLOB_DATA_CONTRIBUTOR_ROLE_DEF_GUID
            )
            authorization_client.role_assignments.create(
                scope=container_scope, role_assignment_name=role_assignment_name,
                parameters={"properties": {
                    "roleDefinitionId": role_definition_id,
                    "principalId": target_msi_principal_id,
                    "principalType": "ServicePrincipal",
                }},
            )
            rbac_created = True

            # 8. Source MCC endpoint over the PRIVATE AWS S3 bucket.
            self.client.endpoints.create_or_update(
                resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=source_endpoint,
                endpoint={"properties": {
                    "endpointType": "AzureMultiCloudConnector",
                    "multiCloudConnectorId": MULTI_CLOUD_CONNECTOR_ID,
                    "awsS3BucketId": PRIVATE_S3_BUCKET_ID,
                    "endpointKind": "Source",
                    "description": "privateMccSourceForJobRunWait",
                }},
            )

            # 9. C2C job definition wired to the approved connection.
            self.client.job_definitions.create_or_update(
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

            # 10. Start the job. The RP returns the job-run resource id; extract basename.
            start_result = self.client.job_definitions.start_job(
                resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
                job_definition_name=job_definition_name,
            )
            assert start_result.job_run_resource_id, "start_job did not return jobRunResourceId"
            job_run_name = start_result.job_run_resource_id.rstrip("/").split("/")[-1]

            # 11. Poll job_runs.get every 30s up to 30 min until terminal.
            terminal_states = {"Succeeded", "Failed", "Cancelled", "PartialSucceeded"}
            final_status = None
            for _ in range(60):
                run = self.client.job_runs.get(
                    resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
                    job_definition_name=job_definition_name, job_run_name=job_run_name,
                )
                current_status = (
                    getattr(run.properties, "status", None) if run.properties is not None else None
                )
                if current_status in terminal_states:
                    final_status = current_status
                    break
                self.sleep(30)
            assert final_status is not None, (
                "Job run did not reach a terminal state within 30 min"
            )
            assert final_status == "Succeeded", (
                "Expected job-run to Succeed with approved connection + target MSI RBAC, "
                "got: " + str(final_status)
            )

            # Cleanup the job definition (other resources rolled back in finally).
            self.client.job_definitions.begin_delete(
                resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
                job_definition_name=job_definition_name,
            ).result()

        finally:
            # Best-effort cleanup of cross-sub side effects in shared infra. Order
            # matters: RBAC then container then connection (container can't be
            # deleted while it has active RBAC pinning the principal).
            if rbac_created:
                try:
                    authorization_client.role_assignments.delete(
                        scope=container_scope, role_assignment_name=role_assignment_name,
                    )
                except Exception:  # noqa: BLE001
                    pass
            if container_created:
                try:
                    storage_client.blob_containers.delete(
                        resource_group_name=STORAGE_ACCOUNT_RG, account_name=STORAGE_ACCOUNT_NAME,
                        container_name=container_name,
                    )
                except Exception:  # noqa: BLE001
                    pass
            if connection_created:
                try:
                    self.client.connections.begin_delete(
                        resource_group_name=rg, storage_mover_name=sm_name,
                        connection_name=connection_name,
                    ).result()
                except Exception:  # noqa: BLE001
                    pass

        return variables
