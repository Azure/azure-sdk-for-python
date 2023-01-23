'''
Saved Filters are used to store a query within EASM, these saved queries can be used to synchronize exact queries across multiple scripts, or to ensure a team is looking at the same assets
In this example, we'll go over how a saved filter could be used to synchronize the a query across multiple scripts
'''
from azure.identity import InteractiveBrowserCredential
from azure.defender.easm import EasmClient

sub_id = '<your subscription ID here>'
workspace_name = '<your workspace name here>'
resource_group = '<your resource group here>'
region = '<your region here>'

endpoint = f'{region}.easm.defender.microsoft.com'

browser_credential = InteractiveBrowserCredential()
client = EasmClient(endpoint, resource_group, sub_id, workspace_name, browser_credential)

# To create a Saved Filter, we need to send a filter, name, and description to the `saved_filters.put` endpoint
saved_filter_name = '<your saved filter name here>'
request = {
	'filter': 'IP Address = 151.101.192.67',
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
	#your asset update request body here
}

client.assets.update(body, filter=asset_filter)

# Should your needs change, the filter can be updated with no need to update the scripts it's used in
# Simply submit a new `saved_filters.put` request to replace the old description and filter with a new set
request = {'filter': 'IP Address = 0.0.0.0', 'description': 'Monitored Addresses'}
client.saved_filters.put(saved_filter_name, body=request)
