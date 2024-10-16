# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import json
import azure.ai.inference as sdk
import azure.ai.inference.prompts as prompts

from model_inference_test_base import (
    ModelClientTestBase,
    ServicePreparerChatCompletions,
    ServicePreparerAOAIChatCompletions,
    ServicePreparerEmbeddings,
)
from azure.core.pipeline.transport import RequestsTransport
from devtools_testutils import recorded_by_proxy
from azure.core.exceptions import AzureError, ServiceRequestError
from azure.core.credentials import AzureKeyCredential



class TestModelClient(ModelClientTestBase):

    # **********************************************************************************
    #
    #                               UNIT TESTS
    #
    # **********************************************************************************

    def test_prompty(self, **kwargs):
        path = "/Users/weiwu/Workspace/1_Testing/TestAI/test-prompty/test.prompty"
        p = prompts.load(path)

        inputs = {
            "input": "my first question",
        }

        print(p)

        parsed = prompts.prepare(p, inputs)

        lc_messages = [] # TODO: will be removed
        for message in parsed:
            message_class = prompts.RoleMap.get_message_class(message["role"])
            lc_messages.append(message_class(content=message["content"]))

        print(lc_messages)

        assert True


    def test_prompt_config(self, **kwargs):
        path = "/Users/weiwu/Workspace/1_Testing/TestAI/test-prompty/test.prompty"
        prompt_config = prompts.get_prompt_config(file_path=path)

        inputs = {
            "input": "my first question",
        }

        messages = prompt_config.render(inputs)
        print(messages)

        assert True
