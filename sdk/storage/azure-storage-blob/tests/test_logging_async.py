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

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key.secret, logging_enable=True)
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

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key.secret)
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

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key.secret)
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
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key.secret)
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

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_logging_body_option_overrides_constructor(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange - Create client with logging_body=True in constructor
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            storage_account_key.secret,
            logging_enable=True,
            logging_body=True
        )
        container_name = self.get_resource_name('utcontainer')
        container = bsc.get_container_client(container_name)
        if self.is_live:
            try:
                await container.create_container()
            except:
                pass
        
        request_body = 'testoverridelogging'
        blob_name = self.get_resource_name("testoverride")
        blob_client = container.get_blob_client(blob_name)
        await blob_client.upload_blob(request_body, overwrite=True)

        # Act - Download without logging_body option (should use constructor default=True)
        with LogCaptured(self) as log_captured:
            await blob_client.download_blob()
            log_as_str = log_captured.getvalue()
            # Assert - In async, response body shows "Body is streamable" instead of actual content
            assert "Body is streamable" in log_as_str

        # Act - Download with logging_body=False (should override constructor)
        with LogCaptured(self) as log_captured:
            await blob_client.download_blob(logging_body=False)
            log_as_str = log_captured.getvalue()
            # Assert - Body should NOT be logged, overriding constructor setting
            assert "Body is streamable" not in log_as_str

        # Act - Upload with logging_body=False (test request logging override)
        with LogCaptured(self) as log_captured:
            await blob_client.upload_blob('uploadtest', overwrite=True, logging_body=False)
            log_as_str = log_captured.getvalue()
            # Assert - Request body should NOT be logged
            assert 'uploadtest' not in log_as_str

        # Act - Upload/Download with logging_enable=False (should override constructor and disable logging entirely)
        with LogCaptured(self) as log_captured:
            await blob_client.upload_blob('uploadtest', overwrite=True, logging_enable=False)
            await blob_client.download_blob(logging_enable=False)
            log_as_str = log_captured.getvalue()
            # Assert - No logging should occur
            assert log_as_str == ''

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_logging_body_isolation_between_requests(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange - Create client with logging_body=True in constructor
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            storage_account_key.secret,
            logging_enable=True,
            logging_body=True
        )
        container_name = self.get_resource_name('utcontainer')
        container = bsc.get_container_client(container_name)
        if self.is_live:
            try:
                await container.create_container()
            except:
                pass
        
        request_body_1 = 'isolationtest1'
        request_body_2 = 'isolationtest2'
        blob_name_1 = self.get_resource_name("testblob1")
        blob_name_2 = self.get_resource_name("testblob2")
        blob_client_1 = container.get_blob_client(blob_name_1)
        blob_client_2 = container.get_blob_client(blob_name_2)
        await blob_client_1.upload_blob(request_body_1, overwrite=True)
        await blob_client_2.upload_blob(request_body_2, overwrite=True)

        # Act - First request with logging_body=False
        with LogCaptured(self) as log_captured:
            await blob_client_1.download_blob(logging_body=False)
            log_as_str = log_captured.getvalue()
            # Assert - Body should NOT be logged
            assert "Body is streamable" not in log_as_str

        # Act - Second request without logging_body option (should revert to constructor default=True)
        with LogCaptured(self) as log_captured:
            await blob_client_2.download_blob()
            log_as_str = log_captured.getvalue()
            # Assert - Body SHOULD be logged, proving previous request's False didn't persist
            assert "Body is streamable" in log_as_str

        # Act - Third request with logging_body=True
        with LogCaptured(self) as log_captured:
            await blob_client_1.download_blob(logging_body=True)
            log_as_str = log_captured.getvalue()
            # Assert - Body should be logged
            assert "Body is streamable" in log_as_str

        # Act - Fourth request without logging_body option (should still use constructor default=True)
        with LogCaptured(self) as log_captured:
            await blob_client_2.download_blob()
            log_as_str = log_captured.getvalue()
            # Assert - Body SHOULD be logged, proving previous request's True didn't change the default
            assert "Body is streamable" in log_as_str

        # Act - Create new client with logging_body=False and verify isolation works in reverse
        bsc_no_body = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            storage_account_key.secret,
            logging_enable=True,
            logging_body=False
        )
        container_no_body = bsc_no_body.get_container_client(container_name)
        blob_client_no_body = container_no_body.get_blob_client(blob_name_1)

        # Act - Request with logging_body=True
        with LogCaptured(self) as log_captured:
            await blob_client_no_body.download_blob(logging_body=True)
            log_as_str = log_captured.getvalue()
            # Assert - Body should be logged
            assert "Body is streamable" in log_as_str

        # Act - Next request without logging_body option (should revert to constructor default=False)
        with LogCaptured(self) as log_captured:
            await blob_client_no_body.download_blob()
            log_as_str = log_captured.getvalue()
            # Assert - Body should NOT be logged, proving previous True didn't persist
            assert "Body is streamable" not in log_as_str

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_logging_body_option_on_retry(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange - Create client with logging enabled and retry configured
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            storage_account_key.secret,
            logging_enable=True,
            retry_total=1,
            initial_backoff=0.1,
            increment_base=0.1,
        )
        container_name = self.get_resource_name('utcontainer')
        container = bsc.get_container_client(container_name)
        if self.is_live:
            try:
                await container.create_container()
            except:
                pass
        
        request_body = 'testretrylogging'
        blob_name = self.get_resource_name("testretry")
        blob_client = container.get_blob_client(blob_name)
        await blob_client.upload_blob(request_body, overwrite=True)

        # Test 1: logging_body=False should prevent logging on both original and retry attempts
        call_count = 0
        def response_hook_fail_once(response):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                response.http_response.status_code = 408  # Request Timeout - triggers retry
        
        with LogCaptured(self) as log_captured:
            call_count = 0
            await blob_client.download_blob(raw_response_hook=response_hook_fail_once, logging_body=False)
            log_as_str = log_captured.getvalue()
            # Assert - Body should NOT be logged on either attempt
            assert "Body is streamable" not in log_as_str
            assert call_count == 2  # Verify retry happened

        # Test 2: logging_body=True should log on both original and retry attempts
        with LogCaptured(self) as log_captured:
            call_count = 0
            await blob_client.download_blob(raw_response_hook=response_hook_fail_once, logging_body=True)
            log_as_str = log_captured.getvalue()
            # Assert - Body should be logged on both attempts (async shows "Body is streamable")
            assert "Body is streamable" in log_as_str
            assert log_as_str.count("Body is streamable") == 2  # Should appear twice (original + retry)
            assert call_count == 2  # Verify retry happened

        # Test 3: Verify that logging_body override persists correctly across retries
        # even when constructor has logging_body=True
        bsc_with_body = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            storage_account_key.secret,
            logging_enable=True,
            logging_body=True,
            retry_total=1,
            initial_backoff=0.1,
            increment_base=0.1,
        )
        container_with_body = bsc_with_body.get_container_client(container_name)
        blob_client_with_body = container_with_body.get_blob_client(blob_name)

        with LogCaptured(self) as log_captured:
            call_count = 0
            await blob_client_with_body.download_blob(raw_response_hook=response_hook_fail_once, logging_body=False)
            log_as_str = log_captured.getvalue()
            # Assert - logging_body=False should override constructor setting on both attempts
            assert "Body is streamable" not in log_as_str
            assert call_count == 2  # Verify retry happened
