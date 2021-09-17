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

from _shared.asynctestcase import AsyncCommunicationTestCase

from azure.communication.callingserver.aio import CallingServerClient

class TestDownloadAsyncLive(AsyncCommunicationTestCase):
    '''
    Download async testing class.
    '''

    def __init__(self, method_name, *args, **kwargs):
        super().__init__(method_name, *args, **kwargs)
        self._metadata_url = \
            "https://storage.asm.skype.com/v1/objects/" + \
                "0-wus-d4-6afafe78b9e313d77933b87578eabc9e/content/acsmetadata"
        self._connection_string = \
            "endpoint=https://acstelephonyportaltesting.communication.azure.com/;" + \
                "accesskey=/cJGRzQtFVNneQVqbUlRvsvOLwEgQwsWDQxjLnWPWcTSg3RwAfnYY4v9Ce/" + \
                    "mN4iAZ50znB8B0UMmQ/cDHLnEtw=="
        self._calling_server_client = \
            CallingServerClient.from_connection_string(self._connection_string)

    @pytest.mark.playback_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    #pylint: disable=missing-function-docstring
    async def test_download_content_to_stream(self):
        stream = await self._execute_test()
        metadata = stream.getvalue()
        self._verify_metadata(metadata)

    @AsyncCommunicationTestCase.await_prepared_test
    @pytest.mark.playback_test_only
    #pylint: disable=missing-function-docstring
    async def test_download_content_to_stream_on_chunks(self):
        stream = await self._execute_test(block_size=400)
        metadata = stream.getvalue()
        self._verify_metadata(metadata)

    @AsyncCommunicationTestCase.await_prepared_test
    @pytest.mark.playback_test_only
    #pylint: disable=missing-function-docstring
    async def test_download_content_to_stream_on_chunks_parallel(self):
        stream = await self._execute_test(
            max_concurrency=3,
            block_size=100)
        metadata = stream.getvalue()
        self._verify_metadata(metadata)

    @AsyncCommunicationTestCase.await_prepared_test
    @pytest.mark.playback_test_only
    #pylint: disable=missing-function-docstring
    async def test_download_content_to_stream_with_redirection(self):
        metadata_url = \
            "https://storage.asm.skype.com/v1/objects/" + \
                "0-weu-d18-f71ce6295ef910657759449422ebb5f4/content/acsmetadata"
        connection_string = \
            "endpoint=https://acs-recording-runner-africa.communication.azure.com/;" + \
                "accesskey=2bgBt+moI0R9h0Gfpxt+xR19yBwHdaKsI7cc5Ac9rbBHq1gNuPIOWJzkW" + \
                    "dMvO3w5Lx3hcVuZLTqyqGP/B3W/QQ=="

        calling_server_client = CallingServerClient.from_connection_string(connection_string)
        downloader = await calling_server_client.download(metadata_url)
        stream = BytesIO()
        await downloader.readinto(stream)
        metadata = stream.getvalue()
        self.assertIsNotNone(metadata)
        self.assertTrue(metadata.__contains__(b"0-weu-d18-f71ce6295ef910657759449422ebb5f4"))

    async def _execute_test(self, **download_options):
        downloader = await self._calling_server_client.download(self._metadata_url,
            **download_options)
        stream = BytesIO()
        await downloader.readinto(stream)
        return stream

    def _verify_metadata(self, metadata):
        self.assertIsNotNone(metadata)
        self.assertTrue(metadata.__contains__(b"0-wus-d4-6afafe78b9e313d77933b87578eabc9e"))
