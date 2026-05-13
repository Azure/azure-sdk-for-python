# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Async scenario tests for endpoints.

Mirrors .NET EndpointTests at:
  Q:\\source\\azure-sdk-for-net\\sdk\\storagemover\\Azure.ResourceManager.StorageMover\\tests\\Scenario\\EndpointTests.cs
"""
import pytest
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.mgmt.storagemover.aio import StorageMoverMgmtClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer
from devtools_testutils.aio import recorded_by_proxy_async

AZURE_LOCATION = "eastus"
STORAGE_ACCOUNT_NAME = "testsmstore24"
CONTAINER_NAME = "testsmcontainer"

FAKE_SUBSCRIPTION_ID = "00000000-0000-0000-0000-000000000000"
MULTI_CLOUD_CONNECTOR_ID = (
    "/subscriptions/b6b34ad8-ca89-4f85-beb7-c2ec13702dac"
    "/resourceGroups/E2E-Management-RGsyn"
    "/providers/Microsoft.HybridConnectivity/publicCloudConnectors/e2e-sm-rp-connector"
)
AWS_S3_BUCKET_ID = (
    "/subscriptions/b6b34ad8-ca89-4f85-beb7-c2ec13702dac"
    "/resourceGroups/aws_640698235822"
    "/providers/Microsoft.AWSConnector/s3Buckets/e2e-sm-rp-bucket"
)


def _account_id(rg):
    return (
        f"/subscriptions/{FAKE_SUBSCRIPTION_ID}/resourceGroups/{rg}"
        f"/providers/Microsoft.Storage/storageAccounts/{STORAGE_ACCOUNT_NAME}"
    )


class TestStorageMoverMgmtEndpointsOperationsAsync(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(StorageMoverMgmtClient, is_async=True)

    async def _create_storage_mover(self, rg, sm_name):
        await self.client.storage_movers.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name,
            storage_mover={"location": AZURE_LOCATION},
        )

    async def _delete_endpoint(self, rg, sm_name, endpoint_name):
        poller = await self.client.endpoints.begin_delete(
            resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=endpoint_name,
        )
        await poller.result()

    # ----- EndpointTests.CreateUpdateGetDeleteTest -----

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_create_update_get_delete(self, resource_group):
        rg = resource_group.name
        sm_name = "testsm-epcrud"
        await self._create_storage_mover(rg, sm_name)

        c_name = "conendpoint-1"
        nfs_name = "nfsendpoint-1"
        smb_name = "smbendpoint-1"
        fs_name = "fsendpoint-1"

        c = await self.client.endpoints.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=c_name,
            endpoint={"properties": {
                "endpointType": "AzureStorageBlobContainer",
                "storageAccountResourceId": _account_id(rg),
                "blobContainerName": CONTAINER_NAME,
                "description": "New container endpoint",
            }},
        )
        assert c.name == c_name
        assert c.properties.endpoint_type == "AzureStorageBlobContainer"

        c_get = await self.client.endpoints.get(
            resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=c_name,
        )
        assert c_get.name == c_name

        nfs = await self.client.endpoints.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=nfs_name,
            endpoint={"properties": {
                "endpointType": "NfsMount",
                "host": "10.0.0.1",
                "export": "/",
                "nfsVersion": "NFSv3",
                "description": "New NFS endpoint",
            }},
        )
        assert nfs.properties.host == "10.0.0.1"
        assert nfs.properties.export == "/"

        nfs_get = await self.client.endpoints.get(
            resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=nfs_name,
        )
        assert nfs_get.properties.host == "10.0.0.1"

        smb = await self.client.endpoints.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=smb_name,
            endpoint={"properties": {
                "endpointType": "SmbMount",
                "host": "10.0.0.1",
                "shareName": "testshare",
                "credentials": {
                    "type": "AzureKeyVaultSmb",
                    "usernameUri": "https://examples-azureKeyVault.vault.azure.net/secrets/examples-username",
                    "passwordUri": "https://examples-azureKeyVault.vault.azure.net/secrets/examples-password",
                },
                "description": "New Smb mount endpoint",
            }},
        )
        assert smb.properties.share_name == "testshare"

        # Workaround for an RP regression in api-version 2025-12-01: the endpoint
        # PATCH (update) handler requires a non-null `identity` on the payload root.
        # The PUT (create) above succeeds without identity — so this is specifically
        # an update-path validation bug, not a real schema requirement. Sending
        # `{"type": "None"}` (the standard ARM "no managed identity" sentinel)
        # satisfies the check. The .NET test omits identity entirely and would also
        # fail today against this api-version.
        smb_updated = await self.client.endpoints.update(
            resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=smb_name,
            endpoint={
                "identity": {"type": "None"},
                "properties": {
                    "endpointType": "SmbMount",
                    "credentials": {
                        "type": "AzureKeyVaultSmb",
                        "usernameUri": "",
                        "passwordUri": "",
                    },
                    "description": "Update endpoint",
                },
            },
        )
        assert smb_updated.properties.host == "10.0.0.1"
        assert smb_updated.properties.share_name == "testshare"

        await self._delete_endpoint(rg, sm_name, smb_name)

        fs = await self.client.endpoints.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=fs_name,
            endpoint={"properties": {
                "endpointType": "AzureStorageSmbFileShare",
                "storageAccountResourceId": _account_id(rg),
                "fileShareName": "testfileshare",
                "description": "new file share endpoint",
            }},
        )
        assert fs.properties.file_share_name == "testfileshare"

        fs_get = await self.client.endpoints.get(
            resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=fs_name,
        )
        assert fs_get.properties.description == "new file share endpoint"

        items = [e async for e in self.client.endpoints.list(
            resource_group_name=rg, storage_mover_name=sm_name,
        )]
        assert len(items) > 1

        with pytest.raises(ResourceNotFoundError):
            await self.client.endpoints.get(
                resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=c_name + "111",
            )
        with pytest.raises(ResourceNotFoundError):
            await self.client.endpoints.get(
                resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=smb_name,
            )

    # ----- EndpointTests.MultiCloudConnectorEndpointCreateGetDeleteTest -----

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_multi_cloud_connector_create_get_delete(self, resource_group):
        rg = resource_group.name
        sm_name = "testsm-mcccrud"
        await self._create_storage_mover(rg, sm_name)

        endpoint_name = "mcc-1"
        endpoint = await self.client.endpoints.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=endpoint_name,
            endpoint={"properties": {
                "endpointType": "AzureMultiCloudConnector",
                "multiCloudConnectorId": MULTI_CLOUD_CONNECTOR_ID,
                "awsS3BucketId": AWS_S3_BUCKET_ID,
                "description": "Test multi-cloud connector endpoint",
            }},
        )
        assert endpoint.name == endpoint_name
        assert endpoint.properties.endpoint_type == "AzureMultiCloudConnector"

        endpoint = await self.client.endpoints.get(
            resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=endpoint_name,
        )
        assert endpoint.properties.description == "Test multi-cloud connector endpoint"
        assert endpoint.properties.multi_cloud_connector_id is not None
        assert endpoint.properties.aws_s3_bucket_id is not None

        await self._delete_endpoint(rg, sm_name, endpoint_name)
        with pytest.raises(ResourceNotFoundError):
            await self.client.endpoints.get(
                resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=endpoint_name,
            )

    # ----- EndpointTests.S3WithHmacEndpointCreateGetDeleteTest -----
    # NOTE: .NET marks this [Ignore] ("requires live S3 resources that are not yet
    # available for recording"). Running it anyway as the user asked — the request
    # uses placeholder URIs/credentials, so the RP may reject them.

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_s3_with_hmac_create_get_delete(self, resource_group):
        rg = resource_group.name
        sm_name = "testsm-s3hmac"
        await self._create_storage_mover(rg, sm_name)

        endpoint_name = "s3hmac-1"
        body = {"properties": {
            "endpointType": "S3WithHMAC",
            "sourceUri": "https://s3.example.com/bucket",
            "sourceType": "MINIO",
            "description": "Test S3 with HMAC endpoint",
            "credentials": {
                "type": "AzureKeyVaultS3WithHMAC",
                "accessKeyUri": "https://examples-azureKeyVault.vault.azure.net/secrets/examples-accesskey",
                "secretKeyUri": "https://examples-azureKeyVault.vault.azure.net/secrets/examples-secretkey",
            },
        }}

        endpoint = await self.client.endpoints.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=endpoint_name,
            endpoint=body,
        )
        assert endpoint.name == endpoint_name
        assert endpoint.properties.endpoint_type == "S3WithHMAC"

        endpoint = await self.client.endpoints.get(
            resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=endpoint_name,
        )
        assert endpoint.name == endpoint_name
        assert endpoint.properties.source_uri == "https://s3.example.com/bucket"
        assert endpoint.properties.source_type == "MINIO"
        assert endpoint.properties.description == "Test S3 with HMAC endpoint"
        assert endpoint.properties.credentials is not None
        assert endpoint.properties.credentials.access_key_uri == \
            "https://examples-azureKeyVault.vault.azure.net/secrets/examples-accesskey"
        assert endpoint.properties.credentials.secret_key_uri == \
            "https://examples-azureKeyVault.vault.azure.net/secrets/examples-secretkey"

        await self._delete_endpoint(rg, sm_name, endpoint_name)
        with pytest.raises(ResourceNotFoundError):
            await self.client.endpoints.get(
                resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=endpoint_name,
            )

    # ----- valid-EndpointKind tests -----

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_nfs_mount_kind_source(self, resource_group):
        rg = resource_group.name
        sm_name = "testsm-nfssrc"
        await self._create_storage_mover(rg, sm_name)

        endpoint_name = "nfs-src-1"
        endpoint = await self.client.endpoints.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=endpoint_name,
            endpoint={"properties": {
                "endpointType": "NfsMount",
                "host": "10.0.0.1",
                "export": "/",
                "endpointKind": "Source",
                "description": "NFS source endpoint",
            }},
        )
        assert endpoint.properties.endpoint_kind == "Source"
        await self._delete_endpoint(rg, sm_name, endpoint_name)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_smb_mount_kind_source(self, resource_group):
        rg = resource_group.name
        sm_name = "testsm-smbsrc"
        await self._create_storage_mover(rg, sm_name)

        endpoint_name = "smb-src-1"
        endpoint = await self.client.endpoints.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=endpoint_name,
            endpoint={"properties": {
                "endpointType": "SmbMount",
                "host": "10.0.0.1",
                "shareName": "testshare",
                "endpointKind": "Source",
                "description": "SMB source endpoint",
            }},
        )
        assert endpoint.properties.endpoint_kind == "Source"
        await self._delete_endpoint(rg, sm_name, endpoint_name)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_multi_cloud_connector_kind_source(self, resource_group):
        rg = resource_group.name
        sm_name = "testsm-mccsrc"
        await self._create_storage_mover(rg, sm_name)

        endpoint_name = "mcc-src-1"
        endpoint = await self.client.endpoints.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=endpoint_name,
            endpoint={"properties": {
                "endpointType": "AzureMultiCloudConnector",
                "multiCloudConnectorId": MULTI_CLOUD_CONNECTOR_ID,
                "awsS3BucketId": AWS_S3_BUCKET_ID,
                "endpointKind": "Source",
                "description": "Multi-cloud connector source endpoint",
            }},
        )
        assert endpoint.properties.endpoint_kind == "Source"
        await self._delete_endpoint(rg, sm_name, endpoint_name)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_blob_container_kind_source(self, resource_group):
        rg = resource_group.name
        sm_name = "testsm-blobsrc"
        await self._create_storage_mover(rg, sm_name)

        endpoint_name = "blob-src-1"
        endpoint = await self.client.endpoints.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=endpoint_name,
            endpoint={"properties": {
                "endpointType": "AzureStorageBlobContainer",
                "storageAccountResourceId": _account_id(rg),
                "blobContainerName": CONTAINER_NAME,
                "endpointKind": "Source",
                "description": "Blob container source endpoint",
            }},
        )
        assert endpoint.properties.endpoint_kind == "Source"
        await self._delete_endpoint(rg, sm_name, endpoint_name)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_blob_container_kind_target(self, resource_group):
        rg = resource_group.name
        sm_name = "testsm-blobtgt"
        await self._create_storage_mover(rg, sm_name)

        endpoint_name = "blob-tgt-1"
        endpoint = await self.client.endpoints.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=endpoint_name,
            endpoint={"properties": {
                "endpointType": "AzureStorageBlobContainer",
                "storageAccountResourceId": _account_id(rg),
                "blobContainerName": CONTAINER_NAME,
                "endpointKind": "Target",
                "description": "Blob container target endpoint",
            }},
        )
        assert endpoint.properties.endpoint_kind == "Target"
        await self._delete_endpoint(rg, sm_name, endpoint_name)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_smb_file_share_kind_target(self, resource_group):
        rg = resource_group.name
        sm_name = "testsm-smbfstgt"
        await self._create_storage_mover(rg, sm_name)

        endpoint_name = "smbfs-tgt-1"
        endpoint = await self.client.endpoints.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=endpoint_name,
            endpoint={"properties": {
                "endpointType": "AzureStorageSmbFileShare",
                "storageAccountResourceId": _account_id(rg),
                "fileShareName": "testfileshare",
                "endpointKind": "Target",
                "description": "SMB file share target endpoint",
            }},
        )
        assert endpoint.properties.endpoint_kind == "Target"
        await self._delete_endpoint(rg, sm_name, endpoint_name)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_nfs_file_share_kind_target(self, resource_group):
        rg = resource_group.name
        sm_name = "testsm-nfsfstgt"
        await self._create_storage_mover(rg, sm_name)

        endpoint_name = "nfsfs-tgt-1"
        endpoint = await self.client.endpoints.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=endpoint_name,
            endpoint={"properties": {
                "endpointType": "AzureStorageNfsFileShare",
                "storageAccountResourceId": _account_id(rg),
                "fileShareName": "testnfsfileshare",
                "endpointKind": "Target",
                "description": "NFS file share target endpoint",
            }},
        )
        assert endpoint.properties.endpoint_kind == "Target"
        await self._delete_endpoint(rg, sm_name, endpoint_name)

    # ----- invalid-EndpointKind tests -----

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_nfs_mount_kind_target_fails(self, resource_group):
        rg = resource_group.name
        sm_name = "testsm-nfstgtfail"
        await self._create_storage_mover(rg, sm_name)

        with pytest.raises(HttpResponseError):
            await self.client.endpoints.create_or_update(
                resource_group_name=rg, storage_mover_name=sm_name, endpoint_name="nfs-tgt-1",
                endpoint={"properties": {
                    "endpointType": "NfsMount",
                    "host": "10.0.0.1",
                    "export": "/",
                    "endpointKind": "Target",
                }},
            )

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_smb_mount_kind_target_fails(self, resource_group):
        rg = resource_group.name
        sm_name = "testsm-smbtgtfail"
        await self._create_storage_mover(rg, sm_name)

        with pytest.raises(HttpResponseError):
            await self.client.endpoints.create_or_update(
                resource_group_name=rg, storage_mover_name=sm_name, endpoint_name="smb-tgt-1",
                endpoint={"properties": {
                    "endpointType": "SmbMount",
                    "host": "10.0.0.1",
                    "shareName": "testshare",
                    "endpointKind": "Target",
                }},
            )

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_multi_cloud_connector_kind_target_fails(self, resource_group):
        rg = resource_group.name
        sm_name = "testsm-mcctgtfail"
        await self._create_storage_mover(rg, sm_name)

        with pytest.raises(HttpResponseError):
            await self.client.endpoints.create_or_update(
                resource_group_name=rg, storage_mover_name=sm_name, endpoint_name="mcc-tgt-1",
                endpoint={"properties": {
                    "endpointType": "AzureMultiCloudConnector",
                    "multiCloudConnectorId": MULTI_CLOUD_CONNECTOR_ID,
                    "awsS3BucketId": AWS_S3_BUCKET_ID,
                    "endpointKind": "Target",
                }},
            )

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_smb_file_share_kind_source_fails(self, resource_group):
        rg = resource_group.name
        sm_name = "testsm-smbfssrcfail"
        await self._create_storage_mover(rg, sm_name)

        with pytest.raises(HttpResponseError):
            await self.client.endpoints.create_or_update(
                resource_group_name=rg, storage_mover_name=sm_name, endpoint_name="smbfs-src-1",
                endpoint={"properties": {
                    "endpointType": "AzureStorageSmbFileShare",
                    "storageAccountResourceId": _account_id(rg),
                    "fileShareName": "testfileshare",
                    "endpointKind": "Source",
                }},
            )

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_nfs_file_share_kind_source_fails(self, resource_group):
        rg = resource_group.name
        sm_name = "testsm-nfsfssrcfail"
        await self._create_storage_mover(rg, sm_name)

        with pytest.raises(HttpResponseError):
            await self.client.endpoints.create_or_update(
                resource_group_name=rg, storage_mover_name=sm_name, endpoint_name="nfsfs-src-1",
                endpoint={"properties": {
                    "endpointType": "AzureStorageNfsFileShare",
                    "storageAccountResourceId": _account_id(rg),
                    "fileShareName": "testnfsfileshare",
                    "endpointKind": "Source",
                }},
            )

    # ----- EndpointTests.NfsFileShareEndpointCreateGetDeleteTest -----

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_nfs_file_share_create_get_delete(self, resource_group):
        rg = resource_group.name
        sm_name = "testsm-nfsfscrud"
        await self._create_storage_mover(rg, sm_name)

        endpoint_name = "nfsfs-1"
        endpoint = await self.client.endpoints.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=endpoint_name,
            endpoint={"properties": {
                "endpointType": "AzureStorageNfsFileShare",
                "storageAccountResourceId": _account_id(rg),
                "fileShareName": "testnfsfileshare",
                "description": "Test NFS file share endpoint",
            }},
        )
        assert endpoint.name == endpoint_name
        assert endpoint.properties.endpoint_type == "AzureStorageNfsFileShare"

        endpoint = await self.client.endpoints.get(
            resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=endpoint_name,
        )
        assert endpoint.properties.file_share_name == "testnfsfileshare"
        assert endpoint.properties.description == "Test NFS file share endpoint"

        await self._delete_endpoint(rg, sm_name, endpoint_name)
        with pytest.raises(ResourceNotFoundError):
            await self.client.endpoints.get(
                resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=endpoint_name,
            )
