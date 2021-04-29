#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
The following sample can be used if the environment you are targeting supports a different version of Storage Blob
SDK than those typically available on Azure. For example, if you are running Event Hubs on an Azure Stack Hub version
2002, the highest available version for the Storage service is version 2017-11-09. In this case, you will need to
specify param api_version to 2017-11-09 when creating the BlobCheckpointStore. For more information on the Azure Storage
service versions supported on Azure Stack Hub, please refer to
<a href=docs.microsoft.com/azure-stack/user/azure-stack-acs-differences>Azure Stack Hub Documentation</a>
"""

import asyncio
import os
from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblobaio import BlobCheckpointStore

CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']
STORAGE_CONNECTION_STR = os.environ["AZURE_STORAGE_CONN_STR"]
BLOB_CONTAINER_NAME = "your-blob-container-name"  # Please make sure the blob container resource exists.
STORAGE_SERVICE_API_VERSION = "2017-11-09"


async def on_event(partition_context, event):
    # Put your code here.
    # Do some sync or async operations. If the operation is i/o intensive, async will have better performance.
    print(event)
    await partition_context.update_checkpoint(event)


async def main(client):
    async with client:
        await client.receive(on_event)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    checkpoint_store = BlobCheckpointStore.from_connection_string(
        STORAGE_CONNECTION_STR,
        container_name=BLOB_CONTAINER_NAME,
        api_version=STORAGE_SERVICE_API_VERSION
    )
    client = EventHubConsumerClient.from_connection_string(
        CONNECTION_STR,
        consumer_group='$Default',
        eventhub_name=EVENTHUB_NAME,
        checkpoint_store=checkpoint_store
    )
    try:
        loop.run_until_complete(main(client))
    finally:
        loop.stop()
