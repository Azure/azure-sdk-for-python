# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
'''
FILE: sample1_managing_discovery_runs.py

DESCRIPTION:
    This sample demonstrates how to create and manage discovery runs in a workspace using the discovery_groups module of the EasmClient

Prerequisites:
     * The Defender EASM client library for Python

USAGE:
    python sample1_managing_discovery_runs.py

    Set the following environment variables before running the sample:
    1) SUBSCRIPTION_ID - the subscription id for your resource
    2) WORKSPACE_NAME - the workspace name for your resource
    3) RESOURCE_GROUP - the resource group for your resource
    4) REGION - the azure region your resource is in
    5) HOSTS - a comma separated list of hosts you would like to run discovery on
    6) DOMAINS - a comma separated list of hosts you would like to run discovery on
'''

import itertools
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

# in order to start discovery runs, we must first create a discovery group, which is a collection of known assets that we can pivot off of. these are created using the `discovery_groups.put` method

hosts = [{'kind': 'host', 'name': i.strip()} for i in os.environ['HOSTS'].split(',')]
domains = [{'kind': 'host', 'name': i.strip()} for i in os.environ['DOMAINS'].split(',')]
name = 'sample discovery group'
assets = hosts + domains
request = {
	'description': 'Discovery group made using the Defender EASM SDK sample',
	'seeds': assets
}

response = client.discovery_groups.put(name, request)

# Discovery groups created through the API's `put` method aren't run automatically, so we need to start the run ourselves.
client.discovery_groups.run(name)

for group in client.discovery_groups.list():
    print(group['name'])
    runs = client.discovery_groups.list_runs(group['name'])
    for run in itertools.islice(runs, 5):
        print(f" - started: {run['startedDate']}, finished: {run['completedDate']}, assets found: {run['totalAssetsFoundCount']}")
