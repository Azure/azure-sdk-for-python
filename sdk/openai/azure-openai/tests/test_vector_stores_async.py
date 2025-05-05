# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from __future__ import annotations

import os
import pytest
import pathlib
import uuid
import openai
from devtools_testutils import AzureRecordedTestCase
from conftest import ASST_AZURE, PREVIEW, GPT_4_OPENAI, configure_async


@pytest.mark.live_test_only
class TestVectorStoresAsync(AzureRecordedTestCase):

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type, api_version", [(ASST_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")])
    async def test_vector_stores_crud(self, client_async: openai.AsyncAzureOpenAI | openai.AsyncOpenAI, api_type, api_version, **kwargs):
        file_name = f"test{uuid.uuid4()}.txt"
        with open(file_name, "w") as f:
            f.write("Contoso company policy requires that all employees take at least 10 vacation days a year.")

        path = pathlib.Path(file_name)

        file = await client_async.files.create(
            file=open(path, "rb"),
            purpose="assistants"
        )

        try:
            vector_store = await client_async.vector_stores.create(
                name="Support FAQ"
            )
            assert vector_store.name == "Support FAQ"
            assert vector_store.id
            assert vector_store.object == "vector_store"
            assert vector_store.created_at
            assert vector_store.file_counts.total == 0

            vectors = client_async.vector_stores.list()
            async for vector in vectors:
                assert vector.id
                assert vector_store.object == "vector_store"
                assert vector_store.created_at

            vector_store = await client_async.vector_stores.update(
                vector_store_id=vector_store.id,
                name="Support FAQ and more",
                metadata={"Q": "A"}
            )
            assert vector_store.name == "Support FAQ and more"
            assert vector_store.metadata == {"Q": "A"}
            retrieved_vector = await client_async.vector_stores.retrieve(
                vector_store_id=vector_store.id
            )
            assert retrieved_vector.id == vector_store.id

            vector_store_file = await client_async.vector_stores.files.create(
                vector_store_id=vector_store.id,
                file_id=file.id
            )
            assert vector_store_file.id
            assert vector_store_file.object == "vector_store.file"
            assert vector_store_file.created_at
            assert vector_store_file.vector_store_id == vector_store.id

            vector_store_files = client_async.vector_stores.files.list(
                vector_store_id=vector_store.id
            )
            async for vector_file in vector_store_files:
                assert vector_file.id
                assert vector_file.object == "vector_store.file"
                assert vector_store_file.created_at
                assert vector_store_file.vector_store_id == vector_store.id

            vector_store_file_2 = await client_async.vector_stores.files.retrieve(
                vector_store_id=vector_store.id,
                file_id=vector_store_file.id
            )
            assert vector_store_file_2.id == vector_store_file.id
            assert vector_store_file.vector_store_id == vector_store.id

            # TODO Not supported by Azure yet
            # vector_store_file_updated = await client_async.vector_stores.files.update(
            #     file_id=vector_store_file.id,
            #     vector_store_id=vector_store.id,
            #     attributes={"Q": "A"}
            # )
            # assert vector_store_file_updated.attributes == {"Q": "A"}

            # file_content = await client_async.vector_stores.files.content(
            #     vector_store_id=vector_store.id,
            #     file_id=vector_store_file.id
            # )
            # assert file_content

            # search_response = await client_async.vector_stores.search(
            #     vector_store_id=vector_store.id,
            #     query="vacation days",
            # )
            # async for s in search_response:
            #     assert s

        finally:
            os.remove(path)
            deleted_vector_store_file = await client_async.vector_stores.files.delete(
                vector_store_id=vector_store.id,
                file_id=vector_store_file.id
            )
            assert deleted_vector_store_file.deleted is True
            deleted_vector_store = await client_async.vector_stores.delete(
                vector_store_id=vector_store.id
            )
            assert deleted_vector_store.deleted is True

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type, api_version", [(ASST_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")])
    async def test_vector_stores_batch_crud(self, client_async: openai.AsyncAzureOpenAI | openai.AsyncOpenAI, api_type, api_version, **kwargs):
        file_name = f"test{uuid.uuid4()}.txt"
        file_name_2 = f"test{uuid.uuid4()}.txt"
        with open(file_name, "w") as f:
            f.write("test")

        path = pathlib.Path(file_name)

        file = await client_async.files.create(
            file=open(path, "rb"),
            purpose="assistants"
        )
        with open(file_name_2, "w") as f:
            f.write("test")
        path_2 = pathlib.Path(file_name_2)

        file_2 = await client_async.files.create(
            file=open(path_2, "rb"),
            purpose="assistants"
        )
        try:
            vector_store = await client_async.vector_stores.create(
                name="Support FAQ"
            )
            vector_store_file_batch = await client_async.vector_stores.file_batches.create(
                vector_store_id=vector_store.id,
                file_ids=[file.id, file_2.id]
            )
            assert vector_store_file_batch.id
            assert vector_store_file_batch.object == "vector_store.file_batch"
            assert vector_store_file_batch.created_at is not None
            assert vector_store_file_batch.status

            vectors = await client_async.vector_stores.file_batches.list_files(
                vector_store_id=vector_store.id,
                batch_id=vector_store_file_batch.id
            )
            async for vector in vectors:
                assert vector.id
                assert vector.object == "vector_store.file"
                assert vector.created_at is not None

            retrieved_vector_store_file_batch = await client_async.vector_stores.file_batches.retrieve(
                vector_store_id=vector_store.id,
                batch_id=vector_store_file_batch.id
            )
            assert retrieved_vector_store_file_batch.id == vector_store_file_batch.id

        finally:
            os.remove(path)
            os.remove(path_2)
            delete_file = await client_async.files.delete(file.id)
            assert delete_file.deleted is True
            delete_file = await client_async.files.delete(file_2.id)
            assert delete_file.deleted is True
            deleted_vector_store = await client_async.vector_stores.delete(
                vector_store_id=vector_store.id
            )
            assert deleted_vector_store.deleted is True
