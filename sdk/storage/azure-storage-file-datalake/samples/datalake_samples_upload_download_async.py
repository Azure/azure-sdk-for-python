# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: datalake_samples_upload_download_async.py
DESCRIPTION:
    This sample demonstrates:
    * Set up a file system
    * Create file
    * Append data to the file
    * Flush data to the file
    * Get file properties
    * Download the uploaded data
    * Delete file system
USAGE:
    python datalake_samples_upload_download_async.py
    Set the environment variables with your own values before running the sample:
    1) STORAGE_ACCOUNT_NAME - the storage account name
    2) STORAGE_ACCOUNT_KEY - the storage account key
"""
import asyncio
import os
import random

from azure.storage.filedatalake.aio import (
    DataLakeServiceClient,
)
SOURCE_FILE = 'SampleSource.txt'

async def upload_download_sample(filesystem_client):
    # create a file before writing content to it
    file_name = "testfile"
    print("Creating a file named '{}'.".format(file_name))
    # [START create_file]
    file_client = filesystem_client.get_file_client(file_name)
    await file_client.create_file()
    # [END create_file]

    # prepare the file content with 4KB of random data
    file_content = get_random_bytes(4*1024)

    # append data to the file
    # the data remain uncommitted until flush is performed
    print("Uploading data to '{}'.".format(file_name))
    await file_client.append_data(data=file_content[0:1024], offset=0, length=1024)
    await file_client.append_data(data=file_content[1024:2048], offset=1024, length=1024)
    # [START append_data]
    await file_client.append_data(data=file_content[2048:3072], offset=2048, length=1024)
    # [END append_data]
    await file_client.append_data(data=file_content[3072:4096], offset=3072, length=1024)

    # data is only committed when flush is called
    await file_client.flush_data(len(file_content))

    # Get file properties
    # [START get_file_properties]
    properties = await file_client.get_file_properties()
    # [END get_file_properties]

    # read the data back
    print("Downloading data from '{}'.".format(file_name))
    # [START read_file]
    download = await file_client.download_file()
    downloaded_bytes = await download.readall()
    # [END read_file]

    # verify the downloaded content
    if file_content == downloaded_bytes:
        print("The downloaded data is equal to the data uploaded.")
    else:
        print("Something went wrong.")

    # Rename the file
    # [START rename_file]
    new_client = await file_client.rename_file(file_client.file_system_name + '/' + 'newname')
    # [END rename_file]

    # download the renamed file in to local file
    with open(SOURCE_FILE, 'wb') as stream:
        download = await new_client.download_file()
        await download.readinto(stream)

    # [START delete_file]
    await new_client.delete_file()
    # [END delete_file]

# help method to provide random bytes to serve as file content
def get_random_bytes(size):
    rand = random.Random()
    result = bytearray(size)
    for i in range(size):
        result[i] = int(rand.random()*255)  # random() is consistent between python 2 and 3
    return bytes(result)


async def main():
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
            await upload_download_sample(filesystem_client)
        finally:
            # clean up the demo filesystem
            await filesystem_client.delete_file_system()


if __name__ == '__main__':
    asyncio.run(main())
