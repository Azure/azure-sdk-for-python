# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import json
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

import pytest
from azure.core.credentials import AccessToken
from azure.core.pipeline.transport import AsyncHttpTransport, HttpTransport
from azure.mgmt.storagemover import StorageMoverMgmtClient, models
from azure.mgmt.storagemover.aio import (
    StorageMoverMgmtClient as AsyncStorageMoverMgmtClient,
)

SUBSCRIPTION_ID = "00000000-0000-0000-0000-000000000000"
PARTNER_TENANT_ID = "22222222-2222-2222-2222-222222222222"
STORAGE_ACCOUNT_ID = (
    f"/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/resource-group"
    "/providers/Microsoft.Storage/storageAccounts/account"
)
PARTNER_STORAGE_ACCOUNT_ID = (
    "/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/partner"
    "/providers/Microsoft.Storage/storageAccounts/partneraccount"
)
PARTNER_ENDPOINT_ID = (
    "/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/partner"
    "/providers/Microsoft.StorageMover/storageMovers/partner/endpoints/target"
)
CONNECTION_ID = (
    f"/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/resource-group"
    "/providers/Microsoft.StorageMover/storageMovers/mover/connections/connection"
)


class _RequestCaptured(Exception):
    def __init__(self, request):
        super().__init__("request captured")
        self.request = request


class _FakeCredential:
    def get_token(self, *scopes, **kwargs):  # pylint: disable=unused-argument
        return AccessToken("fake-token", 2147483647)


class _FakeAsyncCredential:
    async def get_token(self, *scopes, **kwargs):  # pylint: disable=unused-argument
        return AccessToken("fake-token", 2147483647)


