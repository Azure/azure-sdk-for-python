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
FILE: deployment_environments_sample.py

DESCRIPTION:
    This sample demonstrates how to create and delete Environments using python DevCenterClient. For this sample,
    you must have previously configured a DevCenter, Project, Catalog, Environment Definition and Environment Type. 
    More details   on how to configure those requirements at https://learn.microsoft.com/azure/deployment-environments/

USAGE:
    python deployment_environments_sample.py

    Set the environment variables with your own values before running the sample:
    1) DEVCENTER_ENDPOINT - the endpoint for your devcenter
"""

def environment_create_and_delete():
    # [START environment_create_and_delete]
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

    # List available Catalogs
    catalogs = client.list_catalogs(target_project_name)
    if catalogs:
        print("\nList of catalogs: ")
        for catalog in catalogs:
            print(f"{catalog.name}")

        # Select first catalog in the list
        target_catalog_name = list(catalogs)[0].name
    else:
        raise ValueError("Missing Catalog - please create one before running the example")

    # List available Environment Definitions
    environment_definitions = client.list_environment_definitions_by_catalog(target_project_name, target_catalog_name)
    if environment_definitions:
        print("\nList of environment definitions: ")
        for environment_definition in environment_definitions:
            print(f"{environment_definition.name}")

        # Select first environment definition in the list
        target_environment_definition_name = list(environment_definitions)[0].name
    else:
        raise ValueError("Missing Environment Definition - please create one before running the example")

    # List available Environment Types
    environment_types = client.list_environment_types(target_project_name)
    if environment_types:
        print("\nList of environment types: ")
        for environment_type in environment_types:
            print(f"{environment_type.name}")

        # Select first environment type in the list
        target_environment_type_name = list(environment_types)[0].name
    else:
        raise ValueError("Missing Environment Type - please create one before running the example")

    print(
        f"\nStarting to create environment in project {target_project_name} with catalog {target_catalog_name}, environment definition {target_environment_definition_name}, and environment type {target_environment_type_name}."
    )

    # Stand up a new environment
    environment_name = "MyDevEnv"
    environment = {
        "environmentType": target_environment_type_name,
        "catalogName": target_catalog_name,
        "environmentDefinitionName": target_environment_definition_name,
    }

    environment_poller = client.begin_create_or_update_environment(
        target_project_name, "me", environment_name, environment
    )
    environment_result = environment_poller.result()
    print(f"Provisioned environment with status {environment_result.provisioning_state}.")

    # Tear down the environment when finished
    print(f"Starting to delete environment.")
    delete_poller = client.begin_delete_environment(target_project_name, "me", environment_name)
    delete_result = delete_poller.result()
    print(f"Completed deletion for the environment with status {delete_result.status}")
    # [END environment_create_and_delete]


if __name__ == "__main__":
    environment_create_and_delete()
