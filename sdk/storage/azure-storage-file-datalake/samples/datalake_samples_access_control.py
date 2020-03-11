# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: datalake_samples_access_control.py
DESCRIPTION:
    This sample demonstrates set/get access control on directories and files.
USAGE:
    python datalake_samples_access_control.py
    Set the environment variables with your own values before running the sample:
    1) STORAGE_ACCOUNT_NAME - the storage account name
    2) STORAGE_ACCOUNT_KEY - the storage account key
"""

import os
import random
import uuid

from azure.storage.filedatalake import (
    DataLakeServiceClient,
)


def access_control_sample(filesystem_client):
    # create a parent directory
    dir_name = "testdir"
    print("Creating a directory named '{}'.".format(dir_name))
    directory_client = filesystem_client.create_directory(dir_name)

    # populate the directory with some child files
    create_child_files(directory_client, 35)

    # get and display the permissions of the parent directory
    acl_props = directory_client.get_access_control()
    print("Permissions of directory '{}' are {}.".format(dir_name, acl_props['permissions']))

    # set the permissions of the parent directory
    new_dir_permissions = 'rwx------'
    directory_client.set_access_control(permissions=new_dir_permissions)

    # get and display the permissions of the parent directory again
    acl_props = directory_client.get_access_control()
    print("New permissions of directory '{}' are {}.".format(dir_name, acl_props['permissions']))

    # iterate through every file and set their permissions to match the directory
    for file in filesystem_client.get_paths(dir_name):
        file_client = filesystem_client.get_file_client(file.name)

        # get the access control properties of the file
        acl_props = file_client.get_access_control()

        if acl_props['permissions'] != new_dir_permissions:
            file_client.set_access_control(permissions=new_dir_permissions)
            print("Set the permissions of file '{}' to {}.".format(file.name, new_dir_permissions))
        else:
            print("Permission for file '{}' already matches the parent.".format(file.name))


def create_child_files(directory_client, num_child_files):
    import concurrent.futures
    import itertools
    # Use a thread pool because it is too slow otherwise
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        def create_file():
            # generate a random name
            file_name = str(uuid.uuid4()).replace('-', '')
            directory_client.get_file_client(file_name).create_file()

        futures = {executor.submit(create_file) for _ in itertools.repeat(None, num_child_files)}
        concurrent.futures.wait(futures)
        print("Created {} files under the directory '{}'.".format(num_child_files, directory_client.path_name))


def run():
    account_name = os.getenv('STORAGE_ACCOUNT_NAME', "")
    account_key = os.getenv('STORAGE_ACCOUNT_KEY', "")

    # set up the service client with the credentials from the environment variables
    service_client = DataLakeServiceClient(account_url="{}://{}.dfs.core.windows.net".format(
        "https",
        account_name
    ), credential=account_key)

    # generate a random name for testing purpose
    fs_name = "testfs{}".format(random.randint(1, 1000))
    print("Generating a test filesystem named '{}'.".format(fs_name))

    # create the filesystem
    filesystem_client = service_client.create_file_system(file_system=fs_name)

    # invoke the sample code
    try:
        access_control_sample(filesystem_client)
    finally:
        # clean up the demo filesystem
        filesystem_client.delete_file_system()


if __name__ == '__main__':
    run()