class _CapturingTransport(HttpTransport):
    def send(self, request, **kwargs):  # pylint: disable=unused-argument
        raise _RequestCaptured(request)

    def open(self):
        pass

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class _AsyncCapturingTransport(AsyncHttpTransport):
    async def send(self, request, **kwargs):  # pylint: disable=unused-argument
        raise _RequestCaptured(request)

    async def open(self):
        pass

    async def close(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


def _capture_request(call):
    with pytest.raises(_RequestCaptured) as exc_info:
        call()
    return exc_info.value.request


async def _capture_request_async(awaitable):
    with pytest.raises(_RequestCaptured) as exc_info:
        await awaitable
    return exc_info.value.request


def _json_body(request):
    content = request.content
    if isinstance(content, bytes):
        content = content.decode("utf-8")
    return json.loads(content)


def _assert_request(request, method, path_suffix, expected_body):
    parsed = urlparse(request.url)
    assert request.method == method
    assert parsed.path.endswith(path_suffix)
    assert parse_qs(parsed.query)["api-version"] == ["2026-05-01"]
    if expected_body is None:
        assert request.content is None
    else:
        assert _json_body(request) == expected_body


def _endpoint_cases():
    return [
        (
            "blob-cross-tenant",
            models.Endpoint(
                properties=models.AzureStorageBlobContainerEndpointProperties(
                    storage_account_resource_id=STORAGE_ACCOUNT_ID,
                    blob_container_name="container",
                    endpoint_kind=models.EndpointKind.TARGET,
                    enable_cross_tenant_transfer=True,
                    allowed_storage_accounts=[PARTNER_STORAGE_ACCOUNT_ID],
                )
            ),
            {
                "storageAccountResourceId": STORAGE_ACCOUNT_ID,
                "blobContainerName": "container",
                "endpointKind": "Target",
                "enableCrossTenantTransfer": True,
                "allowedStorageAccounts": [PARTNER_STORAGE_ACCOUNT_ID],
                "endpointType": "AzureStorageBlobContainer",
            },
        ),
        (
            "smb-cross-tenant",
            models.Endpoint(
                properties=models.AzureStorageSmbFileShareEndpointProperties(
                    storage_account_resource_id=STORAGE_ACCOUNT_ID,
                    file_share_name="share",
                    endpoint_kind=models.EndpointKind.TARGET,
                    enable_cross_tenant_transfer=True,
                    allowed_storage_accounts=[PARTNER_STORAGE_ACCOUNT_ID],
                )
            ),
            {
                "storageAccountResourceId": STORAGE_ACCOUNT_ID,
                "fileShareName": "share",
                "endpointKind": "Target",
                "enableCrossTenantTransfer": True,
                "allowedStorageAccounts": [PARTNER_STORAGE_ACCOUNT_ID],
                "endpointType": "AzureStorageSmbFileShare",
            },
        ),
        (
            "nfs-fsx",
            models.Endpoint(
                properties=models.NfsMountEndpointProperties(
                    host="10.0.0.5",
                    export="/export",
                    endpoint_kind=models.EndpointKind.SOURCE,
                    nfs_version=models.NfsVersion.NF_SV4_1,
                    source_type=models.NfsMountSourceType.FSXEFS,
                )
            ),
            {
                "host": "10.0.0.5",
                "export": "/export",
                "endpointKind": "Source",
                "nfsVersion": "NFSv4_1",
                "sourceType": "FSX-EFS",
                "endpointType": "NfsMount",
            },
        ),
        (
            "smb-fsx",
            models.Endpoint(
                properties=models.SmbMountEndpointProperties(
                    host="10.0.0.6",
                    share_name="share",
                    endpoint_kind=models.EndpointKind.SOURCE,
                    source_type=models.SmbMountSourceType.FSXSMB,
                    credentials=models.AzureKeyVaultSmbCredentials(
                        username_uri="https://vault.vault.azure.net/secrets/username",
                        password_uri="https://vault.vault.azure.net/secrets/password",
                    ),
                )
            ),
            {
                "host": "10.0.0.6",
                "shareName": "share",
                "endpointKind": "Source",
                "sourceType": "FSX-SMB",
                "credentials": {
                    "usernameUri": "https://vault.vault.azure.net/secrets/username",
                    "passwordUri": "https://vault.vault.azure.net/secrets/password",
                    "type": "AzureKeyVaultSmb",
                },
                "endpointType": "SmbMount",
            },
        ),
    ]


def _cross_tenant_job_definition():
    return models.JobDefinition(
        properties=models.JobDefinitionProperties(
            copy_mode=models.CopyMode.ADDITIVE,
            source_name="source",
            target_name="target",
            job_type=models.JobType.CLOUD_TO_CLOUD,
            is_cross_tenant_job=True,
            cross_tenant_endpoint_tenant_id=PARTNER_TENANT_ID,
            cross_tenant_endpoint_resource_id=PARTNER_ENDPOINT_ID,
            sync_mode="SnapshotBased",
            mover_synced_until=datetime(2026, 5, 1, tzinfo=timezone.utc),
            schedule=models.ScheduleInfo(
                frequency=models.Frequency.HOURLY,
                repeat_interval="PT1H",
                is_active=True,
            ),
        )
    )


def _agentless_job_definition():
    return models.JobDefinition(
        properties=models.JobDefinitionProperties(
            copy_mode=models.CopyMode.ADDITIVE,
            source_name="source",
            target_name="target",
            job_type=models.JobType.ON_PREM_TO_CLOUD_AGENT_LESS,
            connections=[CONNECTION_ID],
        )
    )


def _job_definition_update():
    return models.JobDefinitionUpdateParameters(
        properties=models.JobDefinitionUpdateProperties(
            connections=[CONNECTION_ID],
            sync_mode="FullScan",
            mover_synced_until=datetime(2026, 5, 2, tzinfo=timezone.utc),
            schedule=models.ScheduleInfo(
                frequency=models.Frequency.HOURLY,
                repeat_interval="PT2H",
                is_active=False,
            ),
        )
    )


@pytest.mark.parametrize("endpoint_name,endpoint,expected_properties", _endpoint_cases())
def test_sync_endpoint_requests_match_cli_surface(endpoint_name, endpoint, expected_properties):
    with StorageMoverMgmtClient(
        _FakeCredential(),
        SUBSCRIPTION_ID,
        transport=_CapturingTransport(),
    ) as client:
        request = _capture_request(
            lambda: client.endpoints.create_or_update(
                "resource-group",
                "mover",
                endpoint_name,
                endpoint,
            )
        )

    _assert_request(
        request,
        "PUT",
        f"/storageMovers/mover/endpoints/{endpoint_name}",
        {"properties": expected_properties},
    )


@pytest.mark.parametrize("endpoint_name,endpoint,expected_properties", _endpoint_cases())
@pytest.mark.asyncio
async def test_async_endpoint_requests_match_cli_surface(endpoint_name, endpoint, expected_properties):
    async with AsyncStorageMoverMgmtClient(
        _FakeAsyncCredential(),
        SUBSCRIPTION_ID,
        transport=_AsyncCapturingTransport(),
    ) as client:
        request = await _capture_request_async(
            client.endpoints.create_or_update(
                "resource-group",
                "mover",
                endpoint_name,
                endpoint,
            )
        )

    _assert_request(
        request,
        "PUT",
        f"/storageMovers/mover/endpoints/{endpoint_name}",
        {"properties": expected_properties},
    )


def test_sync_job_definition_requests_match_cli_surface():
    with StorageMoverMgmtClient(
        _FakeCredential(),
        SUBSCRIPTION_ID,
        transport=_CapturingTransport(),
    ) as client:
        request = _capture_request(
            lambda: client.job_definitions.create_or_update(
                "resource-group",
                "mover",
                "project",
                "cross-tenant-job",
                _cross_tenant_job_definition(),
            )
        )
        _assert_request(
            request,
            "PUT",
            "/storageMovers/mover/projects/project/jobDefinitions/cross-tenant-job",
            {
                "properties": {
                    "copyMode": "Additive",
                    "sourceName": "source",
                    "targetName": "target",
                    "jobType": "CloudToCloud",
                    "isCrossTenantJob": True,
                    "crossTenantEndpointTenantId": PARTNER_TENANT_ID,
                    "crossTenantEndpointResourceId": PARTNER_ENDPOINT_ID,
                    "syncMode": "SnapshotBased",
                    "moverSyncedUntil": "2026-05-01T00:00:00Z",
                    "schedule": {
                        "frequency": "Hourly",
                        "repeatInterval": "PT1H",
                        "isActive": True,
                    },
                }
            },
        )

        request = _capture_request(
            lambda: client.job_definitions.create_or_update(
                "resource-group",
                "mover",
                "project",
                "agentless-job",
                _agentless_job_definition(),
            )
        )
        _assert_request(
            request,
            "PUT",
            "/storageMovers/mover/projects/project/jobDefinitions/agentless-job",
            {
                "properties": {
                    "copyMode": "Additive",
                    "sourceName": "source",
                    "targetName": "target",
                    "jobType": "OnPremToCloudAgentLess",
                    "connections": [CONNECTION_ID],
                }
            },
        )

        request = _capture_request(
            lambda: client.job_definitions.update(
                "resource-group",
                "mover",
                "project",
                "job",
                _job_definition_update(),
            )
        )
        _assert_request(
            request,
            "PATCH",
            "/storageMovers/mover/projects/project/jobDefinitions/job",
            {
                "properties": {
                    "connections": [CONNECTION_ID],
                    "syncMode": "FullScan",
                    "moverSyncedUntil": "2026-05-02T00:00:00Z",
                    "schedule": {
                        "frequency": "Hourly",
                        "repeatInterval": "PT2H",
                        "isActive": False,
                    },
                }
            },
        )

        request = _capture_request(
            lambda: client.job_definitions.reconcile_job(
                "resource-group",
                "mover",
                "project",
                "job",
            )
        )
        _assert_request(
            request,
            "POST",
            "/storageMovers/mover/projects/project/jobDefinitions/job/reconcileJob",
            None,
        )


@pytest.mark.asyncio
async def test_async_job_definition_requests_match_cli_surface():
    async with AsyncStorageMoverMgmtClient(
        _FakeAsyncCredential(),
        SUBSCRIPTION_ID,
        transport=_AsyncCapturingTransport(),
    ) as client:
        request = await _capture_request_async(
            client.job_definitions.create_or_update(
                "resource-group",
                "mover",
                "project",
                "cross-tenant-job",
                _cross_tenant_job_definition(),
            )
        )
        _assert_request(
            request,
            "PUT",
            "/storageMovers/mover/projects/project/jobDefinitions/cross-tenant-job",
            {
                "properties": {
                    "copyMode": "Additive",
                    "sourceName": "source",
                    "targetName": "target",
                    "jobType": "CloudToCloud",
                    "isCrossTenantJob": True,
                    "crossTenantEndpointTenantId": PARTNER_TENANT_ID,
                    "crossTenantEndpointResourceId": PARTNER_ENDPOINT_ID,
                    "syncMode": "SnapshotBased",
                    "moverSyncedUntil": "2026-05-01T00:00:00Z",
                    "schedule": {
                        "frequency": "Hourly",
                        "repeatInterval": "PT1H",
                        "isActive": True,
                    },
                }
            },
        )

        request = await _capture_request_async(
            client.job_definitions.create_or_update(
                "resource-group",
                "mover",
                "project",
                "agentless-job",
                _agentless_job_definition(),
            )
        )
        _assert_request(
            request,
            "PUT",
            "/storageMovers/mover/projects/project/jobDefinitions/agentless-job",
            {
                "properties": {
                    "copyMode": "Additive",
                    "sourceName": "source",
                    "targetName": "target",
                    "jobType": "OnPremToCloudAgentLess",
                    "connections": [CONNECTION_ID],
                }
            },
        )

        request = await _capture_request_async(
            client.job_definitions.update(
                "resource-group",
                "mover",
                "project",
                "job",
                _job_definition_update(),
            )
        )
        _assert_request(
            request,
            "PATCH",
            "/storageMovers/mover/projects/project/jobDefinitions/job",
            {
                "properties": {
                    "connections": [CONNECTION_ID],
                    "syncMode": "FullScan",
                    "moverSyncedUntil": "2026-05-02T00:00:00Z",
                    "schedule": {
                        "frequency": "Hourly",
                        "repeatInterval": "PT2H",
                        "isActive": False,
                    },
                }
            },
        )

        request = await _capture_request_async(
            client.job_definitions.reconcile_job(
                "resource-group",
                "mover",
                "project",
                "job",
            )
        )
        _assert_request(
            request,
            "POST",
            "/storageMovers/mover/projects/project/jobDefinitions/job/reconcileJob",
            None,
        )
