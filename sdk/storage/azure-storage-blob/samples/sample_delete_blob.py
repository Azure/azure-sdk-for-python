from azure.storage.blob import BlobServiceClient, ContainerClient
import os


SOURCE_FOLDER = "./sample-blobs/"

def batch_delete_blobs_sample(local_path):
	# Set the connection string and container name values to initialize the Container Client
    connection_string = os.getenv('STORAGE_CONN_STR')

    blob_service_client = BlobServiceClient.from_connection_string(conn_str=connection_string)
	# Create a ContainerClient to use the batch_delete function on a Blob Container
    container_client = blob_service_client.get_container_client("mycontainername")

	# Upload blobs
    for filename in os.listdir(local_path):
        with open(local_path+filename, "rb") as data:
            container_client.upload_blob(name=filename, data=data, blob_type="BlockBlob")

	# List blobs in storage account
    blob_list = [b.name for b in list(container_client.list_blobs())]

	# Delete blobs
    container_client.delete_blobs(*blob_list)

batch_delete_blobs_sample(SOURCE_FOLDER)
