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

# TODO: Remove console logging
import sys
import logging

logger = logging.getLogger("azure")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))
# End logging


import os
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from azure.ai.projects.onedp import AIProjectClient

endpoint = os.environ["PROJECT_ENDPOINT"]
index_name = os.environ["INDEX_NAME"]

with AIProjectClient(
    endpoint=endpoint,
    # credential=DefaultAzureCredential(),
    credential=AzureKeyCredential(os.environ["PROJECT_API_KEY"]),
    logging_enable=True,  # TODO: Remove console logging
) as project_client:

    print(f"Listing all versions of the Index named `{index_name}`:")
    for index in project_client.indexes.list_versions(name=index_name):
        print(index)
    exit()

    print("Get an existing Index version `1`:")
    index = project_client.indexes.get_version(name=index_name, version="1")
    print(index)

    print("List latest versions of all Indexes:")
    for index in project_client.indexes.list_latest():
        print(index)

    print("Delete the Index versions created above:")
    project_client.indexes.delete_version(name=index_name, version="1")
    project_client.indexes.delete_version(name=index_name, version="2")
