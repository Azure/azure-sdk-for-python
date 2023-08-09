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

from azure.purview.workflow import PurviewWorkflowClient
from azure.identity import UsernamePasswordCredential
from azure.core.exceptions import HttpResponseError

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger()

# Set the value of the endpoint as environment variables:
# WORKFLOW_ENDPOINT
# Set the values of client ID and tenant ID of the AAD application as environment variables:
# AZURE_CLIENT_ID, AZURE_TENANT_ID
# set the values of username and password of the AAD user as environment variables:
# USERNAME, PASSWORD
try:
    endpoint = str(os.getenv("WORKFLOW_ENDPOINT"))
    client_id = str(os.getenv("AZURE_CLIENT_ID"))
    tenant_id = str(os.getenv("AZURE_TENANT_ID"))
    username = str(os.getenv("USERNAME"))
    password = str(os.getenv("PASSWORD"))
except KeyError:
    LOG.error(
        "Missing environment variable 'WORKFLOW_ENDPOINT' or 'AZURE_CLIENT_ID' or 'AZURE_TENANT_ID' or 'USERNAME' or "
        "'PASSWORD' - please set if before running the example")
    exit()

credential = UsernamePasswordCredential(client_id=client_id, username=username, password=password,
                                        tenant_id=tenant_id)
# Build a client through AAD
client = PurviewWorkflowClient(endpoint=endpoint, credential=credential)

try:
    user_requests_payload = {
        "operations": [
            {
                "type": "CreateTerm",
                "payload": {
                    "glossaryTerm": {
                        "name": "term",
                        "anchor": {
                            "glossaryGuid": "5dae5e5b-5aa6-48f1-9e46-26fe7328de71"
                        },
                        "status": "Approved",
                        "nickName": "term"
                    }
                }
            }
        ],
        "comment": "Thanks!"
    }
    result = client.submit_user_requests(user_requests_payload)
    print(result)
except HttpResponseError as e:
    print(f"Failed to send JSON message: {e}")
