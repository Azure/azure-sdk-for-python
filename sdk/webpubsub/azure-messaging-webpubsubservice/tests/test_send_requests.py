import io

from azure.messaging.webpubsubservice import WebPubSubServiceClient
from azure.messaging.webpubsubservice.rest import *

from azure.core.credentials import AzureKeyCredential

def test_build_text_request():
    request = build_send_to_all_request('hub', content='hello world', content_type='text/plain')

    assert request.headers['content-type'] == 'text/plain'
    assert request.content == 'hello world'

def test_build_json_request():
    client = WebPubSubServiceClient('https://www.microsoft.com/api', AzureKeyCredential('abcd'))
    request = build_send_to_all_request('hub', json={'hello': 'world'})
    assert request.headers['content-type'] == 'application/json'

def test_build_stream_request():
    stream = io.BytesIO(b'1234')
    client = WebPubSubServiceClient('https://www.microsoft.com/api', AzureKeyCredential('abcd'))
    request = build_send_to_all_request('hub', content=stream, content_type='application/octet-stream')
    assert request.headers['content-type'] == 'application/octet-stream'

def test_build_stream_json_request():
    stream = io.BytesIO(b'{ "hello": "web" }')
    client = WebPubSubServiceClient('https://www.microsoft.com/api', AzureKeyCredential('abcd'))
    request = build_send_to_all_request('hub', content=stream, content_type='application/octet-json')
    assert request.headers['content-type'] == 'application/octet-json'

def test_build_send_message_exclude():
    stream = io.BytesIO(b'{ "hello": "web" }')
    client = WebPubSubServiceClient('https://www.microsoft.com/api', AzureKeyCredential('abcd'))
    request = build_send_to_all_request('hub', content=stream, content_type='application/octet-json', excluded=['a', 'b', 'c'])
    assert 'excluded=a&' in request.url
    assert 'excluded=b&' in request.url
    assert 'excluded=c' in request.url
    assert 'excluded=d' not in request.url
