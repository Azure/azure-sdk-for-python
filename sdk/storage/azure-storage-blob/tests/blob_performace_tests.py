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
    client: 'blob',  # allowed: 'blob' and 'container'
    max_connections: 1, # allowed >= 1
    size_in_mb: 10,
    blob_type: 'BlockBlob' # allowed: 'BlockBlob', 'PageBlob', 'AppendBlob'
    blob_name: 'myblob'
}

def get_random_bytes(size):
    rand = random.Random()
    result = bytearray(size)
    for i in range(size):
        result[i] = int(rand.random()*255)  # random() is consistent between python 2 and 3
    return bytes(result)

def upload_blob(config=CONFIG):
    from azure.storage.blob import BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(CONN_STR)

    # Arrange
    size_in_bytes = config['size_in_mb'] * 10^6
    blob_name = config['blob_name']
    blob_type = config['blob_type']
    if blob_type not in ('BlockBlob', 'PageBlob', 'AppendBlob'):
        raise ("Invalid blob_type")
    client = config['client']
    max_connections = config['max_connections']
    data = get_random_bytes(size_in_bytes)
    FILE_PATH = 'blob_input.temp.dat'
    with open(FILE_PATH, 'wb') as stream:
        stream.write(data)

    # Instantiate a new ContainerClient
    container_client = blob_service_client.get_container_client("mycontainer")
    container_client.create_container()

    # Upload
    if client == 'container':
        container_client.upload_blob(blob_name, stream, blob_type=blob_type, max_connections=max_connections)
    elif client == 'blob':
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(stream, blob_type=blob_type, max_connections=max_connections)
    else:
        raise("client should be 'container' or 'blob'")

def download_blob(config=CONFIG):
    from azure.storage.blob import BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(CONN_STR)

    # Arrange
    size_in_bytes = config['size_in_mb'] * 10^6
    blob_name = config['blob_name']
    blob_type = config['blob_type']
    if blob_type not in ('BlockBlob', 'PageBlob', 'AppendBlob'):
        raise ("Invalid blob_type")
    client = config['client']
    max_connections = config['max_connections']

    # Instantiate a new ContainerClient
    container_client = blob_service_client.get_container_client("mycontainer")
    container_client.create_container()

    with open(DEST_FILE, "wb") as my_blob:
        my_blob.writelines(blob_client.download_blob(max_connections=max_connections))

def main():
    print("testing for following config")
    print(CONFIG)
    start_time = datetime.datetime.now()
    upload_blob(config=CONFIG)
    elapsed_time = datetime.datetime.now() - start_time
    print("Time taken to upload blob is" + elapsed_time)

    start_time = datetime.datetime.now()
    download_blob(config=CONFIG)
    elapsed_time = datetime.datetime.now() - start_time
    print("Time taken to download blob is" + elapsed_time)

if __name__ == '__main__':
    main()
    