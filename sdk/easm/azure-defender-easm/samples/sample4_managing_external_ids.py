'''
External IDs can be a useful method of keeping track of assets in multiple systems, but it can be time consuming to manually tag each asset. In this example, we'll take a look at how you can, with a map of name/kind/external id, tag each asset in your inventory with an external id automatically using the SDK
'''
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

# Assets in EASM can be uniquely distinguished by `name` and `kind`, so we can create a simple dictionary containing `name`, `kind`, and `external_id`. In a more realistic case, this could be generated using an export from the external system we're using for tagging, but for our purposes, we can manually write it out
external_id_mapping = [
    {
        'name': 'example.com',
        'kind': 'host',
        'external_id': 'EXT040'
    },
    {
        'name': 'example.com',
        'kind': 'domain',
        'external_id': 'EXT041'
    },
    {
        'name': '93.184.216.34',
        'kind': 'ipAddress',
        'external_id': 'EXT042'
    },
    {
        'name': 'example.org',
        'kind': 'host',
        'external_id': 'EXT050'
    },
]
# Using the `assets` client, we can update each asset and append the tracking id of the update to our update ID list, so that we can keep track of the progress on each update later
update_ids = []

for asset in external_id_mapping:
    update_request = {'external_id': asset['external_id']}
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

