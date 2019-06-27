# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

try:
    import tests.settings_real as settings
except ImportError:
    import tests.settings_fake as settings

from tests.testcase import (
    StorageTestCase,
    TestMode,
    record
)


class TestFileSamples(StorageTestCase):

    connection_string = settings.CONNECTION_STRING

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

            # Create and allocate bytes for the file (no content added yet)
            file.create_file(size=100)

            # Or upload a file directly
            with open("./SampleSource.txt", "rb") as source:
                file2.upload_file(source)

            # Download the file
            with open("./SampleDestination.txt", "wb") as data:
                data.writelines(file2.download_file())

            # Delete the files
            file.delete_file()
            file2.delete_file()

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
            with open("./SampleSource.txt", "rb") as source:
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
            destination_file.copy_file_from_url(source_url=source_url)

        finally:
            # Delete the share
            share.delete_share()
