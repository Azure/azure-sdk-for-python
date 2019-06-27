# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from datetime import datetime, timedelta

try:
    import tests.settings_real as settings
except ImportError:
    import tests.settings_fake as settings

from tests.testcase import (
    StorageTestCase,
    TestMode,
    record
)


class TestShareSamples(StorageTestCase):
    url = "{}://{}.file.core.windows.net".format(
        settings.PROTOCOL,
        settings.STORAGE_ACCOUNT_NAME
    )
    connection_string = settings.CONNECTION_STRING

    @record
    def test_create_share_snapshot(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.file import ShareClient
        share = ShareClient.from_connection_string(self.connection_string, "sharesnapshot")

        # Create the share
        share.create_share()

        try:
            # Create a snapshot of the share
            share.create_snapshot()
        finally:
            # Delete the share and its snapshot
            share.delete_share(delete_snapshots=True)

    @record
    def test_set_share_quota_and_metadata(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.file import ShareClient
        share = ShareClient.from_connection_string(self.connection_string, "fileshare")

        # Create the share
        share.create_share()

        try:
            # Set the quota for the share to 1GB
            share.set_share_quota(quota=1)

            # Set metadata for the share
            data = {'category': 'test'}
            share.set_share_metadata(metadata=data)

            # Get the metadata for the share
            props = share.get_share_properties().metadata
            assert props == data

        finally:
            # Delete the share
            share.delete_share()

    @record
    def test_list_directories_and_files(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.file import ShareClient
        share = ShareClient.from_connection_string(self.connection_string, "listshare")

        # Create the share
        share.create_share()

        try:
            # Create a directory in the share
            dir_client = share.create_directory("mydir")

            # Upload a file to the directory
            with open("./SampleSource.txt", "rb") as source_file:
                dir_client.upload_file(file_name="sample", data=source_file)

            # List files in the directory
            my_files = list(share.list_directories_and_files(directory_name="mydir"))
            print(my_files)

        finally:
            # Delete the share
            share.delete_share()

    @record
    def test_get_directory_or_file_client(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.file import ShareClient
        share = ShareClient.from_connection_string(self.connection_string, "testfiles")

        # Get the directory client to interact with a specific directory
        my_dir = share.get_directory_client("dir1")

        # Get the file client to interact with a specific file
        my_file = share.get_file_client("dir1/myfile")