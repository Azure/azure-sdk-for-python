# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# These examples are ingested by the documentation system, and are
# displayed in the SDK reference documentation. When editing these
# example snippets, take into consideration how this might affect
# the readability and usability of the reference documentation.

# All interactions starts with an instance of PurviewSharingClient, the client
# Create a share client
# [START create_a_share_client]
import os

from azure.purview.sharing import PurviewSharingClient
from azure.identity import DefaultAzureCredential

endpoint = os.environ["ENDPOINT"]
credential = DefaultAzureCredential()

client = PurviewSharingClient(endpoint=endpoint, credential=credential)
# [END create_a_share_client]

# Create a sent share
# [START create_a_sent_share]
import uuid

sent_share_id = uuid.uuid4()

artifact = {
    "properties": {
        "paths": [
            {
                "containerName": "container-name",
                "receiverPath": "shared-file-name.txt",
                "senderPath": "original/file-name.txt"
            }
        ]
    },
    "storeKind": "AdlsGen2Account",
    "storeReference": {
        "referenceName": "/subscriptions/{subscription-id}/resourceGroups/provider-storage-rg/providers/Microsoft.Storage/storageAccounts/providerstorage",
        "type": "ArmResourceReference"
    }
}

sent_share = {
    "properties": {
        "artifact": artifact,
        "displayName": "sampleShare",
        "description": "A sample share"
    },
    "shareKind": "InPlace"
}

request = client.sent_shares.begin_create_or_replace(
    str(sent_share_id),
    sent_share=sent_share)

response = request.result()
# [END create_a_sent_share]

# Send a user invitation
# [START send_a_user_invitation]
from datetime import date

sent_share_invitation_id = uuid.uuid4()
consumerEmail = "consumer@contoso.com"
today = date.today()
invitation = {
    "invitationKind": "User",
    "properties": {
        "targetEmail": consumerEmail,
        "notify": "true",
        "expirationDate": date(today.year+1,today.month,today.day).strftime("%Y-%m-%d") + " 00:00:00"
    }
}

invitation_response = client.sent_shares.create_invitation(
    sent_share_id=str(sent_share_id),
    sent_share_invitation_id=str(sent_share_invitation_id),
    sent_share_invitation=invitation)
# [END send_a_user_invitation]

# Send a service invitation
# [START send_a_service_invitation]
targetActiverDirectoryId = "72f988bf-86f1-41af-91ab-2d7cd011db47"
targetObjectId = "fc010728-94f6-4e9c-be3c-c08687414bd4"

sent_share_invitation = {
    "invitationKind": "Service",
    "properties": {
        "targetActiveDirectoryId": targetActiverDirectoryId,
        "targetObjectId": targetObjectId
    }
}

invitation_response = client.sent_shares.create_invitation(
    sent_share_id=str(sent_share_id),
    sent_share_invitation_id=str(sent_share_invitation_id),
    sent_share_invitation=sent_share_invitation)
# [END send_a_service_invitation]

# Get a sent share
# [START get_a_sent_share]
get_response = client.sent_shares.get(sent_share_id=str(sent_share_id))
# [END get_a_sent_share]

# Get all sent shares
# [START get_all_sent_shares]
list_request = client.sent_shares.list(
    reference_name=str(sent_share["properties.artifact.storeReference.referenceName"]),
    orderby="properties/createdAt desc")
# [END get_all_sent_shares]

# Delete a sent share
# [START delete_a_sent_share]
delete_request = client.sent_shares.begin_delete(sent_share_id=str(sent_share_id))
delete_response = delete_request.result()
# [END delete_a_sent_share]

# Get a sent share invitation (new)
# [START get_a_sent_share_invitation]
get_invitation_request = client.sent_shares.get_invitation(
    sent_share_id=str(sent_share_id), 
    sent_share_invitation_id=str(sent_share_invitation_id))
#[END get_a_sent_share_invitation]

# View sent invitations
# [START view_sent_invitations]
list_request = client.sent_shares.list_invitations(sent_share_id=str(sent_share_id))
# [END view_sent_invitations]

# Delete a sent share invitation (new)
# [START delete_a_sent_share_invitation]
delete_invitation_request = client.sent_shares.begin_delete_invitation(
    sent_share_id=str(sent_share_id),
    sent_share_invitation_id=str(sent_share_invitation_id))
delete_invitation_response = delete_invitation_request.result()
# [END delete_a_sent_share_invitation]