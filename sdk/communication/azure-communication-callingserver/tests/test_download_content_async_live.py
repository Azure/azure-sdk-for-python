# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from azure.communication.callingserver.aio import CallingServerClient
from azure.communication.callingserver import CallingServerClient as CallingServerClientSync
from io import BytesIO
from _shared.testcase import (
    CommunicationTestCase
)
from _shared.asynctestcase import AsyncCommunicationTestCase
class TestDownloadAsyncLive(CommunicationTestCase):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    @AsyncCommunicationTestCase.await_prepared_test
    @pytest.mark.playback_test_only
    async def test_download_content_to_stream(self):
        metadata_url = "https://storage.asm.skype.com/v1/objects/0-wus-d4-6afafe78b9e313d77933b87578eabc9e/content/acsmetadata"
        connection_string = "endpoint=https://acstelephonyportaltesting.communication.azure.com/;accesskey=/cJGRzQtFVNneQVqbUlRvsvOLwEgQwsWDQxjLnWPWcTSg3RwAfnYY4v9Ce/mN4iAZ50znB8B0UMmQ/cDHLnEtw=="

        calling_server_client = CallingServerClient.from_connection_string(connection_string)
        downloader = await calling_server_client.download(metadata_url)
        stream = BytesIO()
        await downloader.readinto(stream)
        metadata = stream.getvalue()

        self.assertIsNotNone(metadata)
        self.assertTrue(metadata.__contains__(b"0-wus-d4-6afafe78b9e313d77933b87578eabc9e"))

    @AsyncCommunicationTestCase.await_prepared_test
    @pytest.mark.playback_test_only
    async def test_download_content_to_stream_on_chunks(self):
        metadata_url = "https://storage.asm.skype.com/v1/objects/0-wus-d4-6afafe78b9e313d77933b87578eabc9e/content/acsmetadata"
        connection_string = "endpoint=https://acstelephonyportaltesting.communication.azure.com/;accesskey=/cJGRzQtFVNneQVqbUlRvsvOLwEgQwsWDQxjLnWPWcTSg3RwAfnYY4v9Ce/mN4iAZ50znB8B0UMmQ/cDHLnEtw=="

        calling_server_client = CallingServerClient.from_connection_string(connection_string)
        downloader = await calling_server_client.download(metadata_url, block_size=400)
        stream = BytesIO()
        await downloader.readinto(stream)
        metadata = stream.getvalue()
        self.assertIsNotNone(metadata)
        self.assertTrue(metadata.__contains__(b"0-wus-d4-6afafe78b9e313d77933b87578eabc9e"))

    @AsyncCommunicationTestCase.await_prepared_test
    @pytest.mark.playback_test_only
    async def test_download_content_to_stream_on_chunks_parallel(self):
        metadata_url = "https://storage.asm.skype.com/v1/objects/0-wus-d4-6afafe78b9e313d77933b87578eabc9e/content/acsmetadata"
        connection_string = "endpoint=https://acstelephonyportaltesting.communication.azure.com/;accesskey=/cJGRzQtFVNneQVqbUlRvsvOLwEgQwsWDQxjLnWPWcTSg3RwAfnYY4v9Ce/mN4iAZ50znB8B0UMmQ/cDHLnEtw=="

        calling_server_client = CallingServerClient.from_connection_string(connection_string)
        downloader = await calling_server_client.download(metadata_url, max_concurrency=3, block_size=100)
        stream = BytesIO()
        await downloader.readinto(stream)
        metadata = stream.getvalue()
        self.assertIsNotNone(metadata)
        self.assertTrue(metadata.__contains__(b"0-wus-d4-6afafe78b9e313d77933b87578eabc9e"))

    @AsyncCommunicationTestCase.await_prepared_test
    @pytest.mark.playback_test_only
    async def test_download_content_to_stream_with_redirection(self):
        metadata_url = "https://storage.asm.skype.com/v1/objects/0-weu-d18-f71ce6295ef910657759449422ebb5f4/content/acsmetadata"
        connection_string = "endpoint=https://acs-recording-runner-africa.communication.azure.com/;accesskey=2bgBt+moI0R9h0Gfpxt+xR19yBwHdaKsI7cc5Ac9rbBHq1gNuPIOWJzkWdMvO3w5Lx3hcVuZLTqyqGP/B3W/QQ=="

        calling_server_client = CallingServerClient.from_connection_string(connection_string)
        downloader = await calling_server_client.download(metadata_url)
        stream = BytesIO()
        await downloader.readinto(stream)
        metadata = stream.getvalue()
        self.assertIsNotNone(metadata)
        self.assertTrue(metadata.__contains__(b"0-weu-d18-f71ce6295ef910657759449422ebb5f4"))
        
