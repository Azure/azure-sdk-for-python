# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os

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
DEST_FILE = 'SampleDestination.txt'


class TestFileSamples(FileTestCase):

    connection_string = settings.CONNECTION_STRING

    def setUp(self):
        data = b"Lorem ipsum dolor sit amet, consectetur adipiscing elit"
        with open(SOURCE_FILE, 'wb') as stream:
            stream.write(data)

        super(TestFileSamples, self).setUp()

    def tearDown(self):
        if os.path.isfile(SOURCE_FILE):
            try:
                os.remove(SOURCE_FILE)
            except:
                pass
        if os.path.isfile(DEST_FILE):
            try:
                os.remove(DEST_FILE)
            except:
                pass

        return super(TestFileSamples, self).tearDown()

    #--Begin File Samples-----------------------------------------------------------------

    @record
    def test_file_operations(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.file import ShareClient
        share = ShareClient.from_connection_string(self.connection_string, "filesshare")

        # Create the share
        share.create_share()

        try:
            # Get a file client
            file = share.get_file_client("myfile")
            file2 = share.get_file_client("myfile2")

            # [START create_file]
            # Create and allocate bytes for the file (no content added yet)
            file.create_file(size=100)
            # [END create_file]

            # Or upload a file directly
            # [START upload_file]
            with open(SOURCE_FILE, "rb") as source:
                file2.upload_file(source)
            # [END upload_file]

            # Download the file
            # [START download_file]
            with open(DEST_FILE, "wb") as data:
                data.writelines(file2.download_file())
            # [END download_file]

            # Delete the files
            file.delete_file()
            # [START delete_file]
            file2.delete_file()
            # [END delete_file]

        finally:
            # Delete the share
            share.delete_share()

    @record
    def test_copy_from_url(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.file import ShareClient
        share = ShareClient.from_connection_string(self.connection_string, "filesfromurl")

        # Create the share
        share.create_share()

        try:
            # Get a file client and upload a file
            source_file = share.get_file_client("sourcefile")
            with open(SOURCE_FILE, "rb") as source:
                source_file.upload_file(source)

            # Create another file client which will copy the file from url
            destination_file = share.get_file_client("destfile")

            # Build the url from which to copy the file
            source_url = "{}://{}.file.core.windows.net/{}/{}".format(
                settings.PROTOCOL,
                settings.STORAGE_ACCOUNT_NAME,
                "filesfromurl",
                "sourcefile"
            )

            # Copy the sample source file from the url to the destination file
            # [START copy_file_from_url]
            destination_file.start_copy_from_url(source_url=source_url)
            # [END copy_file_from_url]
        finally:
            # Delete the share
            share.delete_share()
