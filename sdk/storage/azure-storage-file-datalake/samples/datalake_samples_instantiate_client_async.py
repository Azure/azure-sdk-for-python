# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: datalake_samples_instantiate_client_async.py
DESCRIPTION:
    This sample demonstrates how to instantiate directory/file client
USAGE:
    python datalake_samples_instantiate_client_async.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
    connection str could be obtained from portal.azure.com your storage account.
"""
import asyncio
import os
connection_string = os.environ['AZURE_STORAGE_CONNECTION_STRING']


async def instantiate_directory_client_from_conn_str():
    # [START instantiate_directory_client_from_conn_str]
    from azure.storage.filedatalake.aio import DataLakeDirectoryClient
    DataLakeDirectoryClient.from_connection_string(connection_string, "myfilesystem", "mydirectory")
    # [END instantiate_directory_client_from_conn_str]


async def instantiate_file_client_from_conn_str():
    # [START instantiate_file_client_from_conn_str]
    from azure.storage.filedatalake.aio import DataLakeFileClient
    DataLakeFileClient.from_connection_string(connection_string, "myfilesystem", "mydirectory", "myfile")
    # [END instantiate_file_client_from_conn_str]


async def main():
    await instantiate_directory_client_from_conn_str()
    await instantiate_file_client_from_conn_str()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
