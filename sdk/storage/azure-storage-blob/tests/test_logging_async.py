# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import sys
from datetime import datetime, timedelta

import pytest
from azure.storage.blob import BlobSasPermissions, ContainerSasPermissions, generate_blob_sas, generate_container_sas
from azure.storage.blob.aio import BlobClient, BlobServiceClient, ContainerClient
from azure.storage.blob._shared.shared_access_signature import QueryStringConstants

from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage import LogCaptured
from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase
from settings.testcase import BlobPreparer

if sys.version_info >= (3,):
    from urllib.parse import parse_qs, quote, urlparse
else:
    from urlparse import parse_qs, urlparse
    from urllib2 import quote

_AUTHORIZATION_HEADER_NAME = 'Authorization'


class TestStorageLoggingAsync(AsyncStorageRecordedTestCase):
    async def _setup(self, bsc):
        self.container_name = self.get_resource_name('utcontainer')

        # create source blob to be copied from
        self.source_blob_name = self.get_resource_name('srcblob')
        self.source_blob_data = self.get_random_bytes(4 * 1024)
        source_blob = bsc.get_blob_client(self.container_name, self.source_blob_name)

        if self.is_live:
            try:
                await bsc.create_container(self.container_name)
            except:
                pass
            await source_blob.upload_blob(self.source_blob_data, overwrite=True)

        # generate a SAS so that it is accessible with a URL
        sas_token = self.generate_sas(
            generate_blob_sas,
            source_blob.account_name,
            source_blob.container_name,
            source_blob.blob_name,
            snapshot=source_blob.snapshot,
            account_key=source_blob.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        sas_source = BlobClient.from_blob_url(source_blob.url, credential=sas_token)
        self.source_blob_url = sas_source.url

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_logging_request_and_response_body(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, logging_enable=True)
        await self._setup(bsc)
        # Arrange
        container = bsc.get_container_client(self.container_name)
        request_body = 'testloggingbody'
        blob_name = self.get_resource_name("testloggingblob")
        blob_client = container.get_blob_client(blob_name)
        await blob_client.upload_blob(request_body, overwrite=True)
        # Act
        with LogCaptured(self) as log_captured:
            await blob_client.download_blob()
            log_as_str = log_captured.getvalue()
            assert not request_body in log_as_str

        with LogCaptured(self) as log_captured:
            await blob_client.upload_blob(request_body, overwrite=True, logging_body=True)
            log_as_str = log_captured.getvalue()
            assert request_body in log_as_str
            assert log_as_str.count(request_body) == 1
            
    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_authorization_is_scrubbed_off(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key)
        await self._setup(bsc)
        # Arrange
        container = bsc.get_container_client(self.container_name)
        # Act
        with LogCaptured(self) as log_captured:
            await container.get_container_properties(logging_enable=True)
            log_as_str = log_captured.getvalue()
            # Assert
            # make sure authorization header is logged, but its value is not
            # the keyword SharedKey is present in the authorization header's value
            assert _AUTHORIZATION_HEADER_NAME in log_as_str
            assert not 'SharedKey' in log_as_str

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_sas_signature_is_scrubbed_off(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Test can only run live

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key)
        await self._setup(bsc)
        # Arrange
        container = bsc.get_container_client(self.container_name)
        token = self.generate_sas(
            generate_container_sas,
            container.account_name,
            container.container_name,
            account_key=container.credential.account_key,
            permission=ContainerSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        # parse out the signed signature
        token_components = parse_qs(token)
        signed_signature = quote(token_components[QueryStringConstants.SIGNED_SIGNATURE][0])

        sas_service = ContainerClient.from_container_url(container.url, credential=token)

        # Act
        with LogCaptured(self) as log_captured:
            await sas_service.get_account_information(logging_enable=True)
            log_as_str = log_captured.getvalue()

            # Assert
            # make sure the query parameter 'sig' is logged, but its value is not
            assert QueryStringConstants.SIGNED_SIGNATURE in log_as_str
            assert not signed_signature in log_as_str

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_copy_source_sas_is_scrubbed_off(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Test can only run live
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key)
        await self._setup(bsc)
        # Arrange
        dest_blob_name = self.get_resource_name('destblob')
        dest_blob = bsc.get_blob_client(self.container_name, dest_blob_name)

        # parse out the signed signature
        query_parameters = urlparse(self.source_blob_url).query
        token_components = parse_qs(query_parameters)
        if QueryStringConstants.SIGNED_SIGNATURE not in token_components:
            pytest.fail("Blob URL {} doesn't contain {}, parsed query params: {}".format(
                self.source_blob_url,
                QueryStringConstants.SIGNED_SIGNATURE,
                list(token_components.keys())
            ))
        signed_signature = quote(token_components[QueryStringConstants.SIGNED_SIGNATURE][0])

        # Act
        with LogCaptured(self) as log_captured:
            await dest_blob.start_copy_from_url(
                self.source_blob_url, requires_sync=True, logging_enable=True)
            log_as_str = log_captured.getvalue()

            # Assert
            # make sure the query parameter 'sig' is logged, but its value is not
            assert QueryStringConstants.SIGNED_SIGNATURE in log_as_str
            assert not signed_signature in log_as_str

            # make sure authorization header is logged, but its value is not
            # the keyword SharedKey is present in the authorization header's value
            assert _AUTHORIZATION_HEADER_NAME in log_as_str
            assert not 'SharedKey' in log_as_str
