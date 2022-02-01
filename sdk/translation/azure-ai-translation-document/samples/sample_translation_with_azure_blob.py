# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_translation_with_azure_blob.py

DESCRIPTION:
    This sample demonstrates how to use Azure Blob Storage to set up the necessary resources to translate
    documents. Run the sample to create containers, upload documents, and generate SAS tokens for the source/target
    containers. Once the operation is completed, use the storage library to download your documents locally.

PREREQUISITE:
    This sample requires you install azure-storage-blob client library:
    https://pypi.org/project/azure-storage-blob/

USAGE:
    python sample_translation_with_azure_blob.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_DOCUMENT_TRANSLATION_ENDPOINT - the endpoint to your Document Translation resource.
    2) AZURE_DOCUMENT_TRANSLATION_KEY - your Document Translation API key.
    3) AZURE_STORAGE_SOURCE_ENDPOINT - the endpoint to your Storage account
    4) AZURE_STORAGE_ACCOUNT_NAME - the name of your storage account
    5) AZURE_STORAGE_SOURCE_KEY - the shared access key to your storage account

    Optional environment variables - if not set, they will be created for you
    6) AZURE_STORAGE_SOURCE_CONTAINER_NAME - the name of your source container
    7) AZURE_STORAGE_TARGET_CONTAINER_NAME - the name of your target container
    8) AZURE_DOCUMENT_NAME - the name and file extension of your document in this directory
        e.g. "document.txt"
"""

import os
import datetime
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceExistsError
from azure.ai.translation.document import DocumentTranslationClient
from azure.storage.blob import BlobServiceClient, BlobClient, generate_container_sas


class SampleTranslationWithAzureBlob:

    def __init__(self):
        self.endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
        self.key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]
        self.storage_endpoint = os.environ["AZURE_STORAGE_SOURCE_ENDPOINT"]
        self.storage_account_name = os.environ["AZURE_STORAGE_ACCOUNT_NAME"]
        self.storage_key = os.environ["AZURE_STORAGE_SOURCE_KEY"]
        self.storage_source_container_name = os.getenv("AZURE_STORAGE_SOURCE_CONTAINER_NAME", None)  # Optional
        self.storage_target_container_name = os.getenv("AZURE_STORAGE_TARGET_CONTAINER_NAME", None)  # Optional
        self.document_name = os.getenv("AZURE_DOCUMENT_NAME", None)  # Optional document in same directory as this sample

    def sample_translation_with_azure_blob(self):

        translation_client = DocumentTranslationClient(
            self.endpoint, AzureKeyCredential(self.key)
        )

        blob_service_client = BlobServiceClient(
            self.storage_endpoint,
            credential=self.storage_key
        )

        source_container = self.create_container(
            blob_service_client,
            container_name=self.storage_source_container_name or "translation-source-container",
        )
        target_container = self.create_container(
            blob_service_client,
            container_name=self.storage_target_container_name or "translation-target-container"
        )

        if self.document_name:
            with open(self.document_name, "rb") as doc:
                source_container.upload_blob(self.document_name, doc)
        else:
            self.document_name = "example_document.txt"
            source_container.upload_blob(
                name=self.document_name,
                data=b"This is an example translation with the document translation client library"
            )
        print(f"Uploaded document {self.document_name} to storage container {source_container.container_name}")

        source_container_sas_url = self.generate_sas_url(source_container, permissions="rl")
        target_container_sas_url = self.generate_sas_url(target_container, permissions="wl")

        poller = translation_client.begin_translation(source_container_sas_url, target_container_sas_url, "fr")
        print(f"Created translation operation with ID: {poller.id}")
        print("Waiting until translation completes...")

        result = poller.result()
        print(f"Status: {poller.status()}")

        print("\nDocument results:")
        for document in result:
            print(f"Document ID: {document.id}")
            print(f"Document status: {document.status}")
            if document.status == "Succeeded":
                print(f"Source document location: {document.source_document_url}")
                print(f"Translated document location: {document.translated_document_url}")
                print(f"Translated to language: {document.translated_to}\n")

                blob_client = BlobClient.from_blob_url(document.translated_document_url, credential=self.storage_key)
                with open("translated_"+self.document_name, "wb") as my_blob:
                    download_stream = blob_client.download_blob()
                    my_blob.write(download_stream.readall())

                print("Downloaded {} locally".format("translated_"+self.document_name))
            else:
                print("\nThere was a problem translating your document.")
                print(f"Document Error Code: {document.error.code}, Message: {document.error.message}\n")

    def create_container(self, blob_service_client, container_name):
        try:
            container_client = blob_service_client.create_container(container_name)
            print(f"Creating container: {container_name}")
        except ResourceExistsError:
            print(f"The container with name {container_name} already exists")
            container_client = blob_service_client.get_container_client(container=container_name)
        return container_client

    def generate_sas_url(self, container, permissions):
        sas_token = generate_container_sas(
            account_name=self.storage_account_name,
            container_name=container.container_name,
            account_key=self.storage_key,
            permission=permissions,
            expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        )

        container_sas_url = self.storage_endpoint + container.container_name + "?" + sas_token
        print(f"Generating {container.container_name} SAS URL")
        return container_sas_url


if __name__ == '__main__':
    sample = SampleTranslationWithAzureBlob()
    sample.sample_translation_with_azure_blob()
