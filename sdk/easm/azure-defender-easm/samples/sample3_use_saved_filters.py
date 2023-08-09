# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
'''
FILE: sample3_use_saved_filters.py

DESCRIPTION:
    Saved Filters are used to store a query within EASM, these saved queries can be used to synchronize exact queries across multiple scripts, or to ensure a team is looking at the same assets
    In this example, we'll go over how a saved filter could be used to synchronize the a query across multiple scripts

Prerequisites:
     * The Defender EASM client library for Python

USAGE:
    python sample3_use_saved_filters.py

    Set the following environment variables before running the sample:
    1) SUBSCRIPTION_ID - the subscription id for your resource
    2) WORKSPACE_NAME - the workspace name for your resource
    3) RESOURCE_GROUP - the resource group for your resource
    4) REGION - the azure region your resource is in
'''

import os
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

# To create a Saved Filter, we need to send a filter, name, and description to the `saved_filters.put` endpoint
saved_filter_name = 'sample saved filter'
request = {
	'filter': 'IP Address = 1.1.1.1',
	'description': 'Monitored Addresses',
}
client.saved_filters.put(saved_filter_name, body=request)

# The saved filter can now be used in scripts to monitor the assets
# First, retrieve the saved filter by name, then use it in an asset list or update call

# A sample asset list call that could be used to monitor the assets:
def monitor(asset):
	pass #your monitor logic here

monitor_filter = client.saved_filters.get(saved_filter_name)['filter']

for asset in client.assets.list(filter=monitor_filter):
	monitor(asset)

# A sample asset update call, which could be used to update the monitored assets:
monitor_filter = client.saved_filters.get(saved_filter_name)['filter']

body = {
    'state': 'confirmed'
}

client.assets.update(body, filter=monitor_filter)

# Should your needs change, the filter can be updated with no need to update the scripts it's used in
# Simply submit a new `saved_filters.put` request to replace the old description and filter with a new set
request = {'filter': 'IP Address = 0.0.0.0', 'description': 'Monitored Addresses'}
client.saved_filters.put(saved_filter_name, body=request)
