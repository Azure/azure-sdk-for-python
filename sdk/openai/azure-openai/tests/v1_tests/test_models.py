# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import pytest
import pathlib
import uuid
from devtools_testutils import AzureRecordedTestCase
from conftest import configure, ALL, ASST_AZURE, OPENAI


class TestModels(AzureRecordedTestCase):

    @configure
    @pytest.mark.parametrize("api_type", ALL)
    def test_models_list(self, client, azure_openai_creds, api_type, **kwargs):

        models = client.models.list()
        for model in models:
            assert model.id

    @configure
    @pytest.mark.parametrize("api_type", ALL)
    def test_models_retrieve(self, client, azure_openai_creds, api_type, **kwargs):

        model = client.models.retrieve(**kwargs)
        assert model.id

    @configure
    @pytest.mark.parametrize("api_type", [OPENAI, ASST_AZURE])
    def test_files(self, client, azure_openai_creds, api_type, **kwargs):
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

            files = client.files.list(purpose="fine-tune")
            for file in files:
                assert file.id

            files = client.files.list(purpose="assistants")
            for file in files:
                assert file.id

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
