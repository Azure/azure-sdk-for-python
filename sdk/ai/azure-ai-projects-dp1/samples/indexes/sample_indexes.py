# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `.indexes` methods to upload a file, create Indexes that reference those files,
    list Indexes and delete Indexes.

USAGE:
    python sample_indexes.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
    2) INDEX_NAME - Required. The name of an Index to create and use in this sample.
"""

import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects.dp1 import AIProjectClient

endpoint = os.environ["PROJECT_ENDPOINT"]
index_name = os.environ["INDEX_NAME"]

project_client = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
)

print("Get an existing Index version `1.0`:")
index = project_client.indexes.get_version(name=index_name, version="1.0")
print(index)


print(f"Listing all versions of the Index named `{index_name}`:")
for index in project_client.indexes.list_versions(name=index_name):
    print(index)


print("List latest versions of all Indexes:")
for index in project_client.indexes.list_latest():
    print(index)


print("Delete the Index versions created above:")
project_client.indexes.delete_version(name=index_name, version="1.0")
project_client.indexes.delete_version(name=index_name, version="2.0")
