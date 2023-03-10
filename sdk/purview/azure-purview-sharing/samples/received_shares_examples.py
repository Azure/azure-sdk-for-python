# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# These examples are ingested by the documentation system, and are
# displayed in the SDK reference documentation. When editing these
# example snippets, take into consideration how this might affect
# the readability and usability of the reference documentation.

# Create a received share client

# [START create_a_received_share_client]
import os

from azure.purview.sharing import PurviewSharingClient
from azure.identity import DefaultAzureCredential

endpoint = os.environ["ENDPOINT"]
credential = DefaultAzureCredential()

client = PurviewSharingClient(endpoint=endpoint,credential=credential)
# [END create_a_received_share_client]

# Get all detached received shares
# [START get_all_detached_received_shares]
list_detached_response = client.received_shares.list_detached(orderby="properties/createdAt desc")
# [END get_all_detached_received_shares]

# Attach a received share
# [START attach_a_received_share]
import json

consumer_storage_account_resource_id = "/subscriptions/{subscription-id}/resourceGroups/consumer-storage-rg/providers/Microsoft.Storage/storageAccounts/consumerstorage"
received_share = next(x for x in list_detached_response)

store_reference = {
    "referenceName": consumer_storage_account_resource_id,
    "type": "ArmResourceReference"
}

sink = {
    "properties": {
        "containerName": "container-test",
        "folder": "folder-test",
        "mountPath": "mountPath-test",
    },
    "storeKind": "AdlsGen2Account",
    "storeReference": store_reference
}

received_share['properties']['sink'] = sink

update_response = client.received_shares.begin_create_or_replace(
    str(received_share['id']),
    received_share=received_share)
# [END attach_a_received_share]

# Get a received share
# [START get_a_received_share]
get_share_response = client.received_shares.get(received_share_id=received_share['id'])
# [END get_a_received_share]

# List attached received shares
# [START list_attached_received_shares]
list_attached_response = client.received_shares.list_attached(
    reference_name=consumer_storage_account_resource_id,
    orderby="properties/createdAt desc")
# [END list_attached_received_shares]

# Delete a received share
# [START delete_a_received_share]
delete_received_share_response = client.received_shares.begin_delete(received_share_id=received_share['id'])
# [END delete_a_received_share]