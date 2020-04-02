# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: datalake_samples_service_async.py
DESCRIPTION:
    This sample demonstrates:
    * Instantiate DataLakeServiceClient using connection str
    * Instantiate DataLakeServiceClient using AAD Credential
    * Get user delegation key
    * Create all kinds of clients from DataLakeServiceClient and operate on those clients
    * List file systems
USAGE:
    python datalake_samples_service_async.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING
    2) STORAGE_ACCOUNT_NAME
    3) ACTIVE_DIRECTORY_APPLICATION_ID
    4) ACTIVE_DIRECTORY_APPLICATION_SECRET
    5) ACTIVE_DIRECTORY_TENANT_ID
"""

import asyncio
import os


connection_string = os.environ['AZURE_STORAGE_CONNECTION_STRING']
account_name = os.getenv('STORAGE_ACCOUNT_NAME', "")
active_directory_application_id = os.getenv("ACTIVE_DIRECTORY_APPLICATION_ID")
active_directory_application_secret = os.getenv("ACTIVE_DIRECTORY_APPLICATION_SECRET")
active_directory_tenant_id = os.getenv("ACTIVE_DIRECTORY_TENANT_ID")

#--Begin DataLake Service Samples-----------------------------------------------------------------

async def data_lake_service_sample():

    # Instantiate a DataLakeServiceClient using a connection string
    # [START create_datalake_service_client]
    from azure.storage.filedatalake.aio import DataLakeServiceClient
    datalake_service_client = DataLakeServiceClient.from_connection_string(connection_string)
    # [END create_datalake_service_client]

    # Instantiate a DataLakeServiceClient Azure Identity credentials.
    # [START create_datalake_service_client_oauth]
    from azure.identity.aio import ClientSecretCredential
    token_credential = ClientSecretCredential(
        active_directory_tenant_id,
        active_directory_application_id,
        active_directory_application_secret,
    )
    datalake_service_client = DataLakeServiceClient("https://{}.dfs.core.windows.net".format(account_name),
                                                    credential=token_credential)
    # [END create_datalake_service_client_oauth]

    async with datalake_service_client:
        # get user delegation key
        # [START get_user_delegation_key]
        from datetime import datetime, timedelta
        user_delegation_key = await datalake_service_client.get_user_delegation_key(datetime.utcnow(),
                                                                              datetime.utcnow() + timedelta(hours=1))
        # [END get_user_delegation_key]

        # Create file systems
        # [START create_file_system_from_service_client]
        await datalake_service_client.create_file_system("filesystem")
        # [END create_file_system_from_service_client]
        file_system_client = await datalake_service_client.create_file_system("anotherfilesystem")

        # List file systems
        # [START list_file_systems]
        file_systems = datalake_service_client.list_file_systems()
        async for file_system in file_systems:
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
        await file_client.create_file(content_settings=content_settings)
        await file_client.set_metadata(metadata=metadata)
        file_props = await file_client.get_file_properties()
        print(file_props.metadata)

        # Create file/directory and set properties
        await directory_client.create_directory(content_settings=content_settings, metadata=metadata)
        dir_props = await directory_client.get_directory_properties()
        print(dir_props.metadata)

        # Delete File Systems
        # [START delete_file_system_from_service_client]
        await datalake_service_client.delete_file_system("filesystem")
        # [END delete_file_system_from_service_client]
        await file_system_client.delete_file_system()

    await token_credential.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(data_lake_service_sample())

