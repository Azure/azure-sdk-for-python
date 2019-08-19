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


class TestShareSamples(FileTestCase):
    url = "{}://{}.file.core.windows.net".format(
        settings.PROTOCOL,
        settings.STORAGE_ACCOUNT_NAME
    )
    connection_string = settings.CONNECTION_STRING

    def setUp(self):
        data = b"Lorem ipsum dolor sit amet, consectetur adipiscing elit"
        with open(SOURCE_FILE, 'wb') as stream:
            stream.write(data)

        super(TestShareSamples, self).setUp()

    def tearDown(self):
        if os.path.isfile(SOURCE_FILE):
            try:
                os.remove(SOURCE_FILE)
            except:
                pass

        return super(TestShareSamples, self).tearDown()

    #--Begin File Samples-----------------------------------------------------------------

    async def _test_create_share_snapshot(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.file.aio import ShareClient
        share = ShareClient.from_connection_string(self.connection_string, "sharesnapshot")

        # [START create_share]
        await share.create_share()
        # [END create_share]
        try:
            # [START create_share_snapshot]
            await share.create_snapshot()
            # [END create_share_snapshot]
        finally:
            # [START delete_share]
            await share.delete_share(delete_snapshots=True)
            # [END delete_share]

    def test_create_share_snapshot(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_share_snapshot())

    async def _test_set_share_quota_and_metadata(self):
        # [START create_share_client_from_conn_string]
        from azure.storage.file.aio import ShareClient
        share = ShareClient.from_connection_string(self.connection_string, "fileshare")
        # [END create_share_client_from_conn_string]

        # Create the share
        await share.create_share()

        try:
            # [START set_share_quota]
            # Set the quota for the share to 1GB
            await share.set_share_quota(quota=1)
            # [END set_share_quota]

            # [START set_share_metadata]
            data = {'category': 'test'}
            await share.set_share_metadata(metadata=data)
            # [END set_share_metadata]

            # Get the metadata for the share
            props = await share.get_share_properties().metadata
            assert props == data

        finally:
            # Delete the share
            await share.delete_share()

    def test_set_share_quota_and_metadata(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_share_quota_and_metadata())

    async def _test_list_directories_and_files(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.file.aio import ShareClient
        share = ShareClient.from_connection_string(self.connection_string, "listshare")

        # Create the share
        await share.create_share()

        try:
            # [START share_list_files_in_dir]
            # Create a directory in the share
            dir_client = await share.create_directory("mydir")

            # Upload a file to the directory
            with open(SOURCE_FILE, "rb") as source_file:
                await dir_client.upload_file(file_name="sample", data=source_file)

            # List files in the directory
            my_files = []
            async for item in share.list_directories_and_files(directory_name="mydir"):
                my_files.append(item)
            print(my_files)
            # [END share_list_files_in_dir]
        finally:
            # Delete the share
            await share.delete_share()

    def test_list_directories_and_files(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_list_directories_and_files())

    async def _test_get_directory_or_file_client(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.file.aio import ShareClient
        share = ShareClient.from_connection_string(self.connection_string, "testfiles")

        # Get the directory client to interact with a specific directory
        my_dir = share.get_directory_client("dir1")

        # Get the file client to interact with a specific file
        my_file = share.get_file_client("dir1/myfile")

    def test_get_directory_or_file_client(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_directory_or_file_client())
