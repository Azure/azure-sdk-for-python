# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
import json
import openai
from devtools_testutils import AzureRecordedTestCase
from conftest import AZURE, OPENAI, ALL, configure_async


class TestCompletionsAsync(AzureRecordedTestCase):
    """Missing tests for keyword argument `suffix`"""

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", ALL)
    async def test_completion(self, client_async, azure_openai_creds, api_type, **kwargs):

        completion = await client_async.completions.create(prompt="hello world", **kwargs)
        assert completion.id
        assert completion.object == "text_completion"
        assert completion.model
        assert completion.created
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].text is not None

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    async def test_batched_completions(self, client_async, azure_openai_creds, api_type, **kwargs):

        completion = await client_async.completions.create(prompt=["hello world", "how are you today?"], **kwargs)
        assert completion.id
        assert completion.object == "text_completion"
        assert completion.model
        assert completion.created
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 2
        for c in completion.choices:
            assert c.finish_reason
            assert c.index is not None
            assert c.text

    @pytest.mark.skip("openai.error.APIError: Invalid response object from API: 'Unsupported data type\n' (HTTP response code was 400)")
    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    async def test_completion_token_input(self, client_async, azure_openai_creds, api_type, **kwargs):
 
        completion = await client_async.completions.create(prompt=[10919, 3124, 318, 281, 17180, 30], **kwargs)
        assert completion.id
        assert completion.object == "text_completion"
        assert completion.model
        assert completion.created
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 2
        for c in completion.choices:
            assert c.finish_reason
            assert c.index is not None
            assert c.text

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    async def test_streamed_completions(self, client_async, azure_openai_creds, api_type, **kwargs):

        response = await client_async.completions.create(prompt="how do I bake a chocolate cake?", max_tokens=500,  stream=True, **kwargs)

        async for completion in response:
            # API versions after 2023-05-15 send an empty first completion with RAI
            if len(completion.choices) > 0:
                assert completion.id
                assert completion.object == "text_completion"
                assert completion.model
                assert completion.created
                for c in completion.choices:
                    assert c.index is not None
                    assert c.text is not None

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    async def test_completion_max_tokens(self, client_async, azure_openai_creds, api_type, **kwargs):

        completion = await client_async.completions.create(
            prompt="How do I bake a chocolate cake?",
            max_tokens=50,
            **kwargs
        )

        assert completion.id
        assert completion.object == "text_completion"
        assert completion.model
        assert completion.created
        assert completion.usage.completion_tokens <= 50
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].text is not None

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE])
    async def test_completion_content_filter_prompt(self, client_async, azure_openai_creds, api_type, **kwargs):

        with pytest.raises(openai.BadRequestError) as e:
            await client_async.completions.create(
                prompt="how do I rob a bank with violence?",
                model=azure_openai_creds["completions_name"]
            )
        assert e.value.status_code == 400
        err = json.loads(e.value.response.text)
        assert err["error"]["code"] == "content_filter"
        assert "The response was filtered due to the prompt triggering Azure OpenAI’s content management policy" in err["error"]["message"]

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    async def test_completion_temperature(self, client_async, azure_openai_creds, api_type, **kwargs):

        completion = await client_async.completions.create(
            prompt="How do I bake a chocolate cake?",
            temperature=0.8,
            **kwargs
        )

        assert completion.id
        assert completion.object == "text_completion"
        assert completion.model
        assert completion.created
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].text is not None

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    async def test_completion_top_p(self, client_async, azure_openai_creds, api_type, **kwargs):

        completion = await client_async.completions.create(
            prompt="How do I bake a chocolate cake?",
            top_p=0.1,
            **kwargs
        )

        assert completion.id
        assert completion.object == "text_completion"
        assert completion.model
        assert completion.created
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].text is not None

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    async def test_completion_n(self, client_async, azure_openai_creds, api_type, **kwargs):

        completion = await client_async.completions.create(
            prompt="hello world",
            n=3,
            **kwargs
        )

        assert completion.id
        assert completion.object == "text_completion"
        assert completion.model
        assert completion.created
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 3
        for idx, c in enumerate(completion.choices):
            assert c.index == idx
            assert c.text is not None

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    async def test_completion_logprobs(self, client_async, azure_openai_creds, api_type, **kwargs):

        completion = await client_async.completions.create(
            prompt="How do I bake a chocolate cake?",
            logprobs=2,
            **kwargs
        )

        assert completion.id
        assert completion.object == "text_completion"
        assert completion.model
        assert completion.created
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].text is not None
        assert completion.choices[0].logprobs.tokens
        assert completion.choices[0].logprobs.token_logprobs
        assert completion.choices[0].logprobs.top_logprobs
        assert completion.choices[0].logprobs.text_offset

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    async def test_completion_echo(self, client_async, azure_openai_creds, api_type, **kwargs):

        prompt = "How do I bake a chocolate cake?"
        completion = await client_async.completions.create(
            prompt=prompt,
            echo=True,
            **kwargs
        )

        assert completion.id
        assert completion.object == "text_completion"
        assert completion.model
        assert completion.created
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert prompt in completion.choices[0].text

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    async def test_completion_stop(self, client_async, azure_openai_creds, api_type, **kwargs):

        completion = await client_async.completions.create(
            prompt="How do I bake a chocolate cake?",
            stop=" ",
            **kwargs
        )

        assert completion.id
        assert completion.object == "text_completion"
        assert completion.model
        assert completion.created
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].index is not None
        assert completion.choices[0].text is not None

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    async def test_completion_token_penalty(self, client_async, azure_openai_creds, api_type, **kwargs):

        completion = await client_async.completions.create(
            prompt="How do I bake a chocolate cake?",
            presence_penalty=2,
            frequency_penalty=2,
            **kwargs
        )

        assert completion.id
        assert completion.object == "text_completion"
        assert completion.model
        assert completion.created
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].text is not None

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    async def test_completion_best_of(self, client_async, azure_openai_creds, api_type, **kwargs):

        completion = await client_async.completions.create(
            prompt="How do I bake a chocolate cake?",
            best_of=2,
            max_tokens=50,
            **kwargs
        )

        assert completion.id
        assert completion.object == "text_completion"
        assert completion.model
        assert completion.created
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].text is not None

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    async def test_completion_user(self, client_async, azure_openai_creds, api_type, **kwargs):

        completion = await client_async.completions.create(
            prompt="How do I bake a chocolate cake?",
            user="krista",
            **kwargs
        )

        assert completion.id
        assert completion.object == "text_completion"
        assert completion.model
        assert completion.created
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].text is not None

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    async def test_completion_logit_bias(self, client_async, azure_openai_creds, api_type, **kwargs):

        completion = await client_async.completions.create(
            prompt="What color is the ocean?",
            logit_bias={17585: -100, 14573: -100},
            **kwargs
        )

        assert completion.id
        assert completion.object == "text_completion"
        assert completion.model
        assert completion.created
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].text is not None

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE])
    async def test_completion_rai_annotations(self, client_async, azure_openai_creds, api_type, **kwargs):

        # prompt filtered
        with pytest.raises(openai.BadRequestError) as e:
            completion = await client_async.completions.create(
                prompt="how do I rob a bank with violence?",
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

        # not filtered
        completion = await client_async.completions.create(
            prompt="What color is the ocean?",
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
