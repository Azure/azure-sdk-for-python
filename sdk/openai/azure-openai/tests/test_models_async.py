# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import pytest
import pathlib
import uuid
from devtools_testutils import AzureRecordedTestCase
from conftest import configure_async, ASST_AZURE, OPENAI, AZURE, PREVIEW, GA


@pytest.mark.live_test_only
class TestModelsAsync(AzureRecordedTestCase):

    @pytest.mark.skip("InternalServerError, opened issue")
    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(AZURE, GA), (AZURE, PREVIEW), (OPENAI, "v1")]
    )
    async def test_models_list(self, client_async, api_type, api_version, **kwargs):

        models = client_async.models.list()
        async for model in models:
            assert model.id

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(AZURE, GA), (AZURE, PREVIEW), (OPENAI, "v1")]
    )
    async def test_models_retrieve(self, client_async, api_type, api_version, **kwargs):

        model = await client_async.models.retrieve(**kwargs)
        assert model.id

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(OPENAI, "v1"), (ASST_AZURE, PREVIEW)]
    )
    async def test_files(self, client_async, api_type, api_version, **kwargs):
        file_name = f"test{uuid.uuid4()}.txt"
        with open(file_name, "w") as f:
            f.write("test")

        try:
            path = pathlib.Path(file_name)

            file1 = await client_async.files.create(
                file=open(path, "rb"),
                purpose="assistants"
            )

            files = client_async.files.list()
            async for file in files:
                assert file.id
                break

            files = client_async.files.list(purpose="assistants")
            async for file in files:
                assert file.id
                break

            retrieved_file = await client_async.files.retrieve(file1.id)
            assert retrieved_file.id
            assert retrieved_file.purpose == "assistants"
            assert retrieved_file.filename == file_name
            assert retrieved_file.created_at
            assert retrieved_file.bytes

        finally:
            await client_async.files.delete(
                file1.id
            )
            os.remove(file_name)
