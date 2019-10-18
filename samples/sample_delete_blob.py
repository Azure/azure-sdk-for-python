from azure.storage.blob import BlobServiceClient, ContainerClient
import os

def batch_delete_blobs_sample(local_path): 
	# Set the connection string and container name values to initialize the Container Client
	connection_string = os.getenv('STORAGE_CONN_STR')
	container_name = os.getenv('STORAGE_CONTAINER_NAME')

	blob_service_client = BlobServiceClient.from_connection_string(conn_str=connection_string)
	# Create a ContainerClient to use the batch_delete function on a Blob Container
	container_client = blob_service_client.get_container_client(container_name)

	# Upload blobs
	for filename in os.listdir(local_path):
		with open(local_path+filename, "rb") as data:
			container_client.upload_blob(name=filename, data=data, blob_type="BlockBlob")

	# List blobs in storage account
	blob_list = list(container_client.list_blobs())

	# Delete blobs
	blobs_to_delete = os.listdir(local_path)
	container_client.delete_blobs(*blobs_to_delete)

	# List blobs in storage account
	blob_list = list(container_client.list_blobs())

batch_delete_blobs_sample("./sample-blobs/")