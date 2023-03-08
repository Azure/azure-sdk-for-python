# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# These examples are ingested by the documentation system, and are
# displayed in the SDK reference documentation. When editing these
# example snippets, take into consideration how this might affect
# the readability and usability of the reference documentation.

# All interactions starts with an instance of PurviewSharing, the client
# Create a share client
# [START create_a_share_client]
import os

from azure.purview.sharing import PurviewSharing
from azure.identity import ClientSecretCredential

endpoint = os.environ["ENDPOINT"]
tenant_id = os.environ.get("AZURE_TENANT_ID", getattr(os.environ, "TENANT_ID", None))
client_id = os.environ.get("AZURE_CLIENT_ID", getattr(os.environ, "CLIENT_ID", None))
secret = os.environ.get("AZURE_CLIENT_SECRET", getattr(os.environ, "CLIENT_SECRET", None))
credential = ClientSecretCredential(tenant_id=str(tenant_id), client_id=str(client_id), client_secret=str(secret))

client = PurviewSharing(endpoint=endpoint, credential=credential)
# [END create_a_share_client]

# Create a sent share
# [START create_a_sent_share]
import uuid, json

from azure.purview.sharing.operations._operations import (
    build_sent_shares_create_or_replace_request
)

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
        "displayName": "sample=share",
        "description": "A sample share"
    },
    "shareKind": "InPlace"
}

request = build_sent_shares_create_or_replace_request(
    str(sent_share_id),
    content_type="application/json",
    content=json.dumps(sent_share))

response = client.send_request(request)
# [END create_a_sent_share]

# Get a sent share
# [START get_a_sent_share]
from azure.purview.sharing.operations._operations import (
    build_sent_shares_get_request
)

get_request = build_sent_shares_get_request(sent_share_id=str(sent_share_id))
get_response = client.send_request(get_request)

retrieved_sent_share = json.loads(get_response.content)
# [END get_a_sent_share]

# Delete a sent share
# [START delete_a_sent_share]
from azure.core.exceptions import HttpResponseError
from azure.purview.sharing.operations._operations import (
    build_sent_shares_delete_request
)

delete_request = build_sent_shares_delete_request(sent_share_id=str(sent_share_id))
delete_response = client.send_request(delete_request)

try:
    delete_response.raise_for_status()
except HttpResponseError as e:
    print("Exception " + str(e))
    print("Response " + delete_response.text())
# [END delete_a_sent_share]

# Get all sent shares
# [START get_all_sent_shares]
from azure.purview.sharing.operations._operations import (
    build_sent_shares_list_request
)

list_request = build_sent_shares_list_request(
    reference_name=str(sent_share["properties.artifact.storeReference.referenceName"]),
    orderby="properties/createdAt desc")

list_response = client.send_request(list_request)
list = json.loads(list_response.content)['value']
# [END get_all_sent_shares]

# Send a user invitation
# [START send_a_user_invitation]
from datetime import date
from azure.purview.sharing.operations._operations import (
    build_sent_shares_create_invitation_request
)

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

invitation_request = build_sent_shares_create_invitation_request(
    sent_share_id=str(sent_share_id),
    sent_share_invitation_id=str(sent_share_invitation_id),
    content_type="application/json",
    content=json.dumps(invitation))

invitation_response = client.send_request(invitation_request)
created_invitation = json.loads(invitation_response.content)
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

invitation_request = build_sent_shares_create_invitation_request(
    sent_share_id=str(sent_share_id),
    sent_share_invitation_id=str(sent_share_invitation_id),
    content_type="application/json",
    content=json.dumps(sent_share_invitation))

invitation_response = client.send_request(invitation_request)
created_invitation = json.loads(invitation_response.content)
# [END send_a_service_invitation]

# View sent invitations
# [START view_sent_invitations]
from azure.purview.sharing.operations._operations import (
    build_sent_shares_list_invitations_request
)

list_request = build_sent_shares_list_invitations_request(sent_share_id=str(sent_share_id))
list_response = client.send_request(list_request)
list = json.loads(list_response.content)['value']
# [END view_sent_invitations]