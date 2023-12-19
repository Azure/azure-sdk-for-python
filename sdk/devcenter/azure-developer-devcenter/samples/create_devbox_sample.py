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

from azure.developer.devcenter import DevCenterClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError

"""
FILE: create_devbox_sample.py

DESCRIPTION:
    This sample demonstrates how to create, connect and delete a dev box using python DevCenterClient. For this sample,
    you must have previously configured DevCenter, Project, Network Connection, Dev Box Definition, and Pool.More details 
    on how to configure those requirements at https://learn.microsoft.com/azure/dev-box/quickstart-configure-dev-box-service


USAGE:
    python create_devbox_sample.py

    Set the environment variables with your own values before running the sample:
    1) DEVCENTER_ENDPOINT - the endpoint for your devcenter
"""

def get_project_name(LOG, client):
    projects = list(client.projects.list_by_dev_center(top=1))
    return projects[0].name


def main():

    # Set the values of the dev center endpoint, client ID, and client secret of the AAD application as environment variables:
    # DEVCENTER_ENDPOINT, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET
    try:
        endpoint = os.environ["DEVCENTER_ENDPOINT"]
    except KeyError:
        raise ValueError("Missing environment variable 'DEVCENTER_ENDPOINT' - please set it before running the example")

    # Build a client through AAD
    client = DevCenterClient(endpoint, credential=DefaultAzureCredential())

    # Fetch control plane resource dependencies
    projects = list(client.list_projects(top=1))
    target_project_name = projects[0]["name"]

    pools = list(client.list_pools(target_project_name, top=1))
    target_pool_name = pools[0]["name"]

    # Stand up a new dev box
    create_response = client.begin_create_dev_box(
        target_project_name, "me", "Test_DevBox", {"poolName": target_pool_name}
    )
    devbox_result = create_response.result()

    print(f"Provisioned dev box with status {devbox_result['provisioningState']}.")

    # Connect to the provisioned dev box
    remote_connection_response = client.get_remote_connection(target_project_name, "me", "Test_DevBox")
    print(f"Connect to the dev box using web URL {remote_connection_response['webUrl']}")

    # Tear down the dev box when finished
    delete_response = client.begin_delete_dev_box(target_project_name, "me", "Test_DevBox")
    delete_response.wait()
    print("Deleted dev box successfully.")


if __name__ == "__main__":
    main()
