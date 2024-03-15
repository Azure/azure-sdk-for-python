# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import requests
import os
import pathlib
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

def get_registry_model_details_for_non_azure_accounts(asset_id, bearer_token):
    url = "https://eastus.api.azureml.ms/modelregistry/v1.0/registry/models/nonazureaccount"

    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    params = {
        "assetId": asset_id
    }

    try:
        response = requests.get(url, headers=headers, params=params)
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
            if not os.path.exists(destinationFolder):
                os.makedirs(destinationFolder)
            
            local_file_path = os.path.join(local_folder, blob_prop.name)
            blob_client = container_client.get_blob_client(blob_prop.name)
            with open(local_file_path, "wb") as local_file:
                download_stream = blob_client.download_blob()
                local_file.write(download_stream.readall())
            print(f"Blob '{blob_prop.name}' copied to '{local_file_path}' successfully.")
        return local_folder
    except Exception as e:
        print(f"Error copying blob to local folder: {e}")
        return None

def download_model(model_asset_id, github_auth_token, local_destination_path):
    try:
        model_entity, blob_sas_uri = get_registry_model_details_for_non_azure_accounts(model_asset_id, github_auth_token)
        if model_entity and blob_sas_uri:
            print(f"Model Entity: {model_entity} \n")
            print(f"Blob SAS URI: {blob_sas_uri} \n")
        else:
            print("Failed to fetch model details.")            
        
        copied_file_path = download_blob_to_local(blob_sas_uri, local_destination_path)
        if copied_file_path:
            print(f"The blob has been downloaded to folder: {copied_file_path}")
        else:
            print("Failed to downloaded blob.")
    except Exception as e:
        print(f"Error getting blob: {e}")
        return None