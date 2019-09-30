# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import datetime
import sys
import asyncio
import random

# EDIT THE CONFIG HERE.
CONFIG = {
    'max_connections': 1, # allowed >= 1
    'size_in_megs': 500,
    'blob_type': 'BlockBlob', # allowed: 'BlockBlob', 'PageBlob', 'AppendBlob'
}

# YOU CAN MODIFY THE CONNECTION STRING HERE
CONN_STR = os.getenv('CONNECTION_STRING')


DEST_FILE = 'BlobDestination.txt'
FILE_PATH = 'blob.temp.dat'
BLOB_NAME = 'myblob'


def create_random_content_file(file_name, size_in_megs):
    if not os.path.exists(file_name):
        with open(file_name, 'wb') as stream:
            for i in range(size_in_megs):
                stream.write(os.urandom(1048576))
        return stream

def remove_file(file_path):
    if os.path.isfile(file_path):
        try:
            os.remove(file_path)
        except:
            pass

async def upload_blob(blob_client, stream, blob_type, max_connections):
    # Upload
    await blob_client.upload_blob(stream, blob_type=blob_type, max_connections=max_connections)

async def download_blob(blob_client, max_conn):
    #with open(DEST_FILE, "wb") as my_blob:
    await (await blob_client.download_blob()).content_as_bytes(max_connections=max_conn)

async def download_loop(blob_client, duration_in_secs=10):
    count = 0
    start_time = datetime.datetime.now()
    elapsed_time = 0
    while elapsed_time <= duration_in_secs:
        await download_blob(blob_client, CONFIG['max_connections'])
        count += 1
        elapsed_time = (datetime.datetime.now() - start_time).total_seconds()
    return count

async def test_rps(container_client, blob_type, max_connections, duration_in_secs=10):
    blob_client = container_client.get_blob_client(BLOB_NAME)
    with open(FILE_PATH, 'rb') as blob_data:
        await upload_blob(blob_client, blob_data, blob_type, max_connections)
    print('FILE OF SIZE {} UPLOADED, STARTING DOWNLOAD LOOP'.format(CONFIG['size_in_megs']))
    count = await download_loop(blob_client, duration_in_secs)
    print("Number of download requests is {} for size {}".format(count, CONFIG['size_in_megs']))

async def test_spr(container_client, blob_type, max_connections):
    for i in range(10):
        try:
            # Create a blob client
            blob_client = container_client.get_blob_client(BLOB_NAME + str(i))

            # Create a stream
            data = create_random_content_file(FILE_PATH, CONFIG['size_in_megs'])
            print("Iteration number is " + str(i))

            # Upload
            start_time = datetime.datetime.now()
            with open(FILE_PATH, 'rb') as blob_data:
                await upload_blob(blob_client, blob_data, blob_type, max_connections)
            elapsed_time = (datetime.datetime.now() - start_time).total_seconds()
            print("Time taken to upload blob is " + str(elapsed_time))

            # Download
            start_time = datetime.datetime.now()
            await download_blob(blob_client, max_connections)
            elapsed_time = (datetime.datetime.now() - start_time).total_seconds()
            print("Time taken to download blob is " + str(elapsed_time))
        finally:
            remove_file(FILE_PATH)
            remove_file(DEST_FILE)

async def main():
    from azure.storage.blob.aio import BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(CONN_STR)

    try:
        container_client = blob_service_client.get_container_client("storageperformancetests")
        # Arrange
        blob_type = CONFIG['blob_type']
        if blob_type not in ('BlockBlob', 'PageBlob', 'AppendBlob'):
            raise ("Invalid blob_type")
        max_connections = CONFIG['max_connections']

        # Instantiate container and create data
        data = create_random_content_file(FILE_PATH, CONFIG['size_in_megs'])
        await container_client.create_container()

        print("Testing for following config")
        print(CONFIG)

        # UNCOMMENT THIS TO TEST REQUESTS PER SECCOND
        # Test Requests per second
        #await test_rps(container_client, blob_type, max_connections, duration_in_secs=10)

        # UNCOMMENT THIS TO TEST SECONDS PER REQUEST
        # Test Seconds per request
        await test_spr(container_client, blob_type, max_connections)
    finally:
        await container_client.delete_container()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
