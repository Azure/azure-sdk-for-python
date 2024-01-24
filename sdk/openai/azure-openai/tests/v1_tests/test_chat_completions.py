# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import json
import openai
from devtools_testutils import AzureRecordedTestCase
from conftest import (
    AZURE,
    OPENAI,
    ALL,
    AZURE_AD,
    GPT_4_AZURE,
    GPT_4_OPENAI,
    configure
)


class TestChatCompletions(AzureRecordedTestCase):

    @configure
    @pytest.mark.parametrize("api_type", ALL)
    def test_chat_completion(self, client, azure_openai_creds, api_type, **kwargs):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]

        completion = client.chat.completions.create(messages=messages, **kwargs)
        assert completion.id
        assert completion.object == "chat.completion"
        assert completion.model
        assert completion.created
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].message.content is not None
        assert completion.choices[0].message.role

    @configure
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    def test_streamed_chat_completions(self, client, azure_openai_creds, api_type, **kwargs):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "How do I bake a chocolate cake?"}
        ]

        response = client.chat.completions.create(messages=messages, stream=True, **kwargs)

        for completion in response:
            # API versions after 2023-05-15 send an empty first completion with RAI
            if len(completion.choices) > 0:
                assert completion.id
                assert completion.object == "chat.completion.chunk"
                assert completion.model
                assert completion.created
                for c in completion.choices:
                    assert c.index is not None
                    assert c.delta is not None

    @configure
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    def test_chat_completion_max_tokens(self, client, azure_openai_creds, api_type, **kwargs):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]

        completion = client.chat.completions.create(messages=messages, max_tokens=50, **kwargs)

        assert completion.id
        assert completion.object == "chat.completion"
        assert completion.model
        assert completion.created
        assert completion.usage.completion_tokens <= 50
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].message.content is not None
        assert completion.choices[0].message.role

    @configure
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    def test_chat_completion_temperature(self, client, azure_openai_creds, api_type, **kwargs):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]

        completion = client.chat.completions.create(messages=messages, temperature=0.8, **kwargs)

        assert completion.id
        assert completion.object == "chat.completion"
        assert completion.model
        assert completion.created
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].message.content is not None
        assert completion.choices[0].message.role

    @configure
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    def test_chat_completion_top_p(self, client, azure_openai_creds, api_type, **kwargs):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]

        completion = client.chat.completions.create(messages=messages, top_p=0.1, **kwargs)

        assert completion.id
        assert completion.object == "chat.completion"
        assert completion.model
        assert completion.created
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].message.content is not None
        assert completion.choices[0].message.role

    @configure
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    def test_chat_completion_n(self, client, azure_openai_creds, api_type, **kwargs):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]

        completion = client.chat.completions.create(messages=messages, n=2, **kwargs)

        assert completion.id
        assert completion.object == "chat.completion"
        assert completion.model
        assert completion.created
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 2
        for idx, c in enumerate(completion.choices):
            assert c.finish_reason
            assert c.index == idx
            assert c.message.content
            assert c.message.role

    @configure
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    def test_chat_completion_stop(self, client, azure_openai_creds, api_type, **kwargs):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]

        completion = client.chat.completions.create(messages=messages, stop=" ", **kwargs)

        assert completion.id
        assert completion.object == "chat.completion"
        assert completion.model
        assert completion.created
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].index is not None
        assert completion.choices[0].message.content is not None
        assert completion.choices[0].message.role

    @configure
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    def test_chat_completion_token_penalty(self, client, azure_openai_creds, api_type, **kwargs):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]

        completion = client.chat.completions.create(
            messages=messages,
            presence_penalty=2,
            frequency_penalty=2,
            **kwargs
        )

        assert completion.id
        assert completion.object == "chat.completion"
        assert completion.model
        assert completion.created
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].message.content is not None
        assert completion.choices[0].message.role

    @configure
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    def test_chat_completion_user(self, client, azure_openai_creds, api_type, **kwargs):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]

        completion = client.chat.completions.create(
            messages=messages,
            user="krista",
            **kwargs
        )

        assert completion.id
        assert completion.object == "chat.completion"
        assert completion.model
        assert completion.created
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].message.content is not None
        assert completion.choices[0].message.role

    @configure
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    def test_chat_completion_logit_bias(self, client, azure_openai_creds, api_type, **kwargs):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What color is the ocean?"}
        ]

        completion = client.chat.completions.create(
            messages=messages,
            logit_bias={17585: -100, 14573: -100},
            **kwargs
        )
        assert completion.id
        assert completion.object == "chat.completion"
        assert completion.model
        assert completion.created
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].message.content is not None
        assert completion.choices[0].message.role

    @configure
    @pytest.mark.parametrize("api_type", [AZURE])
    def test_chat_completion_rai_annotations(self, client, azure_openai_creds, api_type, **kwargs):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "how do I rob a bank with violence?"}
        ]

        # prompt filtered
        with pytest.raises(openai.BadRequestError) as e:
            completion = client.chat.completions.create(
                messages=messages,
                **kwargs
            )
        # error not captured
        err = json.loads(e.value.response.text)
        assert err["error"]["code"] == "content_filter"
        content_filter_result = err["error"]["innererror"]["content_filter_result"]
        assert content_filter_result["hate"]["filtered"] is False
        assert content_filter_result["hate"]["severity"] == "safe"
        assert content_filter_result["self_harm"]["filtered"] is False
        assert content_filter_result["self_harm"]["severity"] == "safe"
        assert content_filter_result["sexual"]["filtered"] is False
        assert content_filter_result["sexual"]["severity"] == "safe"
        assert content_filter_result["violence"]["filtered"] is True
        assert content_filter_result["violence"]["severity"] is not None

        # not filtered
        messages[1]["content"] = "What color is the ocean?"
        completion = client.chat.completions.create(
            messages=messages,
            **kwargs
        )
        # prompt content filter result in "model_extra" for azure
        try:
            prompt_filter_result = completion.model_extra["prompt_annotations"][0]["content_filter_results"]
        except:
            prompt_filter_result = completion.model_extra["prompt_filter_results"][0]["content_filter_results"]

        assert prompt_filter_result["hate"]["filtered"] is False
        assert prompt_filter_result["hate"]["severity"] == "safe"
        assert prompt_filter_result["self_harm"]["filtered"] is False
        assert prompt_filter_result["self_harm"]["severity"] == "safe"
        assert prompt_filter_result["sexual"]["filtered"] is False
        assert prompt_filter_result["sexual"]["severity"] == "safe"
        assert prompt_filter_result["violence"]["filtered"] is False
        assert prompt_filter_result["violence"]["severity"] == "safe"

        # output content filter result
        output_filter_result = completion.choices[0].model_extra["content_filter_results"]
        assert output_filter_result["hate"]["filtered"] is False
        assert output_filter_result["hate"]["severity"] == "safe"
        assert output_filter_result["self_harm"]["filtered"] is False
        assert output_filter_result["self_harm"]["severity"] == "safe"
        assert output_filter_result["sexual"]["filtered"] is False
        assert output_filter_result["sexual"]["severity"] == "safe"
        assert output_filter_result["violence"]["filtered"] is False
        assert output_filter_result["violence"]["severity"] == "safe"

    @configure
    @pytest.mark.parametrize("api_type", [OPENAI, AZURE])
    def test_chat_completion_functions(self, client, azure_openai_creds, api_type, **kwargs):
        messages = [
            {"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."},
            {"role": "user", "content": "What's the weather like today in Seattle?"}
        ]

        functions=[
            {
                "name": "get_current_weather",
                "description": "Get the current weather",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "format": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "The temperature unit to use. Infer this from the users location.",
                        },
                    },
                    "required": ["location"],
                },
            }
        ]

        completion = client.chat.completions.create(
            messages=messages,
            functions=functions,
            **kwargs
        )
        assert completion.id
        assert completion.object == "chat.completion"
        assert completion.model
        assert completion.created
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].message.role
        function_call =  completion.choices[0].message.function_call
        assert function_call.name == "get_current_weather"
        assert "Seattle" in function_call.arguments

        if api_type == "azure":
            # prompt content filter result in "model_extra" for azure
            try:
                prompt_filter_result = completion.model_extra["prompt_annotations"][0]["content_filter_results"]
            except:
                prompt_filter_result = completion.model_extra["prompt_filter_results"][0]["content_filter_results"]

            assert prompt_filter_result["hate"]["filtered"] is False
            assert prompt_filter_result["hate"]["severity"] == "safe"
            assert prompt_filter_result["self_harm"]["filtered"] is False
            assert prompt_filter_result["self_harm"]["severity"] == "safe"
            assert prompt_filter_result["sexual"]["filtered"] is False
            assert prompt_filter_result["sexual"]["severity"] == "safe"
            assert prompt_filter_result["violence"]["filtered"] is False
            assert prompt_filter_result["violence"]["severity"] == "safe"

        messages.append(
            {
                "role": "function",
                "name": "get_current_weather",
                "content": "{\"temperature\": \"22\", \"unit\": \"celsius\", \"description\": \"Sunny\"}"
            }
        )
        function_completion = client.chat.completions.create(
            messages=messages,
            functions=functions,
            **kwargs
        )
        assert function_completion
        assert "sunny" in function_completion.choices[0].message.content.lower()
        assert "22" in function_completion.choices[0].message.content
        assert function_completion.choices[0].message.role == "assistant"

        if api_type == "azure":
            # output content filter result
            output_filter_result = function_completion.choices[0].model_extra["content_filter_results"]
            assert output_filter_result["hate"]["filtered"] is False
            assert output_filter_result["hate"]["severity"] == "safe"
            assert output_filter_result["self_harm"]["filtered"] is False
            assert output_filter_result["self_harm"]["severity"] == "safe"
            assert output_filter_result["sexual"]["filtered"] is False
            assert output_filter_result["sexual"]["severity"] == "safe"
            assert output_filter_result["violence"]["filtered"] is False
            assert output_filter_result["violence"]["severity"] == "safe"

    @configure
    @pytest.mark.parametrize("api_type", [OPENAI, AZURE])
    def test_chat_completion_functions_stream(self, client, azure_openai_creds, api_type, **kwargs):
        messages = [
            {"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."},
            {"role": "user", "content": "What's the weather like today in Seattle?"}
        ]

        functions=[
            {
                "name": "get_current_weather",
                "description": "Get the current weather",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "format": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "The temperature unit to use. Infer this from the users location.",
                        },
                    },
                    "required": ["location"],
                },
            }
        ]

        response = client.chat.completions.create(
            messages=messages,
            functions=functions,
            stream=True,
            **kwargs
        )
        args = ""
        for completion in response:
            for c in completion.choices:
                assert c.delta is not None
                if c.delta.function_call:
                    if c.delta.function_call.name:
                        assert c.delta.function_call.name == "get_current_weather"
                    if c.delta.function_call.arguments:
                        args += c.delta.function_call.arguments
        assert "Seattle" in args

        messages.append(
            {
                "role": "function",
                "name": "get_current_weather",
                "content": "{\"temperature\": \"22\", \"unit\": \"celsius\", \"description\": \"Sunny\"}"
            }
        )
        function_completion = client.chat.completions.create(
            messages=messages,
            functions=functions,
            stream=True,
            **kwargs
        )
        content = ""
        for completion in function_completion:
            for c in completion.choices:
                assert c.delta is not None
                if c.delta.content:
                    content += c.delta.content
                if c.delta.role:
                    assert c.delta.role == "assistant"
        assert "sunny" in content.lower()
        assert "22" in content

    @configure
    @pytest.mark.parametrize("api_type", [OPENAI, AZURE])
    def test_chat_completion_given_function(self, client, azure_openai_creds, api_type, **kwargs):
        messages = [
            {"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."},
            {"role": "user", "content": "What's the weather like today in Seattle?"}
        ]

        functions=[
            {
                "name": "get_current_weather",
                "description": "Get the current weather",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "format": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "The temperature unit to use. Infer this from the users location.",
                        },
                    },
                    "required": ["location"],
                },
            },
            {
                "name": "get_current_temperature",
                "description": "Get the current temperature",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "format": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "The temperature unit to use.",
                        },
                    },
                    "required": ["location"],
                },
            }
        ]

        completion = client.chat.completions.create(
            messages=messages,
            functions=functions,
            function_call={"name": "get_current_temperature"},
            **kwargs
        )
        assert completion.id
        assert completion.object == "chat.completion"
        assert completion.model
        assert completion.created
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].message.role
        function_call =  completion.choices[0].message.function_call
        assert function_call.name == "get_current_temperature"
        assert "Seattle" in function_call.arguments

        messages.append(
            {
                "role": "function",
                "name": "get_current_temperature",
                "content": "{\"temperature\": \"22\", \"unit\": \"celsius\"}"
            }
        )
        function_completion = client.chat.completions.create(
            messages=messages,
            functions=functions,
            **kwargs
        )
        assert function_completion
        assert "22" in function_completion.choices[0].message.content
        assert function_completion.choices[0].message.role == "assistant"

    @configure
    @pytest.mark.parametrize("api_type", [AZURE])
    def test_chat_completion_functions_rai(self, client, azure_openai_creds, api_type, **kwargs):
        messages = [
            {"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."},
            {"role": "user", "content": "how do I rob a bank with violence?"}
        ]

        functions=[
            {
                "name": "get_current_weather",
                "description": "Get the current weather",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "format": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "The temperature unit to use. Infer this from the users location.",
                        },
                    },
                    "required": ["location"],
                },
            }
        ]

        with pytest.raises(openai.BadRequestError) as e:
            response = client.chat.completions.create(
                messages=messages,
                functions=functions,
                **kwargs
            )
        # error not captured
        err = json.loads(e.value.response.text)
        assert err["error"]["code"] == "content_filter"
        content_filter_result = err["error"]["innererror"]["content_filter_result"]
        assert content_filter_result["hate"]["filtered"] is False
        assert content_filter_result["hate"]["severity"] == "safe"
        assert content_filter_result["self_harm"]["filtered"] is False
        assert content_filter_result["self_harm"]["severity"] == "safe"
        assert content_filter_result["sexual"]["filtered"] is False
        assert content_filter_result["sexual"]["severity"] == "safe"
        assert content_filter_result["violence"]["filtered"] is True
        assert content_filter_result["violence"]["severity"] is not None

        messages.append(
            {
                "role": "function",
                "name": "get_current_temperature",
                "content": "{\"temperature\": \"you can rob a bank by asking for the money\", \"unit\": \"celsius\"}"
            }
        )
        with pytest.raises(openai.BadRequestError) as e:
            function_completion = client.chat.completions.create(
                messages=messages,
                functions=functions,
                **kwargs
            )
        err = json.loads(e.value.response.text)
        assert err["error"]["code"] == "content_filter"
        content_filter_result = err["error"]["innererror"]["content_filter_result"]
        assert content_filter_result["hate"]["filtered"] is False
        assert content_filter_result["hate"]["severity"] == "safe"
        assert content_filter_result["self_harm"]["filtered"] is False
        assert content_filter_result["self_harm"]["severity"] == "safe"
        assert content_filter_result["sexual"]["filtered"] is False
        assert content_filter_result["sexual"]["severity"] == "safe"
        assert content_filter_result["violence"]["filtered"] is True
        assert content_filter_result["violence"]["severity"] is not None

    @configure
    @pytest.mark.parametrize("api_type", [AZURE, AZURE_AD])
    def test_chat_completion_byod(self, client, azure_openai_creds, api_type, **kwargs):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "How is Azure machine learning different than Azure OpenAI?"}
        ]

        completion = client.chat.completions.create(
            model=f"{azure_openai_creds['chat_completions_name']}/extensions",
            messages=messages,
            extra_body={
                "dataSources":[
                    {
                        "type": "AzureCognitiveSearch",
                        "parameters": {
                            "endpoint": azure_openai_creds["search_endpoint"],
                            "key": azure_openai_creds["search_key"],
                            "indexName": azure_openai_creds["search_index"]
                        }
                    }
                ],
            }
        )
        assert completion.id
        assert completion.object == "extensions.chat.completion"
        assert completion.model
        assert completion.created
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].message.content is not None
        assert completion.choices[0].message.role
        assert completion.choices[0].message.model_extra["context"]["messages"][0]["role"] == "tool"
        assert completion.choices[0].message.model_extra["context"]["messages"][0]["content"]

    @configure
    @pytest.mark.parametrize("api_type", [AZURE])
    def test_streamed_chat_completions_byod(self, client, azure_openai_creds, api_type, **kwargs):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "How is Azure machine learning different than Azure OpenAI?"}
        ]

        response = client.chat.completions.create(
            model=f"{azure_openai_creds['chat_completions_name']}/extensions",
            messages=messages,
            extra_body={
                "dataSources":[
                    {
                        "type": "AzureCognitiveSearch",
                        "parameters": {
                            "endpoint": azure_openai_creds["search_endpoint"],
                            "key": azure_openai_creds["search_key"],
                            "indexName": azure_openai_creds["search_index"]
                        }
                    }
                ],
            },
            stream=True
        )
        for chunk in response:
            assert chunk.id
            assert chunk.object == "extensions.chat.completion.chunk"
            assert chunk.created
            assert chunk.model
            for c in chunk.choices:
                assert c.index is not None
                assert c.delta is not None
                if c.delta.model_extra.get("context"):
                    assert c.delta.model_extra["context"]["messages"][0]["role"] == "tool"
                    assert c.delta.model_extra["context"]["messages"][0]["content"]
                if c.delta.role:
                    assert c.delta.role == "assistant"
                if c.delta.content:
                    assert c.delta.content is not None

    @configure
    @pytest.mark.parametrize("api_type", [GPT_4_AZURE, GPT_4_OPENAI])
    def test_chat_completion_seed(self, client, azure_openai_creds, api_type, **kwargs):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Why is the sky blue?"}
        ]

        completion = client.chat.completions.create(messages=messages, seed=42, **kwargs)
        assert completion.system_fingerprint
        completion = client.chat.completions.create(messages=messages, seed=42, **kwargs)
        assert completion.system_fingerprint

    @configure
    @pytest.mark.parametrize("api_type", [GPT_4_AZURE, GPT_4_OPENAI])
    def test_chat_completion_json_response(self, client, azure_openai_creds, api_type, **kwargs):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020? Return in json with answer as the key."}
        ]

        completion = client.chat.completions.create(messages=messages, response_format={ "type": "json_object" }, **kwargs)
        assert completion.id
        assert completion.object == "chat.completion"
        assert completion.system_fingerprint
        assert completion.model
        assert completion.created
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert json.loads(completion.choices[0].message.content)
        assert completion.choices[0].message.role

    @configure
    @pytest.mark.parametrize("api_type", [GPT_4_AZURE])
    def test_chat_completion_block_list_term(self, client, azure_openai_creds, api_type, **kwargs):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the best time of year to pick pineapple?"}
        ]
        with pytest.raises(openai.BadRequestError) as e:
            client.chat.completions.create(messages=messages, **kwargs)
        err = json.loads(e.value.response.text)
        assert err["error"]["code"] == "content_filter"
        content_filter_result = err["error"]["innererror"]["content_filter_result"]
        assert content_filter_result["custom_blocklists"][0]["filtered"] is True
        assert content_filter_result["custom_blocklists"][0]["id"].startswith("CustomBlockList")
        assert content_filter_result["hate"]["filtered"] is False
        assert content_filter_result["hate"]["severity"] == "safe"
        assert content_filter_result["self_harm"]["filtered"] is False
        assert content_filter_result["self_harm"]["severity"] == "safe"
        assert content_filter_result["sexual"]["filtered"] is False
        assert content_filter_result["sexual"]["severity"] == "safe"
        assert content_filter_result["violence"]["filtered"] is False
        assert content_filter_result["violence"]["severity"] == "safe"
        assert content_filter_result["profanity"]["detected"] is False
        assert content_filter_result["profanity"]["filtered"] is False
        assert content_filter_result["jailbreak"]["detected"] is False
        assert content_filter_result["jailbreak"]["filtered"] is False

    @configure
    @pytest.mark.parametrize("api_type", [GPT_4_AZURE, GPT_4_OPENAI])
    def test_chat_completion_tools(self, client, azure_openai_creds, api_type, **kwargs):
        messages = [
            {"role": "system", "content": "Don't make assumptions about what values to plug into tools. Ask for clarification if a user request is ambiguous."},
            {"role": "user", "content": "What's the weather like today in Seattle?"}
        ]
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_current_weather",
                    "description": "Get the current weather in a given location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                        },
                        "required": ["location"],
                    },
                }
            }
        ]

        completion = client.chat.completions.create(
            messages=messages,
            tools=tools,
            tool_choice="auto",
            **kwargs
        )
        assert completion.id
        assert completion.object == "chat.completion"
        assert completion.model
        assert completion.created
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].message.role
        function_call =  completion.choices[0].message.tool_calls[0].function
        assert function_call.name == "get_current_weather"
        assert "Seattle" in function_call.arguments
        if api_type == GPT_4_AZURE:
            # workaround to address difference between AOAI and OAI
            completion.choices[0].message.content = None
        messages.append(completion.choices[0].message)

        tool_call_id = completion.choices[0].message.tool_calls[0].id
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": "{\"temperature\": \"22\", \"unit\": \"celsius\", \"description\": \"Sunny\"}"
            }
        )
        tool_completion = client.chat.completions.create(
            messages=messages,
            tools=tools,
            **kwargs
        )
        assert tool_completion
        assert "sunny" in tool_completion.choices[0].message.content.lower()
        assert "22" in tool_completion.choices[0].message.content
        assert tool_completion.choices[0].message.role == "assistant"

    @configure
    @pytest.mark.parametrize("api_type", [GPT_4_AZURE, GPT_4_OPENAI])
    def test_chat_completion_tools_stream(self, client, azure_openai_creds, api_type, **kwargs):
        messages = [
            {"role": "system", "content": "Don't make assumptions about what values to plug into tools. Ask for clarification if a user request is ambiguous."},
            {"role": "user", "content": "What's the weather like today in Seattle?"}
        ]

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_current_weather",
                    "description": "Get the current weather in a given location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                        },
                        "required": ["location"],
                    },
                }
            }
        ]
        response = client.chat.completions.create(
            messages=messages,
            tools=tools,
            stream=True,
            **kwargs
        )
        args = ""
        for completion in response:
            for c in completion.choices:
                assert c.delta is not None
                if c.delta.role:
                    assistant = c.delta.role
                if c.delta.tool_calls:
                    if c.delta.tool_calls[0].type:
                        tool_type = c.delta.tool_calls[0].type
                    if c.delta.tool_calls[0].id:
                        tool_id = c.delta.tool_calls[0].id
                    if c.delta.tool_calls[0].function.name:
                        function_name = c.delta.tool_calls[0].function.name
                    if c.delta.tool_calls[0].function.arguments:
                        args += c.delta.tool_calls[0].function.arguments
        assert "Seattle" in args

        assistant_message = {
            "role": assistant,
            "tool_calls": [
                {
                    "id": tool_id,
                    "type": tool_type,
                    "function": {
                        "name": function_name,
                        "arguments": args
                    }
                }
            ],
            "content": None
        }
        messages.append(assistant_message)
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_id,
                "content": "{\"temperature\": \"22\", \"unit\": \"celsius\", \"description\": \"Sunny\"}"
            }
        )
        function_completion = client.chat.completions.create(
            messages=messages,
            tools=tools,
            stream=True,
            **kwargs
        )
        content = ""
        for func in function_completion:
            for c in func.choices:
                assert c.delta is not None
                if c.delta.content:
                    content += c.delta.content
                if c.delta.role:
                    assert c.delta.role == "assistant"
        assert "sunny" in content.lower()
        assert "22" in content

    @configure
    @pytest.mark.parametrize("api_type", [GPT_4_AZURE, GPT_4_OPENAI])
    def test_chat_completion_tools_parallel_func(self, client, azure_openai_creds, api_type, **kwargs):
        messages = [
            {"role": "system", "content": "Don't make assumptions about what values to plug into tools. Ask for clarification if a user request is ambiguous."},
            {"role": "user", "content": "What's the weather like today in Seattle and Los Angeles?"}
        ]
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_current_weather",
                    "description": "Get the current weather in a given location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                        },
                        "required": ["location"],
                    },
                }
            }
        ]

        completion = client.chat.completions.create(
            messages=messages,
            tools=tools,
            tool_choice="auto",
            **kwargs
        )
        assert completion.id
        assert completion.object == "chat.completion"
        assert completion.model
        assert completion.created
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].message.role

        assert len(completion.choices[0].message.tool_calls) == 2
        if api_type == GPT_4_AZURE:
            # workaround to address difference between AOAI and OAI
            completion.choices[0].message.content = None
        messages.append(completion.choices[0].message)

        function_call = completion.choices[0].message.tool_calls[0].function
        assert function_call.name == "get_current_weather"
        assert "Seattle" in function_call.arguments
        tool_call_id_0 = completion.choices[0].message.tool_calls[0].id

        function_call = completion.choices[0].message.tool_calls[1].function
        assert function_call.name == "get_current_weather"
        assert "Los Angeles" in function_call.arguments
        tool_call_id_1 = completion.choices[0].message.tool_calls[1].id
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call_id_0,
                "content": "{\"temperature\": \"22\", \"unit\": \"celsius\", \"description\": \"Cloudy\"}"
            }
        )
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call_id_1,
                "content": "{\"temperature\": \"80\", \"unit\": \"fahrenheit\", \"description\": \"Sunny\"}"
            }
        )
        tool_completion = client.chat.completions.create(
            messages=messages,
            tools=tools,
            **kwargs
        )
        assert tool_completion
        assert "sunny" in tool_completion.choices[0].message.content.lower()
        assert "cloudy" in tool_completion.choices[0].message.content.lower()
        assert "22" in tool_completion.choices[0].message.content
        assert "80" in tool_completion.choices[0].message.content
        assert tool_completion.choices[0].message.role == "assistant"

    @configure
    @pytest.mark.parametrize("api_type", [OPENAI, GPT_4_AZURE])
    def test_chat_completion_vision(self, client, azure_openai_creds, api_type, **kwargs):
        completion = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What's in this image?"},
                        {
                            "type": "image_url",
                            "image_url": "https://learn.microsoft.com/en-us/azure/ai-services/computer-vision/images/handwritten-note.jpg",
                        },
                    ],
                }
            ],
        )
        assert completion.id
        assert completion.object == "chat.completion"
        assert completion.model
        assert completion.created
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].index is not None
        assert completion.choices[0].message.content is not None
        assert completion.choices[0].message.role
