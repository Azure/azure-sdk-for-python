# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os

from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer, FakeStorageAccount

from filetestcase import (
    FileTestCase
)

SOURCE_FILE = 'SampleSource.txt'
FAKE_STORAGE = FakeStorageAccount(
    name='pyacrstorage',
    id='')

class TestShareSamples(FileTestCase):
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

    @ResourceGroupPreparer()               
    @StorageAccountPreparer(name_prefix='pyacrstorage', playback_fake_resource=FAKE_STORAGE)
    def test_create_share_snapshot(self, resource_group, location, storage_account, storage_account_key):
        # Instantiate the ShareClient from a connection string
        from azure.storage.file import ShareClient
        share = ShareClient.from_connection_string(self.connection_string(storage_account, storage_account_key), "sharesnapshot")

        # [START create_share]
        share.create_share()
        # [END create_share]
        try:
            # [START create_share_snapshot]
            share.create_snapshot()
            # [END create_share_snapshot]
        finally:
            # [START delete_share]
            share.delete_share(delete_snapshots=True)
            # [END delete_share]

    @ResourceGroupPreparer()               
    @StorageAccountPreparer(name_prefix='pyacrstorage', playback_fake_resource=FAKE_STORAGE)
    def test_set_share_quota_and_metadata(self, resource_group, location, storage_account, storage_account_key):
        # [START create_share_client_from_conn_string]
        from azure.storage.file import ShareClient
        share = ShareClient.from_connection_string(self.connection_string(storage_account, storage_account_key), "fileshare")
        # [END create_share_client_from_conn_string]

        # Create the share
        share.create_share()

        try:
            # [START set_share_quota]
            # Set the quota for the share to 1GB
            share.set_share_quota(quota=1)
            # [END set_share_quota]

            # [START set_share_metadata]
            data = {'category': 'test'}
            share.set_share_metadata(metadata=data)
            # [END set_share_metadata]

            # Get the metadata for the share
            props = share.get_share_properties().metadata
            assert props == data

        finally:
            # Delete the share
            share.delete_share()

    @ResourceGroupPreparer()               
    @StorageAccountPreparer(name_prefix='pyacrstorage', playback_fake_resource=FAKE_STORAGE)
    def test_list_directories_and_files(self, resource_group, location, storage_account, storage_account_key):
        # Instantiate the ShareClient from a connection string
        from azure.storage.file import ShareClient
        share = ShareClient.from_connection_string(self.connection_string(storage_account, storage_account_key), "listshare")

        # Create the share
        share.create_share()

        try:
            # [START share_list_files_in_dir]
            # Create a directory in the share
            dir_client = share.create_directory("mydir")

            # Upload a file to the directory
            with open(SOURCE_FILE, "rb") as source_file:
                dir_client.upload_file(file_name="sample", data=source_file)

            # List files in the directory
            my_files = list(share.list_directories_and_files(directory_name="mydir"))
            print(my_files)
            # [END share_list_files_in_dir]
        finally:
            # Delete the share
            share.delete_share()

    @ResourceGroupPreparer()               
    @StorageAccountPreparer(name_prefix='pyacrstorage', playback_fake_resource=FAKE_STORAGE)
    def test_get_directory_or_file_client(self, resource_group, location, storage_account, storage_account_key):
        # Instantiate the ShareClient from a connection string
        from azure.storage.file import ShareClient
        share = ShareClient.from_connection_string(self.connection_string(storage_account, storage_account_key), "testfiles")

        # Get the directory client to interact with a specific directory
        my_dir = share.get_directory_client("dir1")

        # Get the file client to interact with a specific file
        my_file = share.get_file_client("dir1/myfile")