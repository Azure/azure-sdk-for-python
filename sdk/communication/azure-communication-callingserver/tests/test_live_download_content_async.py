# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
'''
    Adding testing for the download recording async use cases.
'''
from io import BytesIO
import pytest
import utils._test_constants as CONST
from _shared.asynctestcase  import AsyncCommunicationTestCase

from azure.communication.callingserver.aio import CallingServerClient
from azure.communication.callingserver._models import ParallelDownloadOptions

class ContentDownloadTestsAsync(AsyncCommunicationTestCase):

    def setUp(self):
        super(ContentDownloadTestsAsync, self).setUp()
        self._document_id = "0-wus-d4-6afafe78b9e313d77933b87578eabc9e"
        self._metadata_url = \
            'https://storagehost.com/v1/objects/{}/content/acsmetadata'.format(self._document_id)
        self._calling_server_client = \
            CallingServerClient.from_connection_string(self.connection_str)

    @pytest.mark.skipif(CONST.SKIP_CALLINGSERVER_INTERACTION_LIVE_TESTS, reason=CONST.CALLINGSERVER_INTERACTION_LIVE_TESTS_SKIP_REASON)
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_download_content_to_stream(self):
        downloader = await self._calling_server_client.download(self._metadata_url)
        stream = await self._downloadToStream(downloader)
        metadata = stream.getvalue()
        self._verify_metadata(metadata)

    @pytest.mark.skipif(CONST.SKIP_CALLINGSERVER_INTERACTION_LIVE_TESTS, reason=CONST.CALLINGSERVER_INTERACTION_LIVE_TESTS_SKIP_REASON)
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_download_content_to_stream_on_chunks(self):
        downloader = await self._calling_server_client.download(
            self._metadata_url,
            block_size=400
        )
        stream = await self._downloadToStream(downloader)
        metadata = stream.getvalue()
        self._verify_metadata(metadata)

    @pytest.mark.skipif(CONST.SKIP_CALLINGSERVER_INTERACTION_LIVE_TESTS, reason=CONST.CALLINGSERVER_INTERACTION_LIVE_TESTS_SKIP_REASON)
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_download_content_to_stream_on_chunks_parallel(self):
        downloader = await self._calling_server_client.download(
            self._metadata_url,
            max_concurrency=3,
            block_size=100
        )
        stream = await self._downloadToStream(downloader)
        metadata = stream.getvalue()
        self._verify_metadata(metadata)

    @pytest.mark.skipif(CONST.SKIP_CALLINGSERVER_INTERACTION_LIVE_TESTS, reason=CONST.CALLINGSERVER_INTERACTION_LIVE_TESTS_SKIP_REASON)
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_download_content_to_stream_with_redirection(self):
        downloader = await self._calling_server_client.download(self._metadata_url)
        stream = await self._downloadToStream(downloader)
        metadata = stream.getvalue()
        self._verify_metadata(metadata)

    async def _downloadToStream(self, downloader):
        stream = BytesIO()
        await downloader.readinto(stream)
        return stream

    def _verify_metadata(self, metadata):
        self.assertIsNotNone(metadata)
        print(metadata)
        self.assertTrue(metadata.__contains__(bytes(self._document_id, 'utf-8')))
