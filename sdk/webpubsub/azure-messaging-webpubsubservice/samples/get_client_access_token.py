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
import logging
import os

from azure.messaging.webpubsubservice import WebPubSubServiceClient
from azure.identity import DefaultAzureCredential

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger()

# Set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:
# AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, WEBPUBSUB_ENDPOINT, WEBPUBSUB_CONNECTION_STRING
try:
    endpoint = os.environ["WEBPUBSUB_ENDPOINT"]
    connection_string = os.environ['WEBPUBSUB_CONNECTION_STRING']
except KeyError:
    LOG.error("Missing environment variable 'WEBPUBSUB_ENDPOINT' or 'WEBPUBSUB_CONNECTION_STRING' - please set if before running the example")
    exit()

# Build a client through AAD
client_aad = WebPubSubServiceClient(endpoint=endpoint, hub='hub', credential=DefaultAzureCredential())

# Build authentication token
token_aad = client_aad.get_client_access_token()
print('token by AAD: {}'.format(token_aad))

# Build a client through connection string
client_key = WebPubSubServiceClient.from_connection_string(connection_string, hub='hub')

# Build authentication token
token_key = client_key.get_client_access_token()
print('token by access key: {}'.format(token_key))
