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
from azure.ai.projects.dp1.models import ListViewType

endpoint = os.environ["PROJECT_ENDPOINT"]
index_name = os.environ["INDEX_NAME"]

project_client = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
)

"""
    def list_versions(
        self,
        name: str,
        *,
        top: Optional[int] = None,
        skip: Optional[str] = None,
        tags: Optional[str] = None,
        list_view_type: Optional[Union[str, _models.ListViewType]] = None,
        **kwargs: Any
    ) -> Iterable["_models.Index"]:

    def list_latest(
        self,
        *,
        top: Optional[int] = None,
        skip: Optional[str] = None,
        tags: Optional[str] = None,
        list_view_type: Optional[Union[str, _models.ListViewType]] = None,
        **kwargs: Any
    ) -> Iterable["_models.Index"]:

    def get_version(self, name: str, version: str, **kwargs: Any) -> _models.Index:
    
    def delete_version(  # pylint: disable=inconsistent-return-statements
        self, name: str, version: str, **kwargs: Any
    ) -> None:

    def create(
        self, name: str, body: _models.Index, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.Index:

    def create_version(
        self, name: str, version: str, body: _models.Index, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.Index:
"""

""" Do we need equivalent of these for Indexes?

print("Upload a single file and create a new dataset to reference the file:")
dataset: DatasetVersion = project_client.datasets.upload_file_and_create_version(
    name=dataset_name,
    version="1.0",
    file="sample_folder/file1.txt",
)
print(dataset)


print("Upload all files in a folder (including subfolders) and create a new dataset version to reference the folder:")
dataset = project_client.datasets.upload_folder_and_create_version(
    name=dataset_name,
    version="2.0",
    folder="sample_folder",
)
print(dataset)
"""


print("Get an existing Index version `1.0`:")
index = project_client.indexes.get_version(name=index_name, version="1.0")
print(index)


print(f"Listing all versions of the Index named `{index_name}`:")
for index in project_client.indexes.list_versions(name=index_name, list_view_type=ListViewType.ALL):
    print(index)


print("List latest versions of all Indexes:")
for index in project_client.indexes.list_latest(list_view_type=ListViewType.ALL):
    print(index)


print("Delete the Index versions created above:")
project_client.indexes.delete_version(name=index_name, version="1.0")
project_client.indexes.delete_version(name=index_name, version="2.0")
