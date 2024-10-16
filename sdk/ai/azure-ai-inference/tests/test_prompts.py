# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from azure.ai.inference.prompts import PromptyTemplate
from devtools_testutils import AzureRecordedTestCase


class TestPrompts(AzureRecordedTestCase):

    # **********************************************************************************
    #
    #                               UNIT TESTS
    #
    # **********************************************************************************

    def test_prompt_config_from_prompty(self, **kwargs):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        prompty_file_path = os.path.join(script_dir, "sample1.prompty")
        prompt_config = PromptyTemplate.load(prompty_file_path)
        assert prompt_config.model_name == "gpt-4o-mini"
        assert prompt_config.config["temperature"] == 1
        assert prompt_config.config["frequency_penalty"] == 0.5
        assert prompt_config.config["presence_penalty"] == 0.5
        input_variables = {
            "input": "please tell me a joke about cats",
        }
        messages = prompt_config.render(input_variables=input_variables)
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "please tell me a joke about cats"

    def test_prompt_config_from_message(self, **kwargs):
        prompt_config = PromptyTemplate.from_message(
            api = "chat",
            model_name = "gpt-4o-mini",
            prompt_template = "system prompt template {input}"
        )
        assert prompt_config.model_name == "gpt-4o-mini"
        input_variables = {
            "input": "please tell me a joke about cats",
        }
        messages = prompt_config.render(input_variables=input_variables)
        assert len(messages) == 1
        assert messages[0]["role"] == "system"
        # TODO: need to separate the system prompt from the user input
        # assert messages[1]["role"] == "user"
        # assert messages[1]["content"] == "please tell me a joke about cats"
