# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from azure.ai.inference.prompts import PromptTemplate


class TestPrompts:

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
        assert prompt_template.prompty.model.configuration["api_version"] == "mock-api-version"
        assert prompt_template.parameters["temperature"] == 1
        assert prompt_template.parameters["frequency_penalty"] == 0.5
        assert prompt_template.parameters["presence_penalty"] == 0.5

        input = "What's the check-in and check-out time?"
        rules = [
            {"rule": "The check-in time is 3pm"},
            {"rule": "The check-out time is 11am"},
            {"rule": "Breakfast is served from 7am to 10am"},
            {"rule": 'The hotel website is https://www.myhotel.com?key1=param1&key2=param"2&key3=param<3>'},
        ]
        messages = prompt_template.create_messages(input=input, rules=rules)
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert "Breakfast is served from 7am to 10am" in messages[0]["content"]
        assert (
            "The hotel website is https://www.myhotel.com?key1=param1&amp;key2=param&quot;2&amp;key3=param&lt;3&gt;"
            in messages[0]["content"]
        )
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "What's the check-in and check-out time?"

    def test_prompt_template_from_prompty_with_masked_secrets(self, **kwargs):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        prompty_file_path = os.path.join(script_dir, "sample1_with_secrets.prompty")
        prompt_template = PromptTemplate.from_prompty(prompty_file_path)
        assert prompt_template.prompty.model.configuration["api_key"] == "test_key"
        assert prompt_template.prompty.model.configuration["api_secret"] == "test_secret"
        telemetry_dict = prompt_template.prompty.to_safe_dict()
        assert telemetry_dict["model"]["configuration"]["api_key"] == "********"
        assert telemetry_dict["model"]["configuration"]["api_secret"] == "***********"

    def test_prompt_template_from_string(self, **kwargs):
        prompt_template_str = "system prompt template text\nuser:\n{{input}}"
        prompt_template = PromptTemplate.from_string(api="chat", prompt_template=prompt_template_str)
        input = "user question input text"
        messages = prompt_template.create_messages(input=input)
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert "system prompt template text" == messages[0]["content"]
        assert "user question input text" == messages[1]["content"]

    def test_prompt_template_from_string_with_tags(self, **kwargs):
        prompt_template_str = """
            system:
            You are an AI assistant in a hotel. You help guests with their requests and provide information about the hotel and its services.

            # context
            {{#rules}}
            {{rule}}
            {{/rules}}

            {{#chat_history}}
            {{role}}:
            {{content}}
            {{/chat_history}}

            user:
            {{input}}
        """
        prompt_template = PromptTemplate.from_string(api="chat", prompt_template=prompt_template_str)
        input = "When I arrived, can I still have breakfast?"
        rules = [
            {"rule": "The check-in time is 3pm"},
            {"rule": "The check-out time is 11am"},
            {"rule": "Breakfast is served from 7am to 10am"},
        ]
        chat_history = [
            {"role": "user", "content": "I'll arrive at 2pm. What's the check-in and check-out time?"},
            {"role": "system", "content": "The check-in time is 3 PM, and the check-out time is 11 AM."},
        ]
        messages = prompt_template.create_messages(input=input, rules=rules, chat_history=chat_history)
        assert len(messages) == 4
        assert messages[0]["role"] == "system"
        assert "You are an AI assistant in a hotel." in messages[0]["content"]
        assert messages[1]["role"] == "user"
        assert "I'll arrive at 2pm. What's the check-in and check-out time?" == messages[1]["content"]
        assert messages[2]["role"] == "system"
        assert "The check-in time is 3 PM, and the check-out time is 11 AM." == messages[2]["content"]
        assert messages[3]["role"] == "user"
        assert "When I arrived, can I still have breakfast?" == messages[3]["content"]
