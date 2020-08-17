# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: blob_samples_walk_blob_hierarchy_async.py

DESCRIPTION:
    This example walks the containers and blobs within a storage account,
    displaying them in a hierarchical structure and, when present, showing
    the number of snapshots that are available per blob. This sample expects
    that the `AZURE_STORAGE_CONNECTION_STRING` environment variable is set.
    It SHOULD NOT be hardcoded in any code derived from this sample.

USAGE: python blob_samples_walk_blob_hierarchy_async.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account

EXAMPLE OUTPUT:

C: container1
F:    folder1/
F:       subfolder1/
B:          test.rtf
B:       test.rtf
F:    folder2/
B:       test.rtf
B:    test.rtf (1 snapshots)
B:    test2.rtf
C: container2
B:    demovid.mp4
B:    mountain.jpg
C: container3
C: container4
"""

import asyncio
import os
import sys

from azure.storage.blob.aio import BlobServiceClient

from azure.storage.blob import BlobPrefix

try:
    CONNECTION_STRING = os.environ['AZURE_STORAGE_CONNECTION_STRING']
except KeyError:
    print("AZURE_STORAGE_CONNECTION_STRING must be set.")
    sys.exit(1)

async def walk_container(client, container):
    container_client = client.get_container_client(container.name)
    print('C: {}'.format(container.name))
    depth = 1
    separator = '   '

    async def walk_blob_hierarchy(prefix=""):
        nonlocal depth
        async for item in container_client.walk_blobs(name_starts_with=prefix):
            short_name = item.name[len(prefix):]
            if isinstance(item, BlobPrefix):
                print('F: ' + separator * depth + short_name)
                depth += 1
                await walk_blob_hierarchy(prefix=item.name)
                depth -= 1
            else:
                message = 'B: ' + separator * depth + short_name
                snapshots = []
                async for snapshot in container_client.list_blobs(name_starts_with=item.name, include=['snapshots']):
                    snapshots.append(snapshot)
                num_snapshots = len(snapshots) - 1
                if num_snapshots:
                    message += " ({} snapshots)".format(num_snapshots)
                print(message)
    await walk_blob_hierarchy()

async def main():
    try:
        async with BlobServiceClient.from_connection_string(CONNECTION_STRING) as service_client:
            containers = service_client.list_containers()
            async for container in containers:
                await walk_container(service_client, container)
    except Exception as error:
        print(error)
        sys.exit(1)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
