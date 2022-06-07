# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: datalake_samples_file_system_async.py
DESCRIPTION:
    This sample demonstrates common file system operations including list paths, create a file system,
    set metadata etc.
USAGE:
    python datalake_samples_file_system_async.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
"""
import asyncio
import os

from azure.core.exceptions import ResourceExistsError

SOURCE_FILE = 'SampleSource.txt'


class FileSystemSamplesAsync(object):

    connection_string = os.environ['AZURE_STORAGE_CONNECTION_STRING']

    #--Begin File System Samples-----------------------------------------------------------------

    async def file_system_sample(self):

        # [START create_file_system_client_from_service]
        # Instantiate a DataLakeServiceClient using a connection string
        from azure.storage.filedatalake.aio import DataLakeServiceClient
        datalake_service_client = DataLakeServiceClient.from_connection_string(self.connection_string)

        async with datalake_service_client:
            # Instantiate a FileSystemClient
            file_system_client = datalake_service_client.get_file_system_client("mynewfilesystems")
            # [END create_file_system_client_from_service]

            try:
                # [START create_file_system]
                await file_system_client.create_file_system()
                # [END create_file_system]

                # [START get_file_system_properties]
                properties = await file_system_client.get_file_system_properties()
                # [END get_file_system_properties]

            finally:
                # [START delete_file_system]
                await file_system_client.delete_file_system()
                # [END delete_file_system]

    async def acquire_lease_on_file_system(self):

        # Instantiate a DataLakeServiceClient using a connection string
        # [START create_data_lake_service_client_from_conn_str]
        from azure.storage.filedatalake.aio import DataLakeServiceClient
        datalake_service_client = DataLakeServiceClient.from_connection_string(self.connection_string)
        # [END create_data_lake_service_client_from_conn_str]

        async with datalake_service_client:
            # Instantiate a FileSystemClient
            file_system_client = datalake_service_client.get_file_system_client("myleasefilesystem")

            # Create new File System
            try:
                await file_system_client.create_file_system()
            except ResourceExistsError:
                pass

            # [START acquire_lease_on_file_system]
            # Acquire a lease on the file system
            lease = await file_system_client.acquire_lease()

            # Delete file system by passing in the lease
            await file_system_client.delete_file_system(lease=lease)
            # [END acquire_lease_on_file_system]

    async def set_metadata_on_file_system(self):

        # Instantiate a DataLakeServiceClient using a connection string
        from azure.storage.filedatalake.aio import DataLakeServiceClient
        datalake_service_client = DataLakeServiceClient.from_connection_string(self.connection_string)

        async with datalake_service_client:
            # Instantiate a FileSystemClient
            file_system_client = datalake_service_client.get_file_system_client("mymetadatafilesystemsync")

            try:
                # Create new File System
                await file_system_client.create_file_system()

                # [START set_file_system_metadata]
                # Create key, value pairs for metadata
                metadata = {'type': 'test'}

                # Set metadata on the file system
                await file_system_client.set_file_system_metadata(metadata=metadata)
                # [END set_file_system_metadata]

                # Get file system properties
                properties = await file_system_client.get_file_system_properties()

            finally:
                # Delete file system
                await file_system_client.delete_file_system()

    async def list_paths_in_file_system(self):

        # Instantiate a DataLakeServiceClient using a connection string
        from azure.storage.filedatalake.aio import DataLakeServiceClient
        datalake_service_client = DataLakeServiceClient.from_connection_string(self.connection_string)

        async with datalake_service_client:
            # Instantiate a FileSystemClient
            file_system_client = datalake_service_client.get_file_system_client("mypathfilesystem")

            # Create new File System
            await file_system_client.create_file_system()

            # [START upload_file_to_file_system]
            file_client = file_system_client.get_file_client("myfile")
            await file_client.create_file()
            with open(SOURCE_FILE, "rb") as data:
                length = data.tell()
                await file_client.append_data(data, 0)
                await file_client.flush_data(length)
            # [END upload_file_to_file_system]

            # [START get_paths_in_file_system]
            path_list = file_system_client.get_paths()
            async for path in path_list:
                print(path.name + '\n')
            # [END get_paths_in_file_system]

            # Delete file system
            await file_system_client.delete_file_system()

    async def get_file_client_from_file_system(self):

        # Instantiate a DataLakeServiceClient using a connection string
        from azure.storage.filedatalake.aio import DataLakeServiceClient
        datalake_service_client = DataLakeServiceClient.from_connection_string(self.connection_string)

        async with datalake_service_client:
            # Instantiate a FileSystemClient
            file_system_client = datalake_service_client.get_file_system_client("myclientfilesystem")

            # Create new File System
            try:
                await file_system_client.create_file_system()
            except ResourceExistsError:
                pass

            # [START get_file_client_from_file_system]
            # Get the FileClient from the FileSystemClient to interact with a specific file
            file_client = file_system_client.get_file_client("mynewfile")
            # [END get_file_client_from_file_system]

            # Delete file system
            await file_system_client.delete_file_system()

    async def get_directory_client_from_file_system(self):

        # Instantiate a DataLakeServiceClient using a connection string
        from azure.storage.filedatalake.aio import DataLakeServiceClient
        datalake_service_client = DataLakeServiceClient.from_connection_string(self.connection_string)

        async with datalake_service_client:
            # Instantiate a FileSystemClient
            file_system_client = datalake_service_client.get_file_system_client("mydirectoryfilesystem")

            # Create new File System
            try:
                await file_system_client.create_file_system()
            except ResourceExistsError:
                pass

            # [START get_directory_client_from_file_system]
            # Get the DataLakeDirectoryClient from the FileSystemClient to interact with a specific file
            directory_client = file_system_client.get_directory_client("mynewdirectory")
            # [END get_directory_client_from_file_system]

            # Delete file system
            await file_system_client.delete_file_system()

    async def create_file_from_file_system(self):
        # [START create_file_system_client_from_connection_string]
        from azure.storage.filedatalake.aio import FileSystemClient
        file_system_client = FileSystemClient.from_connection_string(self.connection_string, "filesystemforcreate")
        # [END create_file_system_client_from_connection_string]

        async with file_system_client:
            await file_system_client.create_file_system()

            # [START create_directory_from_file_system]
            directory_client = await file_system_client.create_directory("mydirectory")
            # [END create_directory_from_file_system]

            # [START create_file_from_file_system]
            file_client = await file_system_client.create_file("myfile")
            # [END create_file_from_file_system]

            # [START delete_file_from_file_system]
            await file_system_client.delete_file("myfile")
            # [END delete_file_from_file_system]

            # [START delete_directory_from_file_system]
            await file_system_client.delete_directory("mydirectory")
            # [END delete_directory_from_file_system]

            await file_system_client.delete_file_system()
    
    # [START batch_delete_files_or_empty_directories]
    async def batch_delete_files_or_empty_directories(self):
        from azure.storage.filedatalake import FileSystemClient
        file_system_client = FileSystemClient.from_connection_string(self.connection_string, "filesystem")

        async with file_system_client:
            await file_system_client.create_file_system()

        data = b'hello world'

        try:
            # create file1
            await file_system_client.get_file_client('file1').upload_data(data, overwrite=True)

            # create file2, then pass file properties in batch delete later
            file2 = file_system_client.get_file_client('file2')
            await file2.upload_data(data, overwrite=True)

            # create file3 and batch delete it later only etag matches this file3 etag
            file3 = file_system_client.get_file_client('file3')
            await file3.upload_data(data, overwrite=True)

            # create dir1. Empty directory can be deleted using delete_files
            await file_system_client.get_directory_client('dir1').create_directory()
            await file_system_client.get_directory_client('dir1').create_file('file4')

        except:
            pass

        response = await file_system_client.delete_files(
            'file1',
            'file2',
            'file3',
            'dir1', # dir1 is not empty
            'dir8', # dir8 doesn't exist
        )
        print("Total number of sub-responses: " + len(response) + "\n")
        print("First failure error code: " + response[3].error_code + "\n")
        print("First failure status code: " + response[3].status_code + "\n")
        print("Second failure error code: " + response[4].error_code + "\n")
        print("Second failure status code: " + response[4].status_code + "\n")
    # [END batch_delete_files_or_empty_directories]


async def run():
    sample = FileSystemSamplesAsync()
    await sample.file_system_sample()
    await sample.acquire_lease_on_file_system()
    await sample.set_metadata_on_file_system()
    await sample.list_paths_in_file_system()
    await sample.get_file_client_from_file_system()
    await sample.create_file_from_file_system()
    await sample.batch_delete_files_or_empty_directories()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    loop.close()
