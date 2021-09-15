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
        
