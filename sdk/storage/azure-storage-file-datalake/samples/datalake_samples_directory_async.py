# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: datalake_samples_directory_async.py
DESCRIPTION:
    This sample demonstrates create directory, rename directory, get directory properties, delete directory etc.
USAGE:
    python datalake_samples_directory_async.py
    Set the environment variables with your own values before running the sample:
    1) STORAGE_ACCOUNT_NAME - the storage account name
    2) STORAGE_ACCOUNT_KEY - the storage account key
"""

import asyncio
import os
import random
import uuid

from azure.core.exceptions import ResourceExistsError

from azure.storage.filedatalake.aio import (
    DataLakeServiceClient,
)


async def directory_sample(filesystem_client):
    # create a parent directory
    dir_name = "testdir"
    print("Creating a directory named '{}'.".format(dir_name))

    # Create directory from file system client
    await filesystem_client.create_directory(dir_name)

    directory_client = filesystem_client.get_directory_client(dir_name)
    try:
        # Create the existing directory again will throw exception
        # [START create_directory]
        await directory_client.create_directory()
        # [END create_directory]
    except ResourceExistsError:
        pass

    # populate the directory with some child files
    await create_child_files(directory_client, 35)

    # rename the directory
    # [START rename_directory]
    new_dir_name = "testdir2"
    print("Renaming the directory named '{}' to '{}'.".format(dir_name, new_dir_name))
    new_directory = await directory_client\
        .rename_directory(new_name=directory_client.file_system_name + '/' + new_dir_name)
    # [END rename_directory]

    # display the properties of the new directory to make sure it was renamed successfully
    # [START get_directory_properties]
    props = await new_directory.get_directory_properties()
    # [END get_directory_properties]
    print("Properties of the new directory named '{}' are: {}.".format(new_dir_name, props))

    # remove the newly renamed directory
    print("Removing the directory named '{}'.".format(new_dir_name))
    # [START delete_directory]
    await new_directory.delete_directory()
    # [END delete_directory]


async def create_child_files(directory_client, num_child_files):
    import itertools
    # Use a thread pool because it is too slow otherwise

    async def create_file():
        # generate a random name
        file_name = str(uuid.uuid4()).replace('-', '')
        file_client = directory_client.get_file_client(file_name)
        await file_client.create_file()

    futures = [asyncio.ensure_future(create_file()) for _ in itertools.repeat(None, num_child_files)]
    await asyncio.wait(futures)
    print("Created {} files under the directory '{}'.".format(num_child_files, directory_client.path_name))


async def run():
    account_name = os.getenv('STORAGE_ACCOUNT_NAME', "")
    account_key = os.getenv('STORAGE_ACCOUNT_KEY', "")

    # set up the service client with the credentials from the environment variables
    service_client = DataLakeServiceClient(account_url="{}://{}.dfs.core.windows.net".format(
        "https",
        account_name
    ), credential=account_key)

    async with service_client:
        # generate a random name for testing purpose
        fs_name = "testfs{}".format(random.randint(1, 1000))
        print("Generating a test filesystem named '{}'.".format(fs_name))

        # create the filesystem
        filesystem_client = await service_client.create_file_system(file_system=fs_name)

        # invoke the sample code
        try:
            await directory_sample(filesystem_client)
        finally:
            # clean up the demo filesystem
            await filesystem_client.delete_file_system()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
