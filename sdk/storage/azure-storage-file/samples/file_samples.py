# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import sys

try:
    CONNECTION_STRING = os.environ['AZURE_STORAGE_CONNECTION_STRING']
except KeyError:
    print("AZURE_STORAGE_CONNECTION_STRING must be set.")
    sys.exit(1)

SOURCE_FILE = 'SampleSource.txt'
DEST_FILE = 'SampleDestination.txt'
data = b"Lorem ipsum dolor sit amet, consectetur adipiscing elit"
with open(SOURCE_FILE, 'wb') as stream:
    stream.write(data)


class FileSamples(object):

    def simple_file_operations(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.file import ShareClient
        share = ShareClient.from_connection_string(CONNECTION_STRING, "myshare")

        # Create the share
        share.create_share()

        try:
            # Get a file client
            my_file = share.get_file_client("myfile")
            my_file2 = share.get_file_client("myfile2")

            # [START create_file]
            # Create and allocate bytes for the file (no content added yet)
            my_file.create_file(size=200)
            # [END create_file]

            # Or upload a file directly
            # [START upload_file]
            with open(SOURCE_FILE, "rb") as source:
                my_file2.upload_file(source)
            # [END upload_file]

            # Download the file
            # [START download_file]
            with open(DEST_FILE, "wb") as data:
                stream = my_file2.download_file()
                data.write(stream.readall())
            # [END download_file]

            # Delete the files
            # [START delete_file]
            my_file.delete_file()
            # [END delete_file]
            my_file2.delete_file()

        finally:
            # Delete the share
            share.delete_share()

    def copy_file_from_url(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.file import ShareClient
        share = ShareClient.from_connection_string(CONNECTION_STRING, "myshare")

        # Create the share
        share.create_share()

        try:
            # Get a file client and upload a file
            source_file = share.get_file_client("sourcefile")
            with open(SOURCE_FILE, "rb") as source:
                source_file.upload_file(source)

            # Create another file client which will copy the file from url
            destination_file = share.get_file_client("destinationfile")

            # Build the url from which to copy the file
            source_url = "https://mystoragename.file.core.windows.net/myshare/sourcefile"

            # Copy the sample source file from the url to the destination file
            # [START copy_file_from_url]
            destination_file.start_copy_from_url(source_url=source_url)
            # [END copy_file_from_url]
        finally:
            # Delete the share
            share.delete_share()
