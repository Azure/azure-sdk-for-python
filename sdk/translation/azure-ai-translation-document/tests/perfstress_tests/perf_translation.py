# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import uuid
import datetime
from devtools_testutils.perfstress_tests import PerfStressTest
from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.document import DocumentTranslationClient
from azure.ai.translation.document.aio import DocumentTranslationClient as AsyncDocumentTranslationClient
from azure.storage.blob.aio import ContainerClient, BlobServiceClient
from azure.storage.blob import generate_container_sas


class Document:
    """Represents a document to be uploaded to source/target container"""

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", str(uuid.uuid4()))
        self.suffix = kwargs.get("suffix", ".txt")
        self.prefix = kwargs.get("prefix", "")
        self.data = kwargs.get("data", b"This is written in english.")

    @classmethod
    def create_docs(cls, docs_count):
        result = []
        for i in range(docs_count):
            result.append(cls())
        return result


class TranslationPerfStressTest(PerfStressTest):
    def __init__(self, arguments):
        super().__init__(arguments)

        # test related env vars
        endpoint = os.environ["TRANSLATION_DOCUMENT_TEST_ENDPOINT"]
        key = os.environ["TRANSLATION_DOCUMENT_TEST_API_KEY"]
        self.storage_name = os.environ["TRANSLATION_DOCUMENT_STORAGE_NAME"]
        self.storage_key = os.environ["TRANSLATION_DOCUMENT_STORAGE_KEY"]
        self.storage_endpoint = "https://" + self.storage_name + ".blob.core.windows.net/"
        self.source_container_name = "source-perf-" + str(uuid.uuid4())
        self.target_container_name = "target-perf-" + str(uuid.uuid4())

        self.service_client = DocumentTranslationClient(endpoint, AzureKeyCredential(key), **self._client_kwargs)
        self.async_service_client = AsyncDocumentTranslationClient(
            endpoint, AzureKeyCredential(key), **self._client_kwargs
        )

    async def create_source_container(self):
        container_client = ContainerClient(self.storage_endpoint, self.source_container_name, self.storage_key)
        async with container_client:
            await container_client.create_container()
            docs = Document.create_docs(10)
            for blob in docs:
                await container_client.upload_blob(name=blob.prefix + blob.name + blob.suffix, data=blob.data)
            return self.generate_sas_url(self.source_container_name, "rl")

    async def create_target_container(self):
        container_client = ContainerClient(self.storage_endpoint, self.target_container_name, self.storage_key)
        async with container_client:
            await container_client.create_container()

        return self.generate_sas_url(self.target_container_name, "wl")

    def generate_sas_url(self, container_name, permission):
        sas_token = generate_container_sas(
            account_name=self.storage_name,
            container_name=container_name,
            account_key=self.storage_key,
            permission=permission,
            expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=2),
        )

        container_sas_url = self.storage_endpoint + container_name + "?" + sas_token
        return container_sas_url

    async def global_setup(self):
        """The global setup is run only once."""
        self.source_container_sas_url = await self.create_source_container()
        self.target_container_sas_url = await self.create_target_container()
        poller = await self.async_service_client.begin_translation(
            self.source_container_sas_url, self.target_container_sas_url, "fr"
        )
        self.translation_id = poller.id

    async def global_cleanup(self):
        """The global cleanup is run only once."""
        blob_service_client = BlobServiceClient(self.storage_endpoint, self.storage_key)
        async with blob_service_client:
            await blob_service_client.delete_container(self.source_container_name)
            await blob_service_client.delete_container(self.target_container_name)

    async def close(self):
        """This is run after cleanup."""
        await self.async_service_client.close()
        self.service_client.close()
        await super().close()

    def run_sync(self):
        """The synchronous perf test."""
        statuses = self.service_client.list_document_statuses(self.translation_id)
        for doc in statuses:
            pass

    async def run_async(self):
        """The asynchronous perf test."""
        statuses = self.async_service_client.list_document_statuses(self.translation_id)
        async for doc in statuses:
            pass
