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

def main():
    logging.basicConfig(level=logging.DEBUG)
    LOG = logging.getLogger()

    # Set the values of the dev center endpoint, client ID, and client secret of the AAD application as environment variables:
    # DEVCENTER_ENDPOINT, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET
    try:
        endpoint = os.environ["DEVCENTER_ENDPOINT"]
    except KeyError:
        LOG.error("Missing environment variable 'DEVCENTER_ENDPOINT' - please set it before running the example")
        exit()

    # Build a client through AAD
    client = DevCenterClient(endpoint, credential=DefaultAzureCredential())

    # Fetch control plane resource dependencies
    target_project_name = list(client.dev_center.list_projects(top=1))[0]['name']
    target_catalog_item_name = list(client.environments.list_catalog_items(target_project_name, top=1))[0]['name']
    target_environment_type_name = list(client.environments.list_environment_types(target_project_name, top=1))[0]['name']

    # Stand up a new environment
    create_response = client.environments.begin_create_environment(target_project_name,
                                                       "Dev_Environment",
                                                       {"catalogItemName": target_catalog_item_name, "environmentType": target_environment_type_name})
    environment_result = create_response.result()

    LOG.info(f"Provisioned environment with status {environment_result['provisioningState']}.")

    # Tear down the environment when finished
    delete_response = client.environments.begin_delete_environment(target_project_name, "Dev_Environment")
    delete_response.wait()
    LOG.info("Completed deletion for the environment.")


if __name__ == "__main__":
    main()