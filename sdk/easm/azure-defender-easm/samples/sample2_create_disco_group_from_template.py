'''
This sample shows you how to use the discovery_groups module to create discovery groups using templates provided by the discovery_templates module of the EasmClient
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

# The discovery_templates.list method can be used to find a discovery template using a filter.
# The endpoint will return templates based on a partial match on the name field.
partial_name = 'taco'
templates = client.discovery_templates.list(filter=partial_name)

for template in templates:
    print(f'{template["id"]}: {template["displayName"]}')

# To get more detail about a disco template, we can use the discovery_templates.get method.
# From here, we can see the names and seeds which would be used in a discovery run.
template_id = '<your chosen template id>'
template = client.discovery_templates.get(template_id)

for name in template['names']:
    print(name)

for seed in template['seeds']:
    print(f'{seed["kind"]}, {seed["name"]}')

#The discovery template can be used to create a discovery group with using a DiscoGroupRequest and the EasmClient's discovery_groups.put method. Don't forget to run your new disco group with discovery_groups.run
group_name = '<your group name here>'

request = {'templateId': template_id}
response = client.discovery_groups.put(group_name, body=request)

client.discovery_groups.run(group_name)
