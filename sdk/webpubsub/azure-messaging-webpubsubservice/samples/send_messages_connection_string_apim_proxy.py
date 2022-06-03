# coding=utf-8
# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
import io
import logging
import os

from azure.messaging.webpubsubservice import WebPubSubServiceClient
from azure.core.exceptions import HttpResponseError

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger()

try:
    connection_string = os.environ['WEBPUBSUB_CONNECTION_STRING']
    reverse_proxy_endpoint = os.environ["WEBPUBSUB_REVERSE_PROXY_ENDPOINT"]
except KeyError:
    LOG.error("Missing environment variable 'WEBPUBSUB_CONNECTION_STRING' or 'WEBPUBSUB_REVERSE_PROXY_ENDPOINT' - please set if before running the example")
    exit()

# Build a client from the connection string. And for this example, we have enabled debug
# tracing. For production code, this should be turned off.
# If you want to know more about the effect of `reverse_proxy_endpoint`, please reference: https://github.com/Azure/azure-webpubsub/issues/194
client = WebPubSubServiceClient.from_connection_string(connection_string, hub='hub', logging_enable=True, reverse_proxy_endpoint=reverse_proxy_endpoint)

try:
    # Raise an exception if the service rejected the call
    client.send_to_all(message={'Hello': 'connection_string_reverse_proxy!'})
    print('Successfully sent a JSON message')
except HttpResponseError as e:
    print('Failed to send JSON message: {}'.format(e.response.json()))

# # Send a text message to everybody on the given hub...
# try:
#     # Raise an exception if the service rejected the call
#     client.send_to_all(message='hello, connection_string_reverse_proxy!', content_type='text/plain')
#     print('Successfully sent a JSON message')
# except HttpResponseError as e:
#     print('Failed to send JSON message: {}'.format(e.response.json()))
#
#
# # Send a json message from a stream to everybody on the given hub...
# try:
#     # Raise an exception if the service rejected the call
#     client.send_to_all(message=io.BytesIO(b'{ "hello": "connection_string_reverse_proxy" }'), content_type='application/octet-stream')
#     print('Successfully sent a JSON message')
# except HttpResponseError as e:
#     print('Failed to send JSON message: {}'.format(e.response.json()))

