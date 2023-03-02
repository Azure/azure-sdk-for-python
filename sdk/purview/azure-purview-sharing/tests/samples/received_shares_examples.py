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

from azure.purview.sharing import PurviewSharing

endpoint = os.environ["ENDPOINT"]
client = PurviewSharing(endpoint=endpoint)
# [END create_a_received_share_client]

# Get all detached received shares
# [START get_all_detached_recieved_shares]
from azure.purview.sharing.operations._operations import (
    build_received_shares_list_detached_request
)

list_detached_request = build_received_shares_list_detached_request(orderby="properties/createdAt desc")
list_detached_response = client.send_request(list_detached_request)
# [END get_all_detached_recieved_shares]

# Attach a received share
# [START attach_a_received_share]
import json

from azure.core.exceptions import HttpResponseError
from azure.purview.sharing.operations._operations import (
    build_received_shares_create_or_replace_request
)

consumer_storage_account_resource_id = "/subscriptions/{subscription-id}/resourceGroups/consumer-storage-rg/providers/Microsoft.Storage/storageAccounts/consumerstorage"
list_detached = json.loads(list_detached_response.content)
received_share = list_detached['value'][0]

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

update_request = build_received_shares_create_or_replace_request(
    received_share['id'],
    content_type="application/json",
    content=json.dumps(received_share))

update_response = client.send_request(update_request)
try:
    update_response.raise_for_status()
except HttpResponseError as e:
    print("Exception " + str(e))
    print("Response " + update_response.text())
# [END attach_a_received_share]

# Get a received share
# [START get_a_received_share]
from azure.purview.sharing.operations._operations import (
    build_received_shares_get_request
)

get_share_request = build_received_shares_get_request(received_share_id=received_share['id'])
get_share_response = client.send_request(get_share_request)

retrieved_share = json.loads(get_share_response.content)
# [END get_a_received_share]

# List attached received shares
# [START list_attached_received_shares]
from azure.purview.sharing.operations._operations import (
    build_received_shares_list_attached_request
)

list_attached_request = build_received_shares_list_attached_request(
    reference_name=consumer_storage_account_resource_id,
    orderby="properties/createdAt desc")

list_attached_response = client.send_request(list_attached_request)
list = json.loads(list_attached_response.content)['value']
# [END list_attached_received_shares]

# Delete a received share
# [START delete_a_recieved_share]
from azure.purview.sharing.operations._operations import (
    build_received_shares_delete_request
)

delete_received_share_request = build_received_shares_delete_request(received_share_id=received_share['id'])
delete_received_share_response = client.send_request(delete_received_share_request)

try:
    delete_received_share_response.raise_for_status()
except HttpResponseError as e:
    print("Exception " + str(e))
    print("Response " + delete_received_share_response.text())
# [END delete_a_recieved_share]