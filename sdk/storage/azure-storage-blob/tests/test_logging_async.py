# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import logging
import asyncio

import sys
from datetime import datetime, timedelta

from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy

from azure.storage.blob.aio import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
)

from azure.storage.blob import (
    ContainerPermissions,
    BlobPermissions,
)

from azure.storage.blob._shared.shared_access_signature import QueryStringConstants

from testcase import (
    StorageTestCase,
    TestMode,
    LogCaptured,
    record
)

if sys.version_info >= (3,):
    from urllib.parse import parse_qs, quote
else:
    from urlparse import parse_qs
    from urllib2 import quote

_AUTHORIZATION_HEADER_NAME = 'Authorization'


class AiohttpTestTransport(AioHttpTransport):
    """Workaround to vcrpy bug: https://github.com/kevin1024/vcrpy/pull/461
    """
    async def send(self, request, **config):
        response = await super(AiohttpTestTransport, self).send(request, **config)
        if not isinstance(response.headers, CIMultiDictProxy):
            response.headers = CIMultiDictProxy(CIMultiDict(response.internal_response.headers))
            response.content_type = response.headers.get("content-type")
        return response


class StorageLoggingTestAsync(StorageTestCase):

    def setUp(self):
        super(StorageLoggingTestAsync, self).setUp()

        url = self._get_account_url()
        credential = self._get_shared_key_credential()

        self.bsc = BlobServiceClient(url, credential=credential, transport=AiohttpTestTransport())
        self.container_name = self.get_resource_name('utcontainer')

    def tearDown(self):
        if not self.is_playback():
            loop = asyncio.get_event_loop()
            try:
                loop.run_until_complete(self.bsc.delete_container(self.container_name))
            except:
                pass

        return super(StorageLoggingTestAsync, self).tearDown()

    async def _setup(self):
        if not self.is_playback():
            try:
                # create source blob to be copied from
                self.source_blob_name = self.get_resource_name('srcblob')
                self.source_blob_data = self.get_random_bytes(4 * 1024)
                source_blob = self.bsc.get_blob_client(self.container_name, self.source_blob_name)

                await self.bsc.create_container(self.container_name)
                await source_blob.upload_blob(self.source_blob_data)

                # generate a SAS so that it is accessible with a URL
                sas_token = source_blob.generate_shared_access_signature(
                    permission=BlobPermissions.READ,
                    expiry=datetime.utcnow() + timedelta(hours=1),
                )
                sas_source = BlobClient(source_blob.url, credential=sas_token)
                self.source_blob_url = sas_source.url
            except:
                pass

    async def _test_authorization_is_scrubbed_off(self):
        await self._setup()
        # Arrange
        container = self.bsc.get_container_client(self.container_name)
        # Act
        with LogCaptured(self) as log_captured:
            await container.get_container_properties(logging_enable=True)
            log_as_str = log_captured.getvalue()
            # Assert
            # make sure authorization header is logged, but its value is not
            # the keyword SharedKey is present in the authorization header's value
            self.assertTrue(_AUTHORIZATION_HEADER_NAME in log_as_str)
            self.assertFalse('SharedKey' in log_as_str)

    @record
    def test_authorization_is_scrubbed_off(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_authorization_is_scrubbed_off())

    async def _test_sas_signature_is_scrubbed_off(self):
        # Test can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        await self._setup()
        # Arrange
        container = self.bsc.get_container_client(self.container_name)
        token = container.generate_shared_access_signature(
            permission=ContainerPermissions.READ,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        # parse out the signed signature
        token_components = parse_qs(token)
        signed_signature = quote(token_components[QueryStringConstants.SIGNED_SIGNATURE][0])

        sas_service = ContainerClient(container.url, credential=token)

        # Act
        with LogCaptured(self) as log_captured:
            await sas_service.get_account_information(logging_enable=True)
            log_as_str = log_captured.getvalue()

            # Assert
            # make sure the query parameter 'sig' is logged, but its value is not
            self.assertTrue(QueryStringConstants.SIGNED_SIGNATURE in log_as_str)
            self.assertFalse(signed_signature in log_as_str)

    @record
    def test_sas_signature_is_scrubbed_off(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_sas_signature_is_scrubbed_off())

    async def _test_copy_source_sas_is_scrubbed_off(self):
        # Test can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        await self._setup()
        # Arrange
        dest_blob_name = self.get_resource_name('destblob')
        dest_blob = self.bsc.get_blob_client(self.container_name, dest_blob_name)

        # parse out the signed signature
        token_components = parse_qs(self.source_blob_url)
        signed_signature = quote(token_components[QueryStringConstants.SIGNED_SIGNATURE][0])

        # Act
        with LogCaptured(self) as log_captured:
            await dest_blob.start_copy_from_url(
                self.source_blob_url, requires_sync=True, logging_enable=True)
            log_as_str = log_captured.getvalue()

            # Assert
            # make sure the query parameter 'sig' is logged, but its value is not
            self.assertTrue(QueryStringConstants.SIGNED_SIGNATURE in log_as_str)
            self.assertFalse(signed_signature in log_as_str)

            # make sure authorization header is logged, but its value is not
            # the keyword SharedKey is present in the authorization header's value
            self.assertTrue(_AUTHORIZATION_HEADER_NAME in log_as_str)
            self.assertFalse('SharedKey' in log_as_str)

    @record
    def test_copy_source_sas_is_scrubbed_off(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_copy_source_sas_is_scrubbed_off())
