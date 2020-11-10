# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: datalake_samples_access_control_recursive_async.py
DESCRIPTION:
    This sample demonstrates recursive set/get access control on directories.
USAGE:
    python datalake_samples_access_control_recursive_async.py
    Set the environment variables with your own values before running the sample:
    1) STORAGE_ACCOUNT_NAME - the storage account name
    2) STORAGE_ACCOUNT_KEY - the storage account key
"""

import os
import random
import uuid
import asyncio

from azure.core.exceptions import AzureError

from azure.storage.filedatalake.aio import (
    DataLakeServiceClient,
)


# TODO: rerun after test account is fixed
async def recursive_access_control_sample(filesystem_client):
    # create a parent directory
    dir_name = "testdir"
    print("Creating a directory named '{}'.".format(dir_name))
    directory_client = await filesystem_client.create_directory(dir_name)

    # populate the directory with some child files
    await create_child_files(directory_client, 35)

    # get and display the permissions of the parent directory
    acl_props = await directory_client.get_access_control()
    print("Permissions of directory '{}' are {}.".format(dir_name, acl_props['permissions']))

    # set the permissions of the entire directory tree recursively
    # update/remove acl operations are performed the same way
    acl = 'user::rwx,group::r-x,other::rwx'
    failed_entries = []

    # the progress callback is invoked each time a batch is completed
    async def progress_callback(acl_changes):
        print(("In this batch: {} directories and {} files were processed successfully, {} failures were counted. " +
               "In total, {} directories and {} files were processed successfully, {} failures were counted.")
              .format(acl_changes.batch_counters.directories_successful, acl_changes.batch_counters.files_successful,
                      acl_changes.batch_counters.failure_count, acl_changes.aggregate_counters.directories_successful,
                      acl_changes.aggregate_counters.files_successful, acl_changes.aggregate_counters.failure_count))

        # keep track of failed entries if there are any
        failed_entries.append(acl_changes.batch_failures)

    # illustrate the operation by using a small batch_size
    try:
        acl_change_result = await directory_client.set_access_control_recursive(acl=acl,
                                                                                progress_hook=progress_callback,
                                                                                batch_size=5)
    except AzureError as error:
        # if the error has continuation_token, you can restart the operation using that continuation_token
        if error.continuation_token:
            acl_change_result = \
                await directory_client.set_access_control_recursive(acl=acl,
                                                                    continuation_token=error.continuation_token,
                                                                    progress_hook=progress_callback,
                                                                    batch_size=5)

    print("Summary: {} directories and {} files were updated successfully, {} failures were counted."
          .format(acl_change_result.counters.directories_successful, acl_change_result.counters.files_successful,
                  acl_change_result.counters.failure_count))

    # if an error was encountered, a continuation token would be returned if the operation can be resumed
    if acl_change_result.continuation is not None:
        print("The operation can be resumed by passing the continuation token {} again into the access control method."
              .format(acl_change_result.continuation))

    # get and display the permissions of the parent directory again
    acl_props = await directory_client.get_access_control()
    print("New permissions of directory '{}' and its children are {}.".format(dir_name, acl_props['permissions']))


async def create_child_files(directory_client, num_child_files):
    import itertools

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
            await recursive_access_control_sample(filesystem_client)
        finally:
            # clean up the demo filesystem
            await filesystem_client.delete_file_system()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
