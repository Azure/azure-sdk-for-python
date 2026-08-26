# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from types import SimpleNamespace
from typing import Any

from azure.core.credentials import AzureKeyCredential
from devtools_testutils.perfstress_tests import PerfStressTest

from azure.search.documents import SearchClient as SyncClient
from azure.search.documents._utils.model_base import SdkJSONEncoder
from azure.search.documents.aio import SearchClient as AsyncClient


class _SyncSerializationClient(SyncClient):
    def _index(
        self, batch: Any, **kwargs: Any
    ) -> Any:  # pylint: disable=unused-argument
        json.dumps(batch, cls=SdkJSONEncoder, exclude_readonly=True)
        return SimpleNamespace(results=[])


class _AsyncSerializationClient(AsyncClient):
    async def _index(
        self, batch: Any, **kwargs: Any
    ) -> Any:  # pylint: disable=unused-argument
        json.dumps(batch, cls=SdkJSONEncoder, exclude_readonly=True)
        return SimpleNamespace(results=[])


class UploadDocumentsTest(PerfStressTest):
    """Measures client-side batch construction and serialization without sending HTTP requests."""

    def __init__(self, arguments):
        super().__init__(arguments)
        credential = AzureKeyCredential("perf-test-key")
        self.service_client = _SyncSerializationClient(
            "https://localhost", "perf-index", credential
        )
        self.async_service_client = _AsyncSerializationClient(
            "https://localhost", "perf-index", credential
        )

        vector = [
            float(index % 10) / 10 for index in range(self.args.vector_dimensions)
        ]
        content = "x" * self.args.text_length
        self.documents = [
            {
                "id": str(index),
                "content": content,
                "content_vector": vector,
                "category": "performance",
                "source": "synthetic",
            }
            for index in range(self.args.num_documents)
        ]

    @staticmethod
    def add_arguments(parser):
        super(UploadDocumentsTest, UploadDocumentsTest).add_arguments(parser)
        parser.add_argument(
            "--num-documents",
            nargs="?",
            type=int,
            help="Number of documents per upload. Defaults to 100.",
            default=100,
        )
        parser.add_argument(
            "--vector-dimensions",
            nargs="?",
            type=int,
            help="Number of floats in each document vector. Defaults to 3072.",
            default=3072,
        )
        parser.add_argument(
            "--text-length",
            nargs="?",
            type=int,
            help="Number of characters in each document text field. Defaults to 4000.",
            default=4000,
        )

    async def close(self):
        self.service_client.close()
        await self.async_service_client.close()
        await super().close()

    def run_sync(self):
        self.service_client.upload_documents(self.documents)

    async def run_async(self):
        await self.async_service_client.upload_documents(self.documents)
