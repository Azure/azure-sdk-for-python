# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import json
import openai
from devtools_testutils import AzureRecordedTestCase
from conftest import AZURE, OPENAI, ALL, ASST_AZURE, configure


class TestAssistants(AzureRecordedTestCase):

    @configure
    @pytest.mark.parametrize("api_type", [ASST_AZURE])
    def test_assistants_crud(self, client, azure_openai_creds, api_type, **kwargs):

        assistant = client.beta.assistants.create(
            name="deleted3",
            instructions="You are a personal math tutor. Write and run code to answer math questions.",
            tools=[{"type": "code_interpreter"}],
            model="gpt-4",
        )

        retrieved_assistant = client.beta.assistants.retrieve(
            assistant_id=assistant.id,
        )



        # list_assistants = client.beta.assistants.list()


        # list_assistants_files = client.beta.assistants.files.list(
        #     assistant_id=assistant.id
        # )

        # deployment 404 error
        modify_assistant = client.beta.assistants.update(
            assistant_id=retrieved_assistant.id,
            metadata={"key": "value"}
        )

        # delete_assistant_file = client.beta.assistants.files.delete(
        #     assistant_id=created_assistant.id,
        #     file_id=files.id
        # )
        delete_assistant = client.beta.assistants.delete(
            assistant_id=created_assistant.id
        )


    @configure
    @pytest.mark.parametrize("api_type", [ASST_AZURE])
    def test_assistants_crud_with_files(self, client, azure_openai_creds, api_type, **kwargs):
        file = client.files.create(
            file=open("number.txt", "rb"),
            purpose="assistants"
        )

        assistant = client.beta.assistants.create(
            name="deleted3",
            instructions="You are a personal math tutor. Write and run code to answer math questions.",
            tools=[{"type": "code_interpreter"}],
            model="gpt-4",
            file_ids=[file.id]
        )

    @configure
    @pytest.mark.parametrize("api_type", [ASST_AZURE])
    def test_assistants_files_crud(self, client, azure_openai_creds, api_type, **kwargs):
        created_assistant_file = client.beta.assistants.files.create(
           assistant_id=created_assistant.id,
           file_id=files.id
        )

        retrieved_assistant_file = client.beta.assistants.files.retrieve(
           assistant_id=created_assistant.id,
           file_id=files.id
        )