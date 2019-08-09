# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import asyncio
try:
    import settings_real as settings
except ImportError:
    import file_settings_fake as settings

from filetestcase import (
    FileTestCase,
    TestMode,
    record
)

SOURCE_FILE = 'SampleSource.txt'


class TestHelloWorldSamples(FileTestCase):

    connection_string = settings.CONNECTION_STRING

    def setUp(self):
        data = b"Lorem ipsum dolor sit amet, consectetur adipiscing elit"
        with open(SOURCE_FILE, 'wb') as stream:
            stream.write(data)

        super(TestHelloWorldSamples, self).setUp()

    def tearDown(self):
        if os.path.isfile(SOURCE_FILE):
            try:
                os.remove(SOURCE_FILE)
            except:
                pass

        return super(TestHelloWorldSamples, self).tearDown()

    #--Begin File Samples-----------------------------------------------------------------

    async def _test_create_client_with_connection_string(self):
        # Instantiate the FileServiceClient from a connection string
        from azure.storage.file.aio import FileServiceClient
        file_service = FileServiceClient.from_connection_string(self.connection_string)

        # Get queue service properties
        properties = await file_service.get_service_properties()
        assert properties is not None

    def test_create_client_with_connection_string(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_client_with_connection_string())

    async def _test_create_file_share(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.file.aio import ShareClient
        share = ShareClient.from_connection_string(self.connection_string, share="myshare")

        # Create the share
        await share.create_share()

        try:
            # [START get_share_properties]
            properties = await share.get_share_properties()
            # [END get_share_properties]
            assert properties is not None

        finally:
            # Delete the share
            await share.delete_share()

    def test_create_file_share(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_file_share())

    async def _test_upload_file_to_share(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.file.aio import ShareClient
        share = ShareClient.from_connection_string(self.connection_string, share="share")

        # Create the share
        await share.create_share()

        try:
            # Instantiate the FileClient from a connection string
            # [START create_file_client]
            from azure.storage.file.aio import FileClient
            file = FileClient.from_connection_string(self.connection_string, share="share", file_path="myfile")
            # [END create_file_client]

            # Upload a file
            with open(SOURCE_FILE, "rb") as source_file:
                await file.upload_file(source_file)

        finally:
            # Delete the share
            await share.delete_share()

    def test_upload_file_to_share(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_upload_file_to_share())
