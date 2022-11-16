# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: file_samples_client_async.py

DESCRIPTION:
    These samples demonstrate simple async file operations like creating a share or file,
    uploading and downloading to a file, and copying a file from a URL.

USAGE:
    python file_samples_client_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
    2) AZURE_STORAGE_ACCOUNT_NAME - the name of the storage account
"""


import os
import asyncio


SOURCE_FILE = './SampleSource.txt'
DEST_FILE = './SampleDestination.txt'


class FileSamplesAsync(object):

    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")

    async def simple_file_operations_async(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.fileshare.aio import ShareClient
        share = ShareClient.from_connection_string(self.connection_string, "filesamples1")

        # Create the share
        async with share:
            await share.create_share()

            try:
                # Get a file client
                my_allocated_file = share.get_file_client("my_allocated_file")
                my_file = share.get_file_client("my_file")

                # [START create_file]
                # Create and allocate bytes for the file (no content added yet)
                await my_allocated_file.create_file(size=100)
                # [END create_file]

                # Or upload a file directly
                # [START upload_file]
                with open(SOURCE_FILE, "rb") as source:
                    await my_file.upload_file(source)
                # [END upload_file]

                # Download the file
                # [START download_file]
                with open(DEST_FILE, "wb") as data:
                    stream = await my_file.download_file()
                    data.write(await stream.readall())
                # [END download_file]

                # Delete the files
                # [START delete_file]
                await my_file.delete_file()
                # [END delete_file]
                await my_allocated_file.delete_file()

            finally:
                # Delete the share
                await share.delete_share()

    async def file_copy_from_url_async(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.fileshare.aio import ShareClient
        share = ShareClient.from_connection_string(self.connection_string, "filesamples2")

        # Create the share
        async with share:
            await share.create_share()

            try:
                # Get a file client and upload a file
                source_file = share.get_file_client("sourcefile")
                with open(SOURCE_FILE, "rb") as source:
                    await source_file.upload_file(source)

                # Create another file client which will copy the file from url
                destination_file = share.get_file_client("destinationfile")

                # Build the url from which to copy the file
                source_url = "https://{}.file.core.windows.net/{}/{}".format(
                    self.account_name,
                    'filesamples2',
                    'sourcefile'
                )

                # Copy the sample source file from the url to the destination file
                # [START copy_file_from_url]
                await destination_file.start_copy_from_url(source_url=source_url)
                # [END copy_file_from_url]
            finally:
                # Delete the share
                await share.delete_share()


async def main():
    sample = FileSamplesAsync()
    await sample.simple_file_operations_async()
    await sample.file_copy_from_url_async()

if __name__ == '__main__':
    asyncio.run(main())
