# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
'''
FILE: sample2_create_disco_group_from_template.py

DESCRIPTION:
    This sample shows you how to use the discovery_groups module to create discovery groups using templates provided by the discovery_templates module of the EasmClient

Prerequisites:
     * The Defender EASM client library for Python

USAGE:
    python sample2_create_disco_group_from_template.py

    Set the following environment variables before running the sample:
    1) SUBSCRIPTION_ID - the subscription id for your resource
    2) WORKSPACE_NAME - the workspace name for your resource
    3) RESOURCE_GROUP - the resource group for your resource
    4) REGION - the azure region your resource is in
    5) PARTIAL_NAME - the search term for the templates. used for a case insensitive "contains" search
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

# The discovery_templates.list method can be used to find a discovery template using a filter.
# The endpoint will return templates based on a partial match on the name field.
partial_name = os.environ['PARTIAL_NAME']
templates = client.discovery_templates.list(filter=partial_name)

for template in templates:
    print(f'{template["id"]}: {template["displayName"]}')

# To get more detail about a disco template, we can use the discovery_templates.get method.
# From here, we can see the names and seeds which would be used in a discovery run.
template_id = input('choose a template id: ')
template = client.discovery_templates.get(template_id)

print(f'Chosen template id: {template_id}')
print('The following names will be used:')
for name in template['names']:
    print(name)
print()

print('The following seeds will be used:')
for seed in template['seeds']:
    print(f'{seed["kind"]}, {seed["name"]}')
print()

#The discovery template can be used to create a discovery group with using the EasmClient's discovery_groups.put method. Don't forget to run your new disco group with discovery_groups.run
group_name = 'sample discovery group'

request = {'templateId': template_id}
response = client.discovery_groups.put(group_name, body=request)

client.discovery_groups.run(group_name)
