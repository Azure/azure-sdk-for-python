import os

from azure.core.credentials import AzureKeyCredential
from azure.messaging.webpubsubservice import WebPubSubServiceClient
from azure.messaging.webpubsubservice.rest import *

endpoint = os.environ['ENDPOINT']
api_key = os.environ['API_KEY']

client = WebPubSubServiceClient(endpoint, credential=AzureKeyCredential(api_key))

# Send message to everybody...
request = prepare_send_to_all('skalman', 'Hello, all!')
response = client.send_request(request)
response.raise_for_status()
print(response)

# Add a user to a group
request = prepare_add_user_to_group('skalman', group='someGroup', user_id='me')
response = client.send_request(request)
response.raise_for_status()
print(response)

# Add a connection to a group
request = prepare_add_connection_to_group(hub='skalman', group='thegroup', connection_id='`7')
response = client.send_request(request)
print(response)

# Check if a group exists
request = prepare_check_group_existence('skalman', group='missing')
response = client.send_request(request)
print(response)

