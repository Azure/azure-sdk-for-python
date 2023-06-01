# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import openai
from devtools_testutils import AzureRecordedTestCase


class TestCompletions(AzureRecordedTestCase):
    """Missing tests for keyword argument `suffix`"""

    def test_completion_bad_deployment_name(self, azure_openai_creds):
        with pytest.raises(openai.error.InvalidRequestError) as e:
            openai.Completion.create(prompt="hello world", deployment_id="deployment")
        assert e.value.http_status == 404
        assert "The API deployment for this resource does not exist" in str(e.value)

    def test_completion_kw_input(self, azure_openai_creds):
        deployment = azure_openai_creds["completions_name"]

        completion = openai.Completion.create(prompt="hello world", deployment_id=deployment)
        assert completion
        completion = openai.Completion.create(prompt="hello world", engine=deployment)
        assert completion
        with pytest.raises(openai.error.InvalidRequestError) as e:
            openai.Completion.create(prompt="hello world", model=deployment)
        assert "Must provide an 'engine' or 'deployment_id' parameter" in str(e.value)

    def test_completion(self, azure_openai_creds):
        deployment = azure_openai_creds["completions_name"]

        completion = openai.Completion.create(prompt="hello world", deployment_id=deployment)
        assert completion.id
        assert completion.object == "text_completion"
        assert completion.created
        assert completion.model
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].text

    def test_batched_completions(self, azure_openai_creds):
        deployment = azure_openai_creds["completions_name"]

        completion = openai.Completion.create(prompt=["hello world", "how are you today?"], deployment_id=deployment)
        assert completion.id
        assert completion.object == "text_completion"
        assert completion.created
        assert completion.model
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 2
        for c in completion.choices:
            assert c.finish_reason
            assert c.index is not None
            assert c.text

    @pytest.mark.skip("openai.error.APIError: Invalid response object from API: 'Unsupported data type\n' (HTTP response code was 400)")
    def test_completion_token_input(self, azure_openai_creds):
        deployment = azure_openai_creds["completions_name"]
 
        completion = openai.Completion.create(prompt=[10919, 3124, 318, 281, 17180, 30], deployment_id=deployment)
        assert completion.id
        assert completion.object == "text_completion"
        assert completion.created
        assert completion.model
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 2
        for c in completion.choices:
            assert c.finish_reason
            assert c.index is not None
            assert c.text

    def test_streamed_completions(self, azure_openai_creds):
        deployment = azure_openai_creds["completions_name"]

        response = openai.Completion.create(prompt="hello world", deployment_id=deployment, stream=True)

        for completion in response:
            assert completion.id
            assert completion.object == "text_completion"
            assert completion.created
            assert completion.model
            for c in completion.choices:
                assert c.index is not None
                assert c.text is not None

    def test_completion_max_tokens(self, azure_openai_creds):
        deployment = azure_openai_creds["completions_name"]

        completion = openai.Completion.create(
            prompt="How do I bake a chocolate cake?",
            deployment_id=deployment,
            max_tokens=50
        )

        assert completion.id
        assert completion.object == "text_completion"
        assert completion.created
        assert completion.model
        assert completion.usage.completion_tokens <= 50
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].text

    def test_completion_content_filter_prompt(self, azure_openai_creds):
        deployment = azure_openai_creds["completions_name"]

        with pytest.raises(openai.error.InvalidRequestError) as e:
            openai.Completion.create(
                prompt="How do I rob a bank?",
                deployment_id=deployment,
            )
        assert e.value.http_status == 400
        assert e.value.error.code == "content_filter"
        assert "The response was filtered due to the prompt triggering Azure OpenAI’s content management policy" in str(e.value)

    def test_completion_temperature(self, azure_openai_creds):
        deployment = azure_openai_creds["completions_name"]

        completion = openai.Completion.create(
            prompt="How do I bake a chocolate cake?",
            deployment_id=deployment,
            temperature=0.8
        )

        assert completion.id
        assert completion.object == "text_completion"
        assert completion.created
        assert completion.model
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].text

    def test_completion_top_p(self, azure_openai_creds):
        deployment = azure_openai_creds["completions_name"]

        completion = openai.Completion.create(
            prompt="How do I bake a chocolate cake?",
            deployment_id=deployment,
            top_p=0.1
        )

        assert completion.id
        assert completion.object == "text_completion"
        assert completion.created
        assert completion.model
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].text

    def test_completion_n(self, azure_openai_creds):
        deployment = azure_openai_creds["completions_name"]

        completion = openai.Completion.create(
            prompt="hello world",
            deployment_id=deployment,
            n=3
        )

        assert completion.id
        assert completion.object == "text_completion"
        assert completion.created
        assert completion.model
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 3
        for idx, c in enumerate(completion.choices):
            assert c.index == idx
            assert c.text

    def test_completion_logprobs(self, azure_openai_creds):
        deployment = azure_openai_creds["completions_name"]

        completion = openai.Completion.create(
            prompt="How do I bake a chocolate cake?",
            deployment_id=deployment,
            logprobs=2
        )

        assert completion.id
        assert completion.object == "text_completion"
        assert completion.created
        assert completion.model
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].text
        assert completion.choices[0].logprobs.tokens
        assert completion.choices[0].logprobs.token_logprobs
        assert completion.choices[0].logprobs.top_logprobs
        assert completion.choices[0].logprobs.text_offset

    def test_completion_echo(self, azure_openai_creds):
        deployment = azure_openai_creds["completions_name"]
        prompt = "How do I bake a chocolate cake?"
        completion = openai.Completion.create(
            prompt=prompt,
            deployment_id=deployment,
            echo=True
        )

        assert completion.id
        assert completion.object == "text_completion"
        assert completion.created
        assert completion.model
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert prompt in completion.choices[0].text

    def test_completion_stop(self, azure_openai_creds):
        deployment = azure_openai_creds["completions_name"]
        completion = openai.Completion.create(
            prompt="How do I bake a chocolate cake?",
            deployment_id=deployment,
            stop=" "
        )

        assert completion.id
        assert completion.object == "text_completion"
        assert completion.created
        assert completion.model
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].index is not None
        assert completion.choices[0].text

    def test_completion_token_penalty(self, azure_openai_creds):
        deployment = azure_openai_creds["completions_name"]
        completion = openai.Completion.create(
            prompt="How do I bake a chocolate cake?",
            deployment_id=deployment,
            presence_penalty=2,
            frequency_penalty=2
        )

        assert completion.id
        assert completion.object == "text_completion"
        assert completion.created
        assert completion.model
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].text

    def test_completion_best_of(self, azure_openai_creds):
        deployment = azure_openai_creds["completions_name"]
        completion = openai.Completion.create(
            prompt="How do I bake a chocolate cake?",
            deployment_id=deployment,
            best_of=2,
            max_tokens=50
        )

        assert completion.id
        assert completion.object == "text_completion"
        assert completion.created
        assert completion.model
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].text

    def test_completion_user(self, azure_openai_creds):
        deployment = azure_openai_creds["completions_name"]
        completion = openai.Completion.create(
            prompt="How do I bake a chocolate cake?",
            deployment_id=deployment,
            user="krista"
        )

        assert completion.id
        assert completion.object == "text_completion"
        assert completion.created
        assert completion.model
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].text

    def test_completion_logit_bias(self, azure_openai_creds):
        deployment = azure_openai_creds["completions_name"]
        completion = openai.Completion.create(
            prompt="What color is the ocean?",
            deployment_id=deployment,
            logit_bias={17585: -100, 14573: -100}
        )

        assert completion.id
        assert completion.object == "text_completion"
        assert completion.created
        assert completion.model
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].text
