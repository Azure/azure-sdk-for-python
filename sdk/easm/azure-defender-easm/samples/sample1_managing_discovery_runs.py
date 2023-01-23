'''
This sample demonstrates how to create and manage discovery runs in a workspace using the discovery_groups module of the EasmClient
'''
import itertools
from azure.identity import InteractiveBrowserCredential
from azure.defender.easm import EasmClient


#To create an EasmClient, you need your subscription ID, region, and some sort of credential.
sub_id = '<your subscription ID here>'
workspace_name = '<your workspace name here>'
resource_group = '<your resource group here>'
region = '<your region here>'

endpoint = f'{region}.easm.defender.microsoft.com'

# For the purposes of this demo, I've chosen the InteractiveBrowserCredential but any credential will work.
browser_credential = InteractiveBrowserCredential()
client = EasmClient(endpoint, resource_group, sub_id, workspace_name, browser_credential)

# in order to start discovery runs, we must first create a discovery group, which is a collection of known assets that we can pivot off of. these are created using the `discovery_groups.put` method
name = '<your discovery group name here>'
assets = [
    {'kind': 'domain', 'name': '<a domain you want to run discovery against>'},
    {'kind': 'host', 'name': '<a host you want to run discovery against>'}
]
request = {
	'description': '<a description for your discovery group>',
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
