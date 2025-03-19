
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the datasets methods
    to upload files, create datasets that reference those files, list datasets
    and delete datasets.

USAGE:
    python sample_datasets.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set this environment variables with your own values:
    * PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the overview page of your
      Azure AI Foundry project.
"""

import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects.dp1 import AIProjectClient
from azure.ai.projects.dp1.models import DatasetVersion, ListViewType

project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

dataset_name = "my-dataset-name"

# Upload a single file and create a new dataset to reference the file
dataset: DatasetVersion = project_client.datasets.create_and_upload_file(
    name=dataset_name,
    version="1.0",
    file="sample_folder/file1.txt",
)
print(dataset)

# Upload all files in a folder (including all subfolders) and create a new dataset version to reference the folder
dataset = project_client.datasets.create_and_upload_folder(
    name=dataset_name,
    version="2.0",
    folder="sample_folder",
)
print(dataset)

# Get an existing dataset version
dataset = project_client.datasets.get_version(name=dataset_name, version="1.0")
print(dataset)

# List all versions of a particular dataset
for dataset in project_client.datasets.list_dataset_versions(name=dataset_name, list_view_type=ListViewType.ALL):
    print(dataset)

# List latest versions of all datasets
for dataset in project_client.datasets.list_latest_datasets(list_view_type=ListViewType.ALL):
    print(dataset)

# Clean up
project_client.datasets.delete_version(name=dataset_name, version="1.0")
project_client.datasets.delete_version(name=dataset_name, version="2.0")


