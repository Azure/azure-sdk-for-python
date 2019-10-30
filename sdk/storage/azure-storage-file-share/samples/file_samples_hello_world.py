# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: file_samples_hello_world.py

DESCRIPTION:
    These samples demonstrate common scenarios like instantiating a client,
    creating a file share, and uploading a file to a share.

USAGE:
    python file_samples_hello_world.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
"""

import os

SOURCE_FILE = './SampleSource.txt'
DEST_FILE = './SampleDestination.txt'


class HelloWorldSamples(object):

    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

    def create_client_with_connection_string(self):
        # Instantiate the ShareServiceClient from a connection string
        from azure.storage.fileshare import ShareServiceClient
        file_service = ShareServiceClient.from_connection_string(self.connection_string)

    def create_file_share(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.fileshare import ShareClient
        share = ShareClient.from_connection_string(self.connection_string, share_name="helloworld1")

        # Create the share
        share.create_share()

        try:
            # [START get_share_properties]
            properties = share.get_share_properties()
            # [END get_share_properties]

        finally:
            # Delete the share
            share.delete_share()

    def upload_a_file_to_share(self):
        # Instantiate the ShareClient from a connection string
        from azure.storage.fileshare import ShareClient
        share = ShareClient.from_connection_string(self.connection_string, share_name="helloworld2")

        # Create the share
        share.create_share()

        try:
            # Instantiate the ShareFileClient from a connection string
            # [START create_file_client]
            from azure.storage.fileshare import ShareFileClient
            file = ShareFileClient.from_connection_string(
                self.connection_string,
                share_name="helloworld2",
                file_path="myfile")
            # [END create_file_client]

            # Upload a file
            with open(SOURCE_FILE, "rb") as source_file:
                file.upload_file(source_file)

        finally:
            # Delete the share
            share.delete_share()


if __name__ == '__main__':
    sample = HelloWorldSamples()
    sample.create_client_with_connection_string()
    sample.create_file_share()
    sample.upload_a_file_to_share()
