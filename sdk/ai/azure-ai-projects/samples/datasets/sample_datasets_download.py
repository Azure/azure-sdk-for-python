# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `.datasets` methods to upload all files in a folder (including sub-folders),
    create Dataset that reference those files, and then download the files using
    an Azure storage ContainerClient.

USAGE:
    python sample_datasets_download.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b4" python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Microsoft Foundry project.
    2) CONNECTION_NAME - Optional. The name of the Azure Storage Account connection to use for uploading files.
    3) DATASET_NAME - Optional. The name of the Dataset to create and use in this sample.
    4) DATASET_VERSION - Optional. The version of the Dataset to create and use in this sample.
    6) DATA_FOLDER - Optional. The folder path where the data files for upload are located.
    7) DOWNLOAD_FOLDER - Optional. The folder path where the downloaded files will be saved.
"""

import os
import re
import tempfile
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ConnectionType
from azure.storage.blob import ContainerClient

load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
connection_name = os.environ.get("CONNECTION_NAME")
dataset_name = os.environ.get("DATASET_NAME", "dataset-test")
dataset_version = os.environ.get("DATASET_VERSION", "1.0")
download_folder = os.environ.get("DOWNLOAD_FOLDER", os.path.join(tempfile.gettempdir(), "downloaded_blobs"))

# Construct the paths to the data folder and data file used in this sample
script_dir = os.path.dirname(os.path.abspath(__file__))
data_folder = os.environ.get("DATA_FOLDER", os.path.join(script_dir, "data_folder"))

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):

    connection_name = (
        connection_name or project_client.connections.get_default(ConnectionType.AZURE_STORAGE_ACCOUNT).name
    )

    print(
        f"Upload files in a folder (including sub-folders) and create a dataset named `{dataset_name}` version `{dataset_version}`, to reference the files."
    )
    dataset = project_client.datasets.upload_folder(
        name=dataset_name,
        version=dataset_version,
        folder=data_folder,
        connection_name=connection_name,
        file_pattern=re.compile(r"\.(txt|csv|md)$", re.IGNORECASE),
    )
    print(dataset)

    print(f"Get credentials of an existing Dataset version `{dataset_version}`:")
    dataset_credential = project_client.datasets.get_credentials(name=dataset_name, version=dataset_version)
    print(dataset_credential)

    print(f"Creating a folder `{download_folder}` for the downloaded blobs:")
    os.makedirs(download_folder, exist_ok=True)

    container_client = ContainerClient.from_container_url(
        container_url=dataset_credential.blob_reference.credential.sas_uri
    )

    print("Looping over all blobs in the container:")
    for blob_name in container_client.list_blob_names():
        blob_client = container_client.get_blob_client(blob_name)

        file_path = os.path.join(download_folder, blob_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Handle sub-folders if needed

        with open(file_path, "wb") as f:
            f.write(blob_client.download_blob().readall())

        print(f"Downloaded: {blob_name} -> {file_path}")

    print(f"All files were downloaded to: {os.path.abspath(download_folder)}")

    print("Delete the dataset created above:")
    project_client.datasets.delete(name=dataset_name, version=dataset_version)
