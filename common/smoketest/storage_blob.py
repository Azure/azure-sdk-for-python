# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import uuid
from azure.storage.blob import BlobClient
from azure.core import exceptions


class StorageBlob:
    def __init__(self):
        id = uuid.uuid1()

        connectionString = os.environ["STORAGE_CONNECTION_STRING"]
        self.blob = BlobClient.from_connection_string(
            conn_str=connectionString,
            container_name="mycontainer",
            blob_name="pyTestBlob-" + id.hex + ".txt",
        )

    def upload_blob(self):
        print("uploading blob...")
        self.data = "This is a sample data for Python Test"
        self.blob.upload_blob(self.data)
        print("\tdone")

    def download_blob(self):
        print("downloading blob...")
        with open("./downloadedBlob.txt", "wb") as my_blob:
            blob_data = self.blob.download_blob()
            blob_data.readinto(my_blob)

        print("\tdone")

    def delete_blob(self):
        print("Cleaning up the resource...")
        self.blob.delete_blob()
        print("\tdone")

    def run(self):
        print("")
        print("------------------------")
        print("Storage - Blob")
        print("------------------------")
        print("1) Upload a Blob")
        print("2) Download a Blob")
        print("3) Delete that Blob (Clean up the resource)")
        print("")

        # Ensure that the blob does not exists before the tests
        try:
            self.delete_blob()
        except exceptions.AzureError:
            pass

        try:
            self.upload_blob()
            self.download_blob()
        finally:
            self.delete_blob()
