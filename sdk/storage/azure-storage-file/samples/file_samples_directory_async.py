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


class DirectorySamples(object):

    async def create_directory(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.file.aio import ShareClient
        share = ShareClient.from_connection_string(CONNECTION_STRING, "myshare")

        # Create the share
        await share.create_share()

        try:
            # Get the directory client
            directory = share.get_directory_client(directory_path="mydirectory")

            # [START create_directory]
            await directory.create_directory()
            # [END create_directory]

            # [START upload_file_to_directory]
            # Upload a file to the directory
            with open(SOURCE_FILE, "rb") as source:
                await directory.upload_file(file_name="sample", data=source)
            # [END upload_file_to_directory]

            # [START delete_file_in_directory]
            # Delete the file in the directory
            await directory.delete_file(file_name="sample")
            # [END delete_file_in_directory]

            # [START delete_directory]
            await directory.delete_directory()
            # [END delete_directory]

        finally:
            # Delete the share
            await share.delete_share()

    async def create_subdirectories(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.file.aio import ShareClient
        share = ShareClient.from_connection_string(CONNECTION_STRING, "myshare")

        # Create the share
        await share.create_share()

        try:
            # Get the directory client
            parent_dir = share.get_directory_client(directory_path="parentdir")

            # [START create_subdirectory]
            # Create the directory
            await parent_dir.create_directory()

            # Create a subdirectory
            subdir = parent_dir.create_subdirectory("subdir")
            # [END create_subdirectory]

            # Upload a file to the parent directory
            with open(SOURCE_FILE, "rb") as source:
                await parent_dir.upload_file(file_name="sample", data=source)

            # Upload a file to the subdirectory
            with open(SOURCE_FILE, "rb") as source:
                await subdir.upload_file(file_name="sample", data=source)

            # [START lists_directory]
            # List the directories and files under the parent directory
            my_list = []
            async for item in parent_dir.list_directories_and_files():
                my_list.append(item)
            print(my_list)
            # [END lists_directory]

            # You must delete the file in the subdirectory before deleting the subdirectory
            await subdir.delete_file("sample")
            # [START delete_subdirectory]
            await parent_dir.delete_subdirectory("subdir")
            # [END delete_subdirectory]

        finally:
            # Delete the share
            await share.delete_share()

    async def get_subdirectory_client(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.file.aio import ShareClient
        share = ShareClient.from_connection_string(CONNECTION_STRING, "myshare")

        # Create the share
        await share.create_share()

        try:
            # [START get_subdirectory_client]
            # Get a directory client and create the directory
            parent = share.get_directory_client("directory1")
            await parent.create_directory()

            # Get a subdirectory client and create the subdirectory "dir1/dir2"
            subdirectory = parent.get_subdirectory_client("directory2")
            await subdirectory.create_directory()
            # [END get_subdirectory_client]
        finally:
            # Delete the share
            await share.delete_share()

