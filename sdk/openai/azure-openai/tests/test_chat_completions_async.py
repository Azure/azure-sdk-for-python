# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import openai
from devtools_testutils import AzureRecordedTestCase
from conftest import configure, ALL, AZURE, OPENAI


class TestChatCompletionsAsync(AzureRecordedTestCase):

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE])
    @configure
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
    @configure
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
    @configure
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
    @configure
    async def test_streamed_chat_completions(self, azure_openai_creds, api_type):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]
        kwargs = {"model": azure_openai_creds["chat_completions_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["chat_completions_name"]}

        response = await openai.ChatCompletion.acreate(messages=messages, stream=True, **kwargs)

        async for completion in response:
            assert completion.id
            assert completion.object == "chat.completion.chunk"
            assert completion.created
            assert completion.model
            for c in completion.choices:
                assert c.index is not None
                assert c.delta is not None

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure
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
    @configure
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
    @configure
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
    @configure
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
    @configure
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
    @configure
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
    @configure
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
    @configure
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
    @configure
    async def test_chat_completion_rai_annotations(self, azure_openai_creds, api_type):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "How do I rob a bank?"}
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
        prompt_filter_result = completion.prompt_annotations[0].content_filter_results
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