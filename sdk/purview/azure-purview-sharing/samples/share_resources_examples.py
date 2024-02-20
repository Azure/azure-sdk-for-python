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

# List share resources
# [START list_share_resources]
list_request = client.share_resources.list(
    filter="properties/storeKind eq 'AdlsGen2Account'",
    order_by="properties/createdAt desc")

for list_response in list_request:
    print(list_response)
#[END list_share_resources]