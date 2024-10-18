# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from azure.ai.inference.prompts import PromptTemplate
from devtools_testutils import AzureRecordedTestCase


class TestPrompts(AzureRecordedTestCase):

    # **********************************************************************************
    #
    #                               UNIT TESTS
    #
    # **********************************************************************************

    def test_prompt_template_from_prompty(self, **kwargs):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        prompty_file_path = os.path.join(script_dir, "sample1.prompty")
        prompt_template = PromptTemplate.from_prompty(prompty_file_path)
        assert prompt_template.model_name == "gpt-4o-mini"
        assert prompt_template.config["temperature"] == 1
        assert prompt_template.config["frequency_penalty"] == 0.5
        assert prompt_template.config["presence_penalty"] == 0.5
        input_variables = {
            "input": "please tell me a joke about cats",
        }
        messages = prompt_template.render(input_variables=input_variables)
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "please tell me a joke about cats"

    def test_prompt_template_from_message(self, **kwargs):
        prompt_template = PromptTemplate.from_message(
            api = "chat",
            model_name = "gpt-4o-mini",
            prompt_template = "system prompt template {input}"
        )
        assert prompt_template.model_name == "gpt-4o-mini"
        input_variables = {
            "input": "please tell me a joke about cats",
        }
        messages = prompt_template.render(input_variables=input_variables)
        assert len(messages) == 1
        assert messages[0]["role"] == "system"
