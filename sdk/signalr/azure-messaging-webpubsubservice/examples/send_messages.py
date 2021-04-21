import io
import logging
import os

from azure.core.credentials import AzureKeyCredential
from azure.messaging.webpubsubservice import WebPubSubServiceClient
from azure.messaging.webpubsubservice.rest import *

endpoint = os.environ['ENDPOINT']
api_key = os.environ['API_KEY']

LOG = logging.basicConfig(level=logging.DEBUG)

client = WebPubSubServiceClient(endpoint, credential=AzureKeyCredential(api_key), tracing_enabled=True)

# Send message to everybody on the given hub...
request = build_send_to_all_request('ahub', json={ 'Hello': 'all!' })
response = client.send_request(request)
try:
    response.raise_for_status()
    print('Successfully sent a message')
except:
    print('Failed to send message: {}'.format(response))


request = build_send_to_all_request('ahub', content='hello, text!', content_type='text/plain')
print(request.headers.items())
response = client.send_request(request)
print(response)


request = build_send_to_all_request('ahub', content=io.BytesIO(b'{ "hello": "world" }'), content_type='application/json')
response = client.send_request(request)
print(response)

# Add a user to a group
request = build_add_user_to_group_request('ahub', group='someGroup', user_id='me')
response = client.send_request(request)
try:
    response.raise_for_status()
except:
    print('Failed to add user to group: {}'.format(response))

request = build_user_exists_in_group_request('ahub', 'someGroup', 'me')
response = client.send_request(request)

request = build_add_connection_to_group_request('ahub', 'someGroup', '7')
response = client.send_request(request)
print(response.content)

# Add a connection to a group
request = build_add_connection_to_group_request(hub='ahub', group='someGroup', connection_id='7')
response = client.send_request(request)
print(response)

# Check if a group exists
request = build_connection_exists_request(hub='ahub', connection_id='missing')
response = client.send_request(request)
if response.status_code == 404:
    print("no such group")
else:
    print('The group exists!')


request = build_grant_permission_request('ahub', 'sendToGroup', '7')
response = client.send_request(request)
print(response.content)