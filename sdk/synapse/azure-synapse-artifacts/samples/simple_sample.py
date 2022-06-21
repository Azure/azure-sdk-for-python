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

from azure.synapse.artifacts import ArtifactsClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger()

# Set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:
# AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, SYNAPSE_ARTIFACTS_ENDPOINT
try:
    endpoint = os.environ["SYNAPSE_ARTIFACTS_ENDPOINT"]
except KeyError:
    LOG.error("Missing environment variable 'SYNAPSE_ARTIFACTS_ENDPOINT' - please set if before running the example")
    exit()

# Build a client through AAD
client = ArtifactsClient(endpoint=endpoint, credential=DefaultAzureCredential())

try:
    linked_service = client.linked_service.get_linked_service(linked_service_name='my_linked_service_name')
except HttpResponseError as e:
    print('Failed to get linked service: {}'.format(e.response.json()))
