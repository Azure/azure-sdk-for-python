# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: file_samples_share.py

DESCRIPTION:
    These samples demonstrate share operations like creating a share snapshot,
    setting share quota and metadata, listing directories and files in the
    file share, and getting directory and file clients from a share client.

USAGE:
    python file_samples_share.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
"""

import os

SOURCE_FILE = './SampleSource.txt'
DEST_FILE = './SampleDestination.txt'


class ShareSamples(object):

    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

    def create_share_snapshot(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.fileshare import ShareClient
        share = ShareClient.from_connection_string(self.connection_string, "sharesamples1")

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

    def set_share_quota_and_metadata(self):
        # [START create_share_client_from_conn_string]
        from azure.storage.fileshare import ShareClient
        share = ShareClient.from_connection_string(self.connection_string, "sharesamples2")
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

        finally:
            # Delete the share
            share.delete_share()

    def list_directories_and_files(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.fileshare import ShareClient
        share = ShareClient.from_connection_string(self.connection_string, "sharesamples3")

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

    def get_directory_or_file_client(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.fileshare import ShareClient
        share = ShareClient.from_connection_string(self.connection_string, "sharesamples4")

        # Get the directory client to interact with a specific directory
        my_dir = share.get_directory_client("dir1")

        # Get the file client to interact with a specific file
        my_file = share.get_file_client("dir1/myfile")


if __name__ == '__main__':
    sample = ShareSamples()
    sample.create_share_snapshot()
    sample.set_share_quota_and_metadata()
    sample.list_directories_and_files()
    sample.get_directory_or_file_client()
