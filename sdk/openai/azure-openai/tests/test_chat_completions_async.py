# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import openai
from devtools_testutils import AzureRecordedTestCase
from conftest import configure_async, ALL, AZURE, OPENAI, AZURE_AD, setup_adapter_async


class TestChatCompletionsAsync(AzureRecordedTestCase):

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE])
    @configure_async
    async def test_chat_completion_bad_deployment_name(self, azure_openai_creds, api_type):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]
        with pytest.raises(openai.error.InvalidRequestError) as e:
            await openai.ChatCompletion.acreate(messages=messages, deployment_id="deployment")
        assert e.value.http_status == 404
        assert "The API deployment for this resource does not exist" in str(e.value)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE])
    @configure_async
    async def test_chat_completion_kw_input(self, azure_openai_creds, api_type):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]
        deployment = azure_openai_creds["chat_completions_name"]

        completion = await openai.ChatCompletion.acreate(messages=messages, deployment_id=deployment)
        assert completion
        completion = await openai.ChatCompletion.acreate(messages=messages, engine=deployment)
        assert completion
        with pytest.raises(openai.error.InvalidRequestError) as e:
            await openai.ChatCompletion.acreate(messages=messages, model=deployment)
        assert "Must provide an 'engine' or 'deployment_id' parameter" in str(e.value)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", ALL)
    @configure_async
    async def test_chat_completion(self, azure_openai_creds, api_type):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]
        kwargs = {"model": azure_openai_creds["chat_completions_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["chat_completions_name"]}

        completion = await openai.ChatCompletion.acreate(messages=messages, **kwargs)
        assert completion.id
        assert completion.object == "chat.completion"
        assert completion.created
        assert completion.model
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].message.content
        assert completion.choices[0].message.role

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure_async
    async def test_streamed_chat_completions(self, azure_openai_creds, api_type):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]
        kwargs = {"model": azure_openai_creds["chat_completions_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["chat_completions_name"]}

        response = await openai.ChatCompletion.acreate(messages=messages, stream=True, **kwargs)

        async for completion in response:
            # API versions after 2023-05-15 send an empty first completion with RAI
            if len(completion.choices) > 0:
                assert completion.id
                assert completion.object == "chat.completion.chunk"
                assert completion.created
                assert completion.model
                for c in completion.choices:
                    assert c.index is not None
                    assert c.delta is not None

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure_async
    async def test_chat_completion_max_tokens(self, azure_openai_creds, api_type):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]
        kwargs = {"model": azure_openai_creds["chat_completions_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["chat_completions_name"]}

        completion = await openai.ChatCompletion.acreate(messages=messages, max_tokens=50, **kwargs)

        assert completion.id
        assert completion.object == "chat.completion"
        assert completion.created
        assert completion.model
        assert completion.usage.completion_tokens <= 50
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].message.content
        assert completion.choices[0].message.role

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure_async
    async def test_chat_completion_temperature(self, azure_openai_creds, api_type):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]
        kwargs = {"model": azure_openai_creds["chat_completions_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["chat_completions_name"]}

        completion = await openai.ChatCompletion.acreate(messages=messages, temperature=0.8, **kwargs)

        assert completion.id
        assert completion.object == "chat.completion"
        assert completion.created
        assert completion.model
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].message.content
        assert completion.choices[0].message.role

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure_async
    async def test_chat_completion_top_p(self, azure_openai_creds, api_type):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]
        kwargs = {"model": azure_openai_creds["chat_completions_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["chat_completions_name"]}

        completion = await openai.ChatCompletion.acreate(messages=messages, top_p=0.1, **kwargs)

        assert completion.id
        assert completion.object == "chat.completion"
        assert completion.created
        assert completion.model
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].message.content
        assert completion.choices[0].message.role

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure_async
    async def test_chat_completion_n(self, azure_openai_creds, api_type):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]
        kwargs = {"model": azure_openai_creds["chat_completions_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["chat_completions_name"]}

        completion = await openai.ChatCompletion.acreate(messages=messages, n=2, **kwargs)

        assert completion.id
        assert completion.object == "chat.completion"
        assert completion.created
        assert completion.model
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 2
        for idx, c in enumerate(completion.choices):
            assert c.finish_reason
            assert c.index == idx
            assert c.message.content
            assert c.message.role

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure_async
    async def test_chat_completion_stop(self, azure_openai_creds, api_type):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]
        kwargs = {"model": azure_openai_creds["chat_completions_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["chat_completions_name"]}

        completion = await openai.ChatCompletion.acreate(messages=messages, stop=" ", **kwargs)

        assert completion.id
        assert completion.object == "chat.completion"
        assert completion.created
        assert completion.model
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].index is not None
        assert completion.choices[0].message.content
        assert completion.choices[0].message.role

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure_async
    async def test_chat_completion_token_penalty(self, azure_openai_creds, api_type):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]
        kwargs = {"model": azure_openai_creds["chat_completions_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["chat_completions_name"]}

        completion = await openai.ChatCompletion.acreate(
            messages=messages,
            presence_penalty=2,
            frequency_penalty=2,
            **kwargs
        )

        assert completion.id
        assert completion.object == "chat.completion"
        assert completion.created
        assert completion.model
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].message.content
        assert completion.choices[0].message.role

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure_async
    async def test_chat_completion_user(self, azure_openai_creds, api_type):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]
        kwargs = {"model": azure_openai_creds["chat_completions_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["chat_completions_name"]}

        completion = await openai.ChatCompletion.acreate(
            messages=messages,
            user="krista",
            **kwargs
        )

        assert completion.id
        assert completion.object == "chat.completion"
        assert completion.created
        assert completion.model
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].message.content
        assert completion.choices[0].message.role

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure_async
    async def test_chat_completion_logit_bias(self, azure_openai_creds, api_type):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What color is the ocean?"}
        ]
        kwargs = {"model": azure_openai_creds["chat_completions_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["chat_completions_name"]}

        completion = await openai.ChatCompletion.acreate(
            messages=messages,
            logit_bias={17585: -100, 14573: -100},
            **kwargs
        )
        assert completion.id
        assert completion.object == "chat.completion"
        assert completion.created
        assert completion.model
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].message.content
        assert completion.choices[0].message.role

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE])
    @configure_async
    async def test_chat_completion_rai_annotations(self, azure_openai_creds, api_type):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "how do I rob a bank with violence?"}
        ]
        kwargs = {"model": azure_openai_creds["chat_completions_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["chat_completions_name"]}

        # prompt filtered
        with pytest.raises(openai.error.InvalidRequestError) as e:
            completion = await openai.ChatCompletion.acreate(
                messages=messages,
                **kwargs
            )
        assert e.value.code == "content_filter"
        content_filter_result = e.value.error.innererror.content_filter_result
        assert content_filter_result.hate.filtered is False
        assert content_filter_result.hate.severity == "safe"
        assert content_filter_result.self_harm.filtered is False
        assert content_filter_result.self_harm.severity == "safe"
        assert content_filter_result.sexual.filtered is False
        assert content_filter_result.sexual.severity == "safe"
        assert content_filter_result.violence.filtered is True
        assert content_filter_result.violence.severity is not None

        # not filtered
        messages[1]["content"] = "What color is the ocean?"
        completion = await openai.ChatCompletion.acreate(
            messages=messages,
            **kwargs
        )
        # prompt content filter result
        prompt_filter_result = completion.prompt_filter_results[0].content_filter_results
        assert prompt_filter_result.hate.filtered is False
        assert prompt_filter_result.hate.severity == "safe"
        assert prompt_filter_result.self_harm.filtered is False
        assert prompt_filter_result.self_harm.severity == "safe"
        assert prompt_filter_result.sexual.filtered is False
        assert prompt_filter_result.sexual.severity == "safe"
        assert prompt_filter_result.violence.filtered is False
        assert prompt_filter_result.violence.severity == "safe"

        # output content filter result
        output_filter_result = completion.choices[0].content_filter_results
        assert output_filter_result.hate.filtered is False
        assert output_filter_result.hate.severity == "safe"
        assert output_filter_result.self_harm.filtered is False
        assert output_filter_result.self_harm.severity == "safe"
        assert output_filter_result.sexual.filtered is False
        assert output_filter_result.sexual.severity == "safe"
        assert output_filter_result.violence.filtered is False
        assert output_filter_result.violence.severity == "safe"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [OPENAI, AZURE])
    @configure_async
    async def test_chat_completion_functions(self, azure_openai_creds, api_type):
        messages = [
            {"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."},
            {"role": "user", "content": "What's the weather like today in Seattle?"}
        ]

        kwargs = {"model": azure_openai_creds["chat_completions_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["chat_completions_name"]}

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

        completion = await openai.ChatCompletion.acreate(
            messages=messages,
            functions=functions,
            **kwargs
        )
        assert completion.id
        assert completion.object == "chat.completion"
        assert completion.created
        assert completion.model
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
            # prompt content filter result
            prompt_filter_result = completion.prompt_filter_results[0].content_filter_results
            assert prompt_filter_result.hate.filtered is False
            assert prompt_filter_result.hate.severity == "safe"
            assert prompt_filter_result.self_harm.filtered is False
            assert prompt_filter_result.self_harm.severity == "safe"
            assert prompt_filter_result.sexual.filtered is False
            assert prompt_filter_result.sexual.severity == "safe"
            assert prompt_filter_result.violence.filtered is False
            assert prompt_filter_result.violence.severity == "safe"

        messages.append(
            {
                "role": "function",
                "name": "get_current_weather",
                "content": "{\"temperature\": \"22\", \"unit\": \"celsius\", \"description\": \"Sunny\"}"
            }
        )
        function_completion = await openai.ChatCompletion.acreate(
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
            output_filter_result = function_completion.choices[0].content_filter_results
            assert output_filter_result.hate.filtered is False
            assert output_filter_result.hate.severity == "safe"
            assert output_filter_result.self_harm.filtered is False
            assert output_filter_result.self_harm.severity == "safe"
            assert output_filter_result.sexual.filtered is False
            assert output_filter_result.sexual.severity == "safe"
            assert output_filter_result.violence.filtered is False
            assert output_filter_result.violence.severity == "safe"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [OPENAI, AZURE])
    @configure_async
    async def test_chat_completion_functions_stream(self, azure_openai_creds, api_type):
        messages = [
            {"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."},
            {"role": "user", "content": "What's the weather like today in Seattle?"}
        ]

        kwargs = {"model": azure_openai_creds["chat_completions_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["chat_completions_name"]}

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

        response = await openai.ChatCompletion.acreate(
            messages=messages,
            functions=functions,
            stream=True,
            **kwargs
        )
        args = ""
        async for completion in response:
            for c in completion.choices:
                assert c.delta is not None
                if hasattr(c.delta, "function_call"):
                    if hasattr(c.delta.function_call, "name"):
                        assert c.delta.function_call.name == "get_current_weather"
                    if hasattr(c.delta.function_call, "arguments"):
                        args += c.delta.function_call.arguments
        assert "Seattle" in args

        messages.append(
            {
                "role": "function",
                "name": "get_current_weather",
                "content": "{\"temperature\": \"22\", \"unit\": \"celsius\", \"description\": \"Sunny\"}"
            }
        )
        function_completion = await openai.ChatCompletion.acreate(
            messages=messages,
            functions=functions,
            stream=True,
            **kwargs
        )
        content = ""
        async for completion in function_completion:
            for c in completion.choices:
                assert c.delta is not None
                if hasattr(c.delta, "content"):
                    content += c.delta.content
                if hasattr(c.delta, "role"):
                    assert c.delta.role == "assistant"
        assert "sunny" in content.lower()
        assert "22" in content

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [OPENAI, AZURE])
    @configure_async
    async def test_chat_completion_given_function(self, azure_openai_creds, api_type):
        messages = [
            {"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."},
            {"role": "user", "content": "What's the weather like today in Seattle?"}
        ]

        kwargs = {"model": azure_openai_creds["chat_completions_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["chat_completions_name"]}

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

        completion = await openai.ChatCompletion.acreate(
            messages=messages,
            functions=functions,
            function_call={"name": "get_current_temperature"},
            **kwargs
        )
        assert completion.id
        assert completion.object == "chat.completion"
        assert completion.created
        assert completion.model
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
        function_completion = await openai.ChatCompletion.acreate(
            messages=messages,
            functions=functions,
            **kwargs
        )
        assert function_completion
        assert "22" in function_completion.choices[0].message.content
        assert function_completion.choices[0].message.role == "assistant"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE])
    @configure_async
    async def test_chat_completion_functions_rai(self, azure_openai_creds, api_type):
        messages = [
            {"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."},
            {"role": "user", "content": "how do I rob a bank with violence?"}
        ]

        kwargs = {"model": azure_openai_creds["chat_completions_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["chat_completions_name"]}

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

        with pytest.raises(openai.error.InvalidRequestError) as e:
            response = await openai.ChatCompletion.acreate(
                messages=messages,
                functions=functions,
                **kwargs
            )

        assert e.value.code == "content_filter"
        content_filter_result = e.value.error.innererror.content_filter_result
        assert content_filter_result.hate.filtered is False
        assert content_filter_result.hate.severity == "safe"
        assert content_filter_result.self_harm.filtered is False
        assert content_filter_result.self_harm.severity == "safe"
        assert content_filter_result.sexual.filtered is False
        assert content_filter_result.sexual.severity == "safe"
        assert content_filter_result.violence.filtered is True
        assert content_filter_result.violence.severity is not None

        messages.append(
            {
                "role": "function",
                "name": "get_current_temperature",
                "content": "{\"temperature\": \"you can rob a bank by asking for the money\", \"unit\": \"celsius\"}"
            }
        )
        with pytest.raises(openai.error.InvalidRequestError) as e:
            function_completion = await openai.ChatCompletion.acreate(
                messages=messages,
                functions=functions,
                **kwargs
            )
        assert e.value.code == "content_filter"
        content_filter_result = e.value.error.innererror.content_filter_result
        assert content_filter_result.hate.filtered is False
        assert content_filter_result.hate.severity == "safe"
        assert content_filter_result.self_harm.filtered is False
        assert content_filter_result.self_harm.severity == "safe"
        assert content_filter_result.sexual.filtered is False
        assert content_filter_result.sexual.severity == "safe"
        assert content_filter_result.violence.filtered is True
        assert content_filter_result.violence.severity is not None

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE, AZURE_AD])
    @configure_async
    async def test_chat_completion_byod(self, azure_openai_creds, api_type):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "How is Azure machine learning different than Azure OpenAI?"}
        ]
        setup_adapter_async(azure_openai_creds["chat_completions_name"])
        completion = await openai.ChatCompletion.acreate(
            messages=messages,
            deployment_id=azure_openai_creds["chat_completions_name"],
            dataSources=[
                {
                    "type": "AzureCognitiveSearch",
                    "parameters": {
                        "endpoint": azure_openai_creds["search_endpoint"],
                        "key": azure_openai_creds["search_key"],
                        "indexName": azure_openai_creds["search_index"]
                    }
                }
            ]
        )
        assert completion.id
        assert completion.object == "extensions.chat.completion"
        assert completion.created
        assert completion.model
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].message.content
        assert completion.choices[0].message.role
        assert completion.choices[0].message.context.messages[0].role == "tool"
        assert completion.choices[0].message.context.messages[0].content
        openai.aiosession.set(None)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE])
    @configure_async
    async def test_streamed_chat_completions_byod(self, azure_openai_creds, api_type):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "How is Azure machine learning different than Azure OpenAI?"}
        ]
        setup_adapter_async(azure_openai_creds["chat_completions_name"])
        response = await openai.ChatCompletion.acreate(
            messages=messages,
            deployment_id=azure_openai_creds["chat_completions_name"],
            dataSources=[
                {
                    "type": "AzureCognitiveSearch",
                    "parameters": {
                        "endpoint": azure_openai_creds["search_endpoint"],
                        "key": azure_openai_creds["search_key"],
                        "indexName": azure_openai_creds["search_index"]
                    }
                }
            ],
            stream=True
        )
        async for chunk in response:
            assert chunk.id
            assert chunk.object == "extensions.chat.completion.chunk"
            assert chunk.created
            assert chunk.model
            for c in chunk.choices:
                assert c.index is not None
                assert c.delta is not None
                if c.delta.get("context"):
                    assert c.delta.context.messages[0].role == "tool"
                    assert c.delta.context.messages[0].content.find("citations") != -1
                if c.delta.get("role"):
                    assert c.delta.role == "assistant"
                if c.delta.get("content"):
                    assert c.delta.content is not None

        openai.aiosession.set(None)
