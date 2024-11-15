# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import pytest
import pathlib
import uuid
from devtools_testutils import AzureRecordedTestCase
from conftest import configure, ASST_AZURE, OPENAI, AZURE, PREVIEW, GA


@pytest.mark.live_test_only
class TestModels(AzureRecordedTestCase):

    @configure
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(AZURE, GA), (AZURE, PREVIEW), (OPENAI, "v1")]
    )
    def test_models_list(self, client, api_type, api_version, **kwargs):

        models = client.models.list()
        for model in models:
            assert model.id

    @configure
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(AZURE, GA), (AZURE, PREVIEW), (OPENAI, "v1")]
    )
    def test_models_retrieve(self, client, api_type, api_version, **kwargs):

        model = client.models.retrieve(**kwargs)
        assert model.id

    @configure
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(OPENAI, "v1"), (ASST_AZURE, PREVIEW)]
    )
    def test_files(self, client, api_type, api_version, **kwargs):
        file_name = f"test{uuid.uuid4()}.txt"
        with open(file_name, "w") as f:
            f.write("test")

        try:
            path = pathlib.Path(file_name)

            file1 = client.files.create(
                file=open(path, "rb"),
                purpose="assistants"
            )

            files = client.files.list()
            for file in files:
                assert file.id
                break

            files = client.files.list(purpose="assistants")
            for file in files:
                assert file.id
                break

            retrieved_file = client.files.retrieve(file1.id)
            assert retrieved_file.id
            assert retrieved_file.purpose == "assistants"
            assert retrieved_file.filename == file_name
            assert retrieved_file.created_at
            assert retrieved_file.bytes

        finally:
            client.files.delete(
                file1.id
            )
            os.remove(file_name)
