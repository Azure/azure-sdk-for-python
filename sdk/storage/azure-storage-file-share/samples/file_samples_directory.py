# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: file_samples_directory.py

DESCRIPTION:
    These samples demonstrate directory operations like creating a directory
    or subdirectory, and working on files within the directories.

USAGE:
    python file_samples_directory.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
"""

import os

SOURCE_FILE = './SampleSource.txt'
DEST_FILE = './SampleDestination.txt'


class DirectorySamples(object):

    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

    def create_directory_and_file(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.fileshare import ShareClient
        share = ShareClient.from_connection_string(self.connection_string, "directorysamples1")

        # Create the share
        share.create_share()

        try:
            # Get the directory client
            my_directory = share.get_directory_client(directory_path="mydirectory")

            # [START create_directory]
            my_directory.create_directory()
            # [END create_directory]

            # [START upload_file_to_directory]
            # Upload a file to the directory
            with open(SOURCE_FILE, "rb") as source:
                my_directory.upload_file(file_name="sample", data=source)
            # [END upload_file_to_directory]

            # [START delete_file_in_directory]
            # Delete the file in the directory
            my_directory.delete_file(file_name="sample")
            # [END delete_file_in_directory]

            # [START delete_directory]
            my_directory.delete_directory()
            # [END delete_directory]

        finally:
            # Delete the share
            share.delete_share()

    def create_subdirectory_and_file(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.fileshare import ShareClient
        share = ShareClient.from_connection_string(self.connection_string, "directorysamples2")

        # Create the share
        share.create_share()

        try:
            # Get the directory client
            parent_dir = share.get_directory_client(directory_path="parentdir")

            # [START create_subdirectory]
            # Create the directory
            parent_dir.create_directory()

            # Create a subdirectory
            subdir = parent_dir.create_subdirectory("subdir")
            # [END create_subdirectory]

            # Upload a file to the parent directory
            with open(SOURCE_FILE, "rb") as source:
                parent_dir.upload_file(file_name="sample", data=source)

            # Upload a file to the subdirectory
            with open(SOURCE_FILE, "rb") as source:
                subdir.upload_file(file_name="sample", data=source)

            # [START lists_directory]
            # List the directories and files under the parent directory
            my_list = list(parent_dir.list_directories_and_files())
            print(my_list)
            # [END lists_directory]

            # You must delete the file in the subdirectory before deleting the subdirectory
            subdir.delete_file("sample")
            # [START delete_subdirectory]
            parent_dir.delete_subdirectory("subdir")
            # [END delete_subdirectory]

        finally:
            # Delete the share
            share.delete_share()

    def get_subdirectory_client(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.fileshare import ShareClient
        share = ShareClient.from_connection_string(self.connection_string, "directorysamples3")

        # Create the share
        share.create_share()

        try:
            # [START get_subdirectory_client]
            # Get a directory client and create the directory
            parent = share.get_directory_client("dir1")
            parent.create_directory()

            # Get a subdirectory client and create the subdirectory "dir1/dir2"
            subdirectory = parent.get_subdirectory_client("dir2")
            subdirectory.create_directory()
            # [END get_subdirectory_client]
        finally:
            # Delete the share
            share.delete_share()


if __name__ == '__main__':
    sample = DirectorySamples()
    sample.create_directory_and_file()
    sample.create_subdirectory_and_file()
    sample.get_subdirectory_client()
