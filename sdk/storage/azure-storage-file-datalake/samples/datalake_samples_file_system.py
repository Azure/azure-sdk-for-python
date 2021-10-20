# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: datalake_samples_file_system.py
DESCRIPTION:
    This sample demonstrates common file system operations including list paths, create a file system,
    set metadata etc.
USAGE:
    python datalake_samples_file_system.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
"""

import os

from azure.core.exceptions import ResourceExistsError

SOURCE_FILE = 'SampleSource.txt'


class FileSystemSamples(object):

    connection_string = os.environ['AZURE_STORAGE_CONNECTION_STRING']

    #--Begin File System Samples-----------------------------------------------------------------

    def file_system_sample(self):

        # [START create_file_system_client_from_service]
        # Instantiate a DataLakeServiceClient using a connection string
        from azure.storage.filedatalake import DataLakeServiceClient
        datalake_service_client = DataLakeServiceClient.from_connection_string(self.connection_string)

        # Instantiate a FileSystemClient
        file_system_client = datalake_service_client.get_file_system_client("mynewfilesystem")
        # [END create_file_system_client_from_service]

        try:
            # [START create_file_system]
            file_system_client.create_file_system()
            # [END create_file_system]

            # [START get_file_system_properties]
            properties = file_system_client.get_file_system_properties()
            # [END get_file_system_properties]

        finally:
            # [START delete_file_system]
            file_system_client.delete_file_system()
            # [END delete_file_system]

    def acquire_lease_on_file_system(self):

        # Instantiate a DataLakeServiceClient using a connection string
        # [START create_data_lake_service_client_from_conn_str]
        from azure.storage.filedatalake import DataLakeServiceClient
        datalake_service_client = DataLakeServiceClient.from_connection_string(self.connection_string)
        # [END create_data_lake_service_client_from_conn_str]

        # Instantiate a FileSystemClient
        file_system_client = datalake_service_client.get_file_system_client("myleasefilesystem")

        # Create new File System
        try:
            file_system_client.create_file_system()
        except ResourceExistsError:
            pass

        # [START acquire_lease_on_file_system]
        # Acquire a lease on the file system
        lease = file_system_client.acquire_lease()

        # Delete file system by passing in the lease
        file_system_client.delete_file_system(lease=lease)
        # [END acquire_lease_on_file_system]

    def set_metadata_on_file_system(self):

        # Instantiate a DataLakeServiceClient using a connection string
        from azure.storage.filedatalake import DataLakeServiceClient
        datalake_service_client = DataLakeServiceClient.from_connection_string(self.connection_string)

        # Instantiate a FileSystemClient
        file_system_client = datalake_service_client.get_file_system_client("mymetadatafilesystemsync")

        try:
            # Create new File System
            file_system_client.create_file_system()

            # [START set_file_system_metadata]
            # Create key, value pairs for metadata
            metadata = {'type': 'test'}

            # Set metadata on the file system
            file_system_client.set_file_system_metadata(metadata=metadata)
            # [END set_file_system_metadata]

            # Get file system properties
            properties = file_system_client.get_file_system_properties()

        finally:
            # Delete file system
            file_system_client.delete_file_system()

    def list_paths_in_file_system(self):

        # Instantiate a DataLakeServiceClient using a connection string
        from azure.storage.filedatalake import DataLakeServiceClient
        datalake_service_client = DataLakeServiceClient.from_connection_string(self.connection_string)

        # Instantiate a FileSystemClient
        file_system_client = datalake_service_client.get_file_system_client("myfilesystemforlistpaths")

        # Create new File System
        file_system_client.create_file_system()

        # [START upload_file_to_file_system]
        with open(SOURCE_FILE, "rb") as data:
            file_client = file_system_client.get_file_client("myfile")
            file_client.create_file()
            file_client.append_data(data, 0)
            file_client.flush_data(data.tell())
        # [END upload_file_to_file_system]

        # [START get_paths_in_file_system]
        path_list = file_system_client.get_paths()
        for path in path_list:
            print(path.name + '\n')
        # [END get_paths_in_file_system]

        # Delete file system
        file_system_client.delete_file_system()

    def get_file_client_from_file_system(self):

        # Instantiate a DataLakeServiceClient using a connection string
        from azure.storage.filedatalake import DataLakeServiceClient
        datalake_service_client = DataLakeServiceClient.from_connection_string(self.connection_string)

        # Instantiate a FileSystemClient
        file_system_client = datalake_service_client.get_file_system_client("myfilesystemforgetclient")

        # Create new File System
        try:
            file_system_client.create_file_system()
        except ResourceExistsError:
            pass

        # [START get_file_client_from_file_system]
        # Get the FileClient from the FileSystemClient to interact with a specific file
        file_client = file_system_client.get_file_client("mynewfile")
        # [END get_file_client_from_file_system]

        # Delete file system
        file_system_client.delete_file_system()

    def get_directory_client_from_file_system(self):

        # Instantiate a DataLakeServiceClient using a connection string
        from azure.storage.filedatalake import DataLakeServiceClient
        datalake_service_client = DataLakeServiceClient.from_connection_string(self.connection_string)

        # Instantiate a FileSystemClient
        file_system_client = datalake_service_client.get_file_system_client("myfilesystem")

        # Create new File System
        try:
            file_system_client.create_file_system()
        except ResourceExistsError:
            pass

        # [START get_directory_client_from_file_system]
        # Get the DataLakeDirectoryClient from the FileSystemClient to interact with a specific file
        directory_client = file_system_client.get_directory_client("mynewdirectory")
        # [END get_directory_client_from_file_system]

        # Delete file system
        file_system_client.delete_file_system()

    def create_file_from_file_system(self):
        # [START create_file_system_client_from_connection_string]
        from azure.storage.filedatalake import FileSystemClient
        file_system_client = FileSystemClient.from_connection_string(self.connection_string, "filesystem")
        # [END create_file_system_client_from_connection_string]

        file_system_client.create_file_system()

        # [START create_directory_from_file_system]
        directory_client = file_system_client.create_directory("mydirectory")
        # [END create_directory_from_file_system]

        # [START create_file_from_file_system]
        file_client = file_system_client.create_file("myfile")
        # [END create_file_from_file_system]

        # [START delete_file_from_file_system]
        file_system_client.delete_file("myfile")
        # [END delete_file_from_file_system]

        # [START delete_directory_from_file_system]
        file_system_client.delete_directory("mydirectory")
        # [END delete_directory_from_file_system]

        file_system_client.delete_file_system()

    # [START batch_delete_files_or_empty_directories]
    def batch_delete_files_or_empty_directories(self):
        from azure.storage.filedatalake import FileSystemClient
        file_system_client = FileSystemClient.from_connection_string(self.connection_string, "filesystem")

        file_system_client.create_file_system()

        data = b'hello world'

        try:
            # create file1
            file_system_client.get_file_client('file1').upload_data(data, overwrite=True)

            # create file2, then pass file properties in batch delete later
            file2 = file_system_client.get_file_client('file2')
            file2.upload_data(data, overwrite=True)
            file2_properties = file2.get_file_properties()

            # create file3 and batch delete it later only etag matches this file3 etag
            file3 = file_system_client.get_file_client('file3')
            file3.upload_data(data, overwrite=True)
            file3_etag = file3.get_file_properties().etag

            # create dir1. Empty directory can be deleted using delete_files
            file_system_client.get_directory_client('dir1').create_directory(),

            # create dir2, then pass directory properties in batch delete later
            dir2 = file_system_client.get_directory_client('dir2')
            dir2.create_directory()
            dir2_properties = dir2.get_directory_properties()
        except:
            pass

        # Act
        response = file_system_client.delete_files(
            'file1',
            file2_properties,
            {'name': 'file3', 'etag': file3_etag},
            'dir1',
            dir2_properties,
            raise_on_any_failure=False
        )
        print("total number of sub-responses:" + len(response))
        print(response[0].status_code)
        print(response[2].status_code)
        print(response[3].status_code)
    # [END batch_delete_files_or_empty_directories]


if __name__ == '__main__':
    sample = FileSystemSamples()
    sample.file_system_sample()
    sample.acquire_lease_on_file_system()
    sample.set_metadata_on_file_system()
    sample.list_paths_in_file_system()
    sample.get_file_client_from_file_system()
    sample.create_file_from_file_system()
    sample.batch_delete_files_or_empty_directories()
