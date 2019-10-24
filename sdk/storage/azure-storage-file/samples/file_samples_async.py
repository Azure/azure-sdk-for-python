# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import sys
import asyncio

try:
    CONNECTION_STRING = os.environ['AZURE_STORAGE_CONNECTION_STRING']
except KeyError:
    print("AZURE_STORAGE_CONNECTION_STRING must be set.")
    print("AZURE_STORAGE_SHARED_ACCESS_KEY must be set.")
    sys.exit(1)

SOURCE_FILE = 'SampleSource.txt'
DEST_FILE = 'SampleDestination.txt'
data = b"Lorem ipsum dolor sit amet, consectetur adipiscing elit"
with open(SOURCE_FILE, 'wb') as stream:
    stream.write(data)


class FileSamples(object):

    async def simple_file_operations(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.file.aio import ShareClient
        share = ShareClient.from_connection_string(CONNECTION_STRING, "myshare")

        # Create the share
        await share.create_share()

        try:
            # Get a file client
            my_file = share.get_file_client("myfile")
            my_file2 = share.get_file_client("myfile2")

            # [START create_file]
            # Create and allocate bytes for the file (no content added yet)
            await my_file.create_file(size=100)
            # [END create_file]

            # Or upload a file directly
            # [START upload_file]
            with open(SOURCE_FILE, "rb") as source:
                await my_file2.upload_file(source)
            # [END upload_file]

            # Download the file
            # [START download_file]
            with open(DEST_FILE, "wb") as data:
                stream = await my_file2.download_file()
                data.write(await stream.readall())
            # [END download_file]

            # Delete the files
            # [START delete_file]
            await my_file.delete_file()
            # [END delete_file]
            await my_file2.delete_file()

        finally:
            # Delete the share
            await share.delete_share()

    async def file_copy_from_url(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.file.aio import ShareClient
        share = ShareClient.from_connection_string(CONNECTION_STRING, "myshare")

        # Create the share
        await share.create_share()

        try:
            # Get a file client and upload a file
            source_file = share.get_file_client("sourcefile")
            with open(SOURCE_FILE, "rb") as source:
                await source_file.upload_file(source)

            # Create another file client which will copy the file from url
            destination_file = share.get_file_client("destinationfile")

            # Build the url from which to copy the file
            source_url = "https://mystoragename.file.core.windows.net/myshare/sourcefile"

            # Copy the sample source file from the url to the destination file
            # [START copy_file_from_url]
            await destination_file.start_copy_from_url(source_url=source_url)
            # [END copy_file_from_url]
        finally:
            # Delete the share
            await share.delete_share()
