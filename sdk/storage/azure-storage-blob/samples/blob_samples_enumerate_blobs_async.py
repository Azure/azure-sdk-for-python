# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: enumerate_blobs_async.py
DESCRIPTION:
    This sample demos how to enumerate a container and print all blobs.
USAGE: python enumerate_blobs_async.py
"""

from __future__ import print_function
import os
import sys
import asyncio
from azure.storage.blob.aio import ContainerClient

async def main():
    try:
        CONNECTION_STRING = os.environ['AZURE_STORAGE_CONNECTION_STRING']
    except KeyError:
        print("AZURE_STORAGE_CONNECTION_STRING must be set.")
        sys.exit(1)

    container = ContainerClient.from_connection_string(CONNECTION_STRING, container_name="mycontainer")

    async for blob in container.list_blobs():
        print(blob.name + '\n')

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
