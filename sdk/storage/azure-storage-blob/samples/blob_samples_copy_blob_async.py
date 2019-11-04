# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: blob_samples_copy_blob_async.py
DESCRIPTION:
    This sample demos how to copy a blob from a URL.
USAGE: python blob_samples_copy_blob_async.py
    Set the environment variables with your own values before running the sample.
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
"""

from __future__ import print_function
import os
import sys
import asyncio
import time
from azure.storage.blob.aio import BlobServiceClient

async def main():
    try:
        CONNECTION_STRING = os.environ['AZURE_STORAGE_CONNECTION_STRING']

    except KeyError:
        print("AZURE_STORAGE_CONNECTION_STRING must be set.")
        sys.exit(1)

    status = None
    blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
    async with blob_service_client:
        source_blob = "http://www.gutenberg.org/files/59466/59466-0.txt"
        copied_blob = blob_service_client.get_blob_client("mycontainer", '59466-0.txt')
        # Copy started"
        await copied_blob.start_copy_from_url(source_blob)
        for i in range(10):
            props = await copied_blob.get_blob_properties()
            status = props.copy.status
            print("Copy status: " + status)
            if status == "success":
                # copy finished
                break
            time.sleep(10)

        if status != "success":
            # if not finished after 100s, cancel the operation
            props = await copied_blob.get_blob_properties()
            print(props.copy.status)
            copy_id = props.copy.id
            await copied_blob.abort_copy(copy_id)
            props = copied_blob.get_blob_properties()
            print(props.copy.status)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
