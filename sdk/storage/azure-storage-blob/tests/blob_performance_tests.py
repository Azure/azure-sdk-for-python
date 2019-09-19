# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import datetime
import sys
import random

from azure.storage.blob import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
)

CONN_STR = os.getenv('CONNECTION_STRING')
DEST_FILE = 'BlobDestination.txt'
CONFIG = {
    'client': 'blob',  # allowed: 'blob' and 'container'
    'max_connections': 1, # allowed >= 1
    'size_in_mb': 10,
    'blob_type': 'BlockBlob', # allowed: 'BlockBlob', 'PageBlob', 'AppendBlob'
    'blob_name': 'myblob'
}

def create_random_content_file(file_name, size_in_megs):
    if not os.path.exists(file_name):
        with open(file_name, 'wb') as stream:
            for i in range(size_in_megs):
                stream.write(os.urandom(1048576))
        return stream

def upload_blob(blob_client, stream, blob_type, max_connections):
    # Upload
    blob_client.upload_blob(stream, blob_type=blob_type, max_connections=max_connections)

def download_blob(blob_client):
    with open(DEST_FILE, "wb") as my_blob:
        my_blob.writelines(blob_client.download_blob())

def download_loop(blob_client, duration_in_secs=60):
    count = 0
    start_time = datetime.datetime.now()
    elapsed_time = 0
    while elapsed_time <= duration_in_secs:
        download_blob(blob_client)
        count += 1
        elapsed_time = (datetime.datetime.now() - start_time).total_seconds()
    return count

def main():
    try:
        config = CONFIG
        FILE_PATH = 'blob.temp.dat'
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(CONN_STR)

        # Arrange
        size_in_megs = config['size_in_mb']
        blob_name = config['blob_name']
        blob_type = config['blob_type']
        if blob_type not in ('BlockBlob', 'PageBlob', 'AppendBlob'):
            raise ("Invalid blob_type")
        client = config['client']
        max_connections = config['max_connections']

        # Instantiate container
        container_client = blob_service_client.get_container_client("storageperformance")
        container_client.create_container()
        # blob_client = container_client.get_blob_client(blob_name)
        print("Testing for following config")
        print(CONFIG)


        for i in range(10):
            # Create a blob client
            blob_client = container_client.get_blob_client(blob_name + str(i))
    
            # Create a stream
            start_time = datetime.datetime.now()
            data = create_random_content_file(FILE_PATH, size_in_megs)
            file_creation_time = datetime.datetime.now() - start_time

            print("Iteration number is " + str(i))

            # Upload
            start_time = datetime.datetime.now()
            with open(FILE_PATH, 'rb') as blob_data:
                upload_blob(blob_client, blob_data, blob_type, max_connections)
            elapsed_time = (datetime.datetime.now() - start_time).total_seconds()
            print("Time taken to upload blob is " + str(elapsed_time))

            # Download
            start_time = datetime.datetime.now()
            download_blob(blob_client)
            elapsed_time = (datetime.datetime.now() - start_time).total_seconds()
            print("Time taken to download blob is " + str(elapsed_time))
    finally:
        container_client.delete_container()

if __name__ == '__main__':
    main()
    