# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: datalake_samples_service.py
DESCRIPTION:
    This sample demonstrates:
    * Instantiate DataLakeServiceClient using connection str
    * Instantiate DataLakeServiceClient using AAD Credential
    * Get user delegation key
    * Create all kinds of clients from DataLakeServiceClient and operate on those clients
    * List file systems
USAGE:
    python datalake_samples_service.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING
    2) STORAGE_ACCOUNT_NAME
"""

import os


class DataLakeServiceSamples(object):

    connection_string = os.environ['AZURE_STORAGE_CONNECTION_STRING']
    account_name = os.getenv('STORAGE_ACCOUNT_NAME', "")

    #--Begin DataLake Service Samples-----------------------------------------------------------------

    def data_lake_service_sample(self):

        # Instantiate a DataLakeServiceClient using a connection string
        # [START create_datalake_service_client]
        from azure.storage.filedatalake import DataLakeServiceClient
        datalake_service_client = DataLakeServiceClient.from_connection_string(self.connection_string)
        # [END create_datalake_service_client]

        # Instantiate a DataLakeServiceClient Azure Identity credentials.
        # [START create_datalake_service_client_oauth]
        from azure.identity import DefaultAzureCredential
        token_credential = DefaultAzureCredential()
        datalake_service_client = DataLakeServiceClient("https://{}.dfs.core.windows.net".format(self.account_name),
                                                        credential=token_credential)
        # [END create_datalake_service_client_oauth]

        # get user delegation key
        # [START get_user_delegation_key]
        from datetime import datetime, timedelta
        user_delegation_key = datalake_service_client.get_user_delegation_key(datetime.utcnow(),
                                                                              datetime.utcnow() + timedelta(hours=1))
        # [END get_user_delegation_key]

        # Create file systems
        # [START create_file_system_from_service_client]
        datalake_service_client.create_file_system("filesystem")
        # [END create_file_system_from_service_client]
        file_system_client = datalake_service_client.create_file_system("anotherfilesystem")

        # List file systems
        # [START list_file_systems]
        file_systems = datalake_service_client.list_file_systems()
        for file_system in file_systems:
            print(file_system.name)
        # [END list_file_systems]

        # Get Clients from DataLakeServiceClient
        file_system_client = datalake_service_client.get_file_system_client(file_system_client.file_system_name)
        # [START get_directory_client_from_service_client]
        directory_client = datalake_service_client.get_directory_client(file_system_client.file_system_name,
                                                                        "mydirectory")
        # [END get_directory_client_from_service_client]
        # [START get_file_client_from_service_client]
        file_client = datalake_service_client.get_file_client(file_system_client.file_system_name, "myfile")
        # [END get_file_client_from_service_client]

        # Create file and set properties
        metadata = {'hello': 'world', 'number': '42'}
        from azure.storage.filedatalake import ContentSettings
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        file_client.create_file(content_settings=content_settings)
        file_client.set_metadata(metadata=metadata)
        file_props = file_client.get_file_properties()
        print(file_props.metadata)

        # Create file/directory and set properties
        directory_client.create_directory(content_settings=content_settings, metadata=metadata)
        dir_props = directory_client.get_directory_properties()
        print(dir_props.metadata)

        # Delete File Systems
        # [START delete_file_system_from_service_client]
        datalake_service_client.delete_file_system("filesystem")
        # [END delete_file_system_from_service_client]
        file_system_client.delete_file_system()


if __name__ == '__main__':
    sample = DataLakeServiceSamples()
    sample.data_lake_service_sample()
