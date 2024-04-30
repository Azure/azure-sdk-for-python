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
FILE: dev_box_create_sample.py

DESCRIPTION:
    This sample demonstrates how to create, connect and delete a dev box using python DevCenterClient. For this sample,
    you must have previously configured DevCenter, Project, Network Connection, Dev Box Definition, and Pool.More details 
    on how to configure those requirements at https://learn.microsoft.com/azure/dev-box/quickstart-configure-dev-box-service


USAGE:
    python dev_box_create_sample.py

    Set the environment variables with your own values before running the sample:
    1) DEVCENTER_ENDPOINT - the endpoint for your devcenter
"""

def dev_box_create_connect_delete():
    # [START dev_box_create_connect_delete]
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

    # List available Projects
    projects = client.list_projects()
    if projects:
        print("\nList of projects: ")
        for project in projects:
            print(f"{project.name}")

        # Select first project in the list
        target_project_name = list(projects)[0].name
    else:
        raise ValueError("Missing Project - please create one before running the example")

    # List available Pools
    pools = client.list_pools(target_pool_name)
    if pools:
        print("\nList of pools: ")
        for pool in pools:
            print(f"{pool.name}")

        # Select first pool in the list
        target_pool_name = list(pools)[0].name
    else:
        raise ValueError("Missing Pool - please create one before running the example")

    # Stand up a new Dev Box
    print(f"\nStarting to create dev box in project {target_project_name} and pool {target_pool_name}")

    dev_box_poller = client.begin_create_dev_box(
        target_project_name, "me", "Test_DevBox", {"poolName": target_pool_name}
    )
    dev_box = dev_box_poller.result()
    print(f"Provisioned dev box with status {dev_box.provisioning_state}.")

    # Connect to the provisioned Dev Box
    remote_connection = client.get_remote_connection(target_project_name, "me", dev_box.name)
    print(f"Connect to the dev box using web URL {remote_connection.web_url}")

    # Tear down the Dev Box when finished
    print(f"Starting to delete dev box.")

    delete_poller = client.begin_delete_dev_box(target_project_name, "me", "Test_DevBox")
    delete_result = delete_poller.result()
    print(f"Completed deletion for the dev box with status {delete_result.status}")
    # [END dev_box_create_connect_delete]

if __name__ == "__main__":
    dev_box_create_connect_delete()
