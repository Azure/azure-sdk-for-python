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
    sys.exit(1)

SOURCE_FILE = 'SampleSource.txt'
data = b"Lorem ipsum dolor sit amet, consectetur adipiscing elit"
with open(SOURCE_FILE, 'wb') as stream:
    stream.write(data)


class TestHelloWorldSamples(object):

    async def create_client_with_connection_string(self):
        # Instantiate the FileServiceClient from a connection string
        from azure.storage.file.aio import FileServiceClient
        file_service = FileServiceClient.from_connection_string(CONNECTION_STRING)

    async def create_file_share(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.file.aio import ShareClient
        share = ShareClient.from_connection_string(CONNECTION_STRING, share_name="myshare")

        # Create the share
        await share.create_share()

        try:
            # [START get_share_properties]
            properties = await share.get_share_properties()
            # [END get_share_properties]

        finally:
            # Delete the share
            await share.delete_share()

    async def upload_a_file_to_share(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.file.aio import ShareClient
        share = ShareClient.from_connection_string(CONNECTION_STRING, share_name='myshare')

        # Create the share
        await share.create_share()

        try:
            # Instantiate the FileClient from a connection string
            # [START create_file_client]
            from azure.storage.file.aio import FileClient
            file = FileClient.from_connection_string(CONNECTION_STRING, share_name='myshare', file_path="myfile")
            # [END create_file_client]

            # Upload a file
            with open(SOURCE_FILE, "rb") as source_file:
                await file.upload_file(source_file)

        finally:
            # Delete the share
            await share.delete_share()

