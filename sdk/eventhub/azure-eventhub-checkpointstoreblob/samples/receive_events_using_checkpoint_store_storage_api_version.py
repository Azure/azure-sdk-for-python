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
<a href=learn.microsoft.com/azure-stack/user/azure-stack-acs-differences>Azure Stack Hub Documentation</a>
"""

import os
from azure.identity import DefaultAzureCredential
from azure.eventhub import EventHubConsumerClient # type: ignore[attr-defined]
from azure.eventhub.extensions.checkpointstoreblob import BlobCheckpointStore

FULLY_QUALIFIED_NAMESPACE = os.environ["EVENT_HUB_HOSTNAME"]
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']
STORAGE_ACCOUNT = "https://{}.blob.core.windows.net".format(
        os.environ["AZURE_STORAGE_ACCOUNT"])
BLOB_CONTAINER_NAME = "your-blob-container-name"  # Please make sure the blob container resource exists.
STORAGE_SERVICE_API_VERSION = "2019-02-02"


def on_event(partition_context, event):
    # Put your code here.
    # Avoid time-consuming operations.
    print(event)
    partition_context.update_checkpoint(event)


if __name__ == '__main__':
    checkpoint_store = BlobCheckpointStore(
        STORAGE_ACCOUNT,
        container_name=BLOB_CONTAINER_NAME,
        api_version=STORAGE_SERVICE_API_VERSION,
        credential=DefaultAzureCredential()
    )
    client = EventHubConsumerClient(
        FULLY_QUALIFIED_NAMESPACE,
        credential=DefaultAzureCredential(),
        consumer_group='$Default',
        eventhub_name=EVENTHUB_NAME,
        checkpoint_store=checkpoint_store
    )

    try:
        client.receive(on_event)
    except KeyboardInterrupt:
        client.close()
