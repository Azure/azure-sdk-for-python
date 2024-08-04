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
"""
FILE: create_client_sample.py

DESCRIPTION:
    This sample demonstrates how to create a Dev Center client. For this sample, you must 
    have previously configured a Dev Center in Azure. More details on how to configure it at 
    https://learn.microsoft.com/azure/deployment-environments/quickstart-create-and-configure-devcenter#create-a-dev-center

USAGE:
    python create_client_sample.py

    Set the environment variables with your own values before running the sample:
    1) DEVCENTER_ENDPOINT - the endpoint for your devcenter
"""

def create_dev_center_client():
    # [START create_dev_center_client]
    import os

    from azure.developer.devcenter import DevCenterClient
    from azure.identity import DefaultAzureCredential

    # Set the values of the dev center endpoint, client ID, and client secret of the AAD application as environment variables:
    # DEVCENTER_ENDPOINT, AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET
    try:
        endpoint = os.environ["DEVCENTER_ENDPOINT"]
    except KeyError:
        raise ValueError("Missing environment variable 'DEVCENTER_ENDPOINT' - please set it before running the example")

    # Build a client through AAD
    client = DevCenterClient(endpoint, credential=DefaultAzureCredential())
    # [END create_dev_center_client]

if __name__ == "__main__":
    create_dev_center_client()
