# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: file_samples_share_async.py

DESCRIPTION:
    These samples demonstrate share operations like creating a share snapshot,
    setting share quota and metadata, listing directories and files in the
    file share, and getting directory and file clients from a share client.

USAGE:
    python file_samples_share_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
"""

import os
import asyncio
from azure.storage.fileshare import ShareAccessTier

SOURCE_FILE = './SampleSource.txt'
DEST_FILE = './SampleDestination.txt'


class ShareSamplesAsync(object):

    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

    async def create_share_snapshot_async(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.fileshare.aio import ShareClient
        share = ShareClient.from_connection_string(self.connection_string, "sharesamples1")

        async with share:
            # [START create_share]
            # Create share with Access Tier set to Hot
            await share.create_share(access_tier=ShareAccessTier("Hot"))
            # [END create_share]
            try:
                # [START create_share_snapshot]
                await share.create_snapshot()
                # [END create_share_snapshot]
            finally:
                # [START delete_share]
                await share.delete_share(delete_snapshots=True)
                # [END delete_share]

    async def set_share_quota_and_metadata_async(self):
        # [START create_share_client_from_conn_string]
        from azure.storage.fileshare.aio import ShareClient
        share = ShareClient.from_connection_string(self.connection_string, "sharesamples2")
        # [END create_share_client_from_conn_string]

        # Create the share
        async with share:
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
                props = (await share.get_share_properties()).metadata

            finally:
                # Delete the share
                await share.delete_share()

    async def set_share_properties(self):
        from azure.storage.fileshare.aio import ShareClient
        share1 = ShareClient.from_connection_string(self.connection_string, "sharesamples3a")
        share2 = ShareClient.from_connection_string(self.connection_string, "sharesamples3b")

        # Create the share
        async with share1 and share2:
            await share1.create_share()
            await share2.create_share()

            try:
                # [START set_share_properties]
                # Set the tier for the first share to Hot
                await share1.set_share_properties(access_tier="Hot")
                # Set the quota for the first share to 3
                await share1.set_share_properties(quota=3)
                # Set the tier for the second share to Cool and quota to 2
                await share2.set_share_properties(access_tier=ShareAccessTier("Cool"), quota=2)

                # Get the shares' properties
                props1 = await share1.get_share_properties()
                props2 = await share2.get_share_properties()
                print(props1.access_tier)
                print(props1.quota)
                print(props2.access_tier)
                print(props2.quota)
                # [END set_share_properties]

            finally:
                # Delete the shares
                await share1.delete_share()
                await share2.delete_share()

    async def list_directories_and_files_async(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.fileshare.aio import ShareClient
        share = ShareClient.from_connection_string(self.connection_string, "sharesamples4")

        # Create the share
        async with share:
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

    async def get_directory_or_file_client_async(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.fileshare.aio import ShareClient
        share = ShareClient.from_connection_string(self.connection_string, "sharesamples5")

        # Get the directory client to interact with a specific directory
        my_dir = share.get_directory_client("dir1")

        # Get the file client to interact with a specific file
        my_file = share.get_file_client("dir1/myfile")


async def main():
    sample = ShareSamplesAsync()
    await sample.create_share_snapshot_async()
    await sample.set_share_quota_and_metadata_async()
    await sample.set_share_properties()
    await sample.list_directories_and_files_async()
    await sample.get_directory_or_file_client_async()

if __name__ == '__main__':
    asyncio.run(main())
