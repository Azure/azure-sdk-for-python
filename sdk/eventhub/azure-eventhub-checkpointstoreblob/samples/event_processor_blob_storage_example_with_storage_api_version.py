#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Some environments have different versions of Azure Storage Service API. For instance, Azure Stack Platform
version 2002 uses Azure Storage Service API 2017-11-07.

Specify api_version when you create the BlobCheckpointStore as shown in this example.
"""

import os
from azure.eventhub import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblob import BlobCheckpointStore

CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
STORAGE_CONNECTION_STR = os.environ["AZURE_STORAGE_CONN_STR"]
BLOB_CONTAINER_NAME = "your-blob-container-name"  # Please make sure the blob container resource exists.
STORAGE_SERVICE_API_VERSION = "2017-11-09"


def on_event(partition_context, event):
    # Put your code here.
    # Avoid time-consuming operations.
    print(event)
    partition_context.update_checkpoint(event)


if __name__ == '__main__':
    checkpoint_store = BlobCheckpointStore.from_connection_string(
        STORAGE_CONNECTION_STR,
        container_name=BLOB_CONTAINER_NAME,
        api_version=STORAGE_SERVICE_API_VERSION
    )
    client = EventHubConsumerClient.from_connection_string(
        CONNECTION_STR,
        "$Default",
        checkpoint_store=checkpoint_store
    )

    try:
        client.receive(on_event)
    except KeyboardInterrupt:
        client.close()
