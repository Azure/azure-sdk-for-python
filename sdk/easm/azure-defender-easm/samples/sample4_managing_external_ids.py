# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
'''
FILE: sample4_managing_external_ids.py

DESCRIPTION:
    External IDs can be a useful method of keeping track of assets in multiple systems, but it can be time consuming to manually tag each asset. In this example, we'll take a look at how you can, with a map of name/kind/external id, tag each asset in your inventory with an external id automatically using the SDK

Prerequisites:
     * The Defender EASM client library for Python
     * a json file with a mapping of name and kind to external id, like so:
    [
        {
            'name': 'example.com',
            'kind': 'host',
            'external_id': 'EXT040'
        },
        {
            'name': 'example.com',
            'kind': 'domain',
            'external_id': 'EXT041'
        }
    ]

USAGE:
    python sample4_managing_external_ids.py

    Set the following environment variables before running the sample:
    1) SUBSCRIPTION_ID - the subscription id for your resource
    2) WORKSPACE_NAME - the workspace name for your resource
    3) RESOURCE_GROUP - the resource group for your resource
    4) REGION - the azure region your resource is in
    5) MAPPING - a json file with an external id mapping.
'''

import os
import json
from azure.identity import InteractiveBrowserCredential
from azure.defender.easm import EasmClient

#To create an EasmClient, you need your subscription ID, region, and some sort of credential.
sub_id = os.environ['SUBSCRIPTION_ID']
workspace_name = os.environ['WORKSPACE_NAME']
resource_group = os.environ['RESOURCE_GROUP']
region = os.environ['REGION']
endpoint = f'{region}.easm.defender.microsoft.com'

# For the purposes of this demo, I've chosen the InteractiveBrowserCredential but any credential will work.
browser_credential = InteractiveBrowserCredential()
client = EasmClient(endpoint, resource_group, sub_id, workspace_name, browser_credential)

# Assets in EASM can be uniquely distinguished by `name` and `kind`, so we can create a simple dictionary containing `name`, `kind`, and `external_id`. In a more realistic case, this could be generated using an export from the external system we're using for tagging
external_id_mapping = None
with open(os.environ['MAPPING']) as mapping:
    external_id_mapping = json.load(mapping)

# Using the `assets` client, we can update each asset and append the tracking id of the update to our update ID list, so that we can keep track of the progress on each update later
update_ids = []

for asset in external_id_mapping:
    update_request = {'externalId': asset['external_id']}
    asset_filter = f"kind = {asset['kind']} AND name = {asset['name']}"
    update = client.assets.update(body=update_request, filter=asset_filter)
    update_ids.append(update['id'])

# Using the `tasks` client, we can view the progress of each update using the `get` method
for update_id in update_ids:
    update = client.tasks.get(update_id)
    print(f'{update["id"]}: {update["state"]}')

# The updates can be viewed using the `assets.list` method by creating a filter that matches on each external id using an `in` query
ids = ', '.join([f'"{asset["external_id"]}"' for asset in external_id_mapping])
asset_filter = f'External ID in ({ids})'

for asset in client.assets.list(filter=asset_filter):
    print(f'{asset["externalId"]}, {asset["name"]}')

