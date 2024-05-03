# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import requests
from azure.storage.blob import ContainerClient
from azure.core.exceptions import ResourceNotFoundError, ServiceResponseError

def get_registry_model_details(asset_id, bearer_token):
    url = "https://eastus.api.azureml.ms/modelregistry/v1.0/registry/models/nonazureaccount"

    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    params = {
        "assetId": asset_id
    }
    timeout = 5

    try:
        response = requests.get(url, headers=headers, params=params, timeout=timeout)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        model_entity = data.get("modelEntity")
        blob_sas_uri = data.get("blobSasUri")
        return model_entity, blob_sas_uri
    except requests.exceptions.RequestException as e:
        print(f"Error accessing API: {e}")
        return None, None

def download_blob_to_local(blob_sas_url, local_folder):
    try:
        # Create local folder if it doesn't exist
        if not os.path.exists(local_folder):
            os.makedirs(local_folder)

        container_client = ContainerClient.from_container_url(blob_sas_url)
        blob_list = container_client.list_blobs()
        for blob_prop in blob_list:
            blobDirectory = os.path.dirname(blob_prop.name)
            blobFileName = os.path.basename(blob_prop.name)
            destinationFolder = os.path.join(local_folder, blobDirectory)
            print(f"blobDirectory: {blobDirectory}, blobFileName: {blobFileName}")
            if not os.path.exists(destinationFolder):
                os.makedirs(destinationFolder)

            local_file_path = os.path.join(local_folder, blob_prop.name)
            blob_client = container_client.get_blob_client(blob_prop.name)
            with open(local_file_path, "wb") as local_file:
                download_stream = blob_client.download_blob()
                local_file.write(download_stream.readall())
            print(f"Blob '{blob_prop.name}' copied to '{local_file_path}' successfully.")
    except ResourceNotFoundError as e:
        print(f"Resource not found: {e}")
    except ServiceResponseError as e:
        print(f"Service response error: {e}")

# sample parameters
# modelAssetId = "azureml://registries/testFeed/models/testModel/versions/13"
# localDestinationPath = "C:\\PythonVirtualEnv\\venv1\\BlobDownLoad"
# gitHubAuthToken = "ghu_xxxxxxxxxxxxx"
def download_model(model_asset_id, github_auth_token, local_destination_path):
    model_entity, blob_sas_uri = get_registry_model_details(model_asset_id, github_auth_token)
    if model_entity and blob_sas_uri:
        print(f"Model Entity: {model_entity} \n")
        print(f"Blob SAS URI: {blob_sas_uri} \n")
    else:
        print("Failed to fetch model details.")

    download_blob_to_local(blob_sas_uri, local_destination_path)
    print(f"The blob has been downloaded to folder: {local_destination_path}")
