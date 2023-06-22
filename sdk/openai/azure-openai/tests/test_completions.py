# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import openai
from devtools_testutils import AzureRecordedTestCase
from conftest import configure, AZURE, OPENAI, ALL


class TestCompletions(AzureRecordedTestCase):
    """Missing tests for keyword argument `suffix`"""

    @pytest.mark.parametrize("api_type", [AZURE])
    @configure
    def test_completion_bad_deployment_name(self, azure_openai_creds, api_type):
        with pytest.raises(openai.error.InvalidRequestError) as e:
            openai.Completion.create(prompt="hello world", deployment_id="deployment")
        assert e.value.http_status == 404
        assert "The API deployment for this resource does not exist" in str(e.value)

    @pytest.mark.parametrize("api_type", [AZURE])
    @configure
    def test_completion_kw_input(self, azure_openai_creds, api_type):
        deployment = azure_openai_creds["completions_name"]

        completion = openai.Completion.create(prompt="hello world", deployment_id=deployment)
        assert completion
        completion = openai.Completion.create(prompt="hello world", engine=deployment)
        assert completion
        with pytest.raises(openai.error.InvalidRequestError) as e:
            openai.Completion.create(prompt="hello world", model=deployment)
        assert "Must provide an 'engine' or 'deployment_id' parameter" in str(e.value)

    @pytest.mark.parametrize("api_type", [ALL])
    @configure
    def test_completion(self, azure_openai_creds, api_type):
        kwargs = {"model": azure_openai_creds["completions_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["completions_name"]}

        completion = openai.Completion.create(prompt="hello world", **kwargs)
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

    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure
    def test_batched_completions(self, azure_openai_creds, api_type):
        kwargs = {"model": azure_openai_creds["completions_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["completions_name"]}

        completion = openai.Completion.create(prompt=["hello world", "how are you today?"], **kwargs)
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
    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure
    def test_completion_token_input(self, azure_openai_creds, api_type):
        kwargs = {"model": azure_openai_creds["completions_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["completions_name"]}
 
        completion = openai.Completion.create(prompt=[10919, 3124, 318, 281, 17180, 30], **kwargs)
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

    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure
    def test_streamed_completions(self, azure_openai_creds, api_type):
        kwargs = {"model": azure_openai_creds["completions_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["completions_name"]}

        response = openai.Completion.create(prompt="hello world", stream=True, **kwargs)

        for completion in response:
            assert completion.id
            assert completion.object == "text_completion"
            assert completion.created
            assert completion.model
            for c in completion.choices:
                assert c.index is not None
                assert c.text is not None

    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure
    def test_completion_max_tokens(self, azure_openai_creds, api_type):
        kwargs = {"model": azure_openai_creds["completions_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["completions_name"]}

        completion = openai.Completion.create(
            prompt="How do I bake a chocolate cake?",
            max_tokens=50,
            **kwargs
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

    @pytest.mark.parametrize("api_type", [AZURE])
    @configure
    def test_completion_content_filter_prompt(self, azure_openai_creds, api_type):
        deployment = azure_openai_creds["completions_name"]

        with pytest.raises(openai.error.InvalidRequestError) as e:
            openai.Completion.create(
                prompt="How do I rob a bank?",
                deployment_id=deployment,
            )
        assert e.value.http_status == 400
        assert e.value.error.code == "content_filter"
        assert "The response was filtered due to the prompt triggering Azure OpenAI’s content management policy" in str(e.value)

    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure
    def test_completion_temperature(self, azure_openai_creds, api_type):
        kwargs = {"model": azure_openai_creds["completions_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["completions_name"]}

        completion = openai.Completion.create(
            prompt="How do I bake a chocolate cake?",
            temperature=0.8,
            **kwargs
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

    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure
    def test_completion_top_p(self, azure_openai_creds, api_type):
        kwargs = {"model": azure_openai_creds["completions_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["completions_name"]}

        completion = openai.Completion.create(
            prompt="How do I bake a chocolate cake?",
            top_p=0.1,
            **kwargs
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

    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure
    def test_completion_n(self, azure_openai_creds, api_type):
        kwargs = {"model": azure_openai_creds["completions_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["completions_name"]}

        completion = openai.Completion.create(
            prompt="hello world",
            n=3,
            **kwargs
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

    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure
    def test_completion_logprobs(self, azure_openai_creds, api_type):
        kwargs = {"model": azure_openai_creds["completions_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["completions_name"]}

        completion = openai.Completion.create(
            prompt="How do I bake a chocolate cake?",
            logprobs=2,
            **kwargs
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

    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure
    def test_completion_echo(self, azure_openai_creds, api_type):
        kwargs = {"model": azure_openai_creds["completions_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["completions_name"]}

        prompt = "How do I bake a chocolate cake?"
        completion = openai.Completion.create(
            prompt=prompt,
            echo=True,
            **kwargs
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

    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure
    def test_completion_stop(self, azure_openai_creds, api_type):
        kwargs = {"model": azure_openai_creds["completions_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["completions_name"]}

        completion = openai.Completion.create(
            prompt="How do I bake a chocolate cake?",
            stop=" ",
            **kwargs
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

    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure
    def test_completion_token_penalty(self, azure_openai_creds, api_type):
        kwargs = {"model": azure_openai_creds["completions_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["completions_name"]}

        completion = openai.Completion.create(
            prompt="How do I bake a chocolate cake?",
            presence_penalty=2,
            frequency_penalty=2,
            **kwargs
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

    @pytest.mark.parametrize("api_type", [AZURE])
    @configure
    def test_completion_best_of(self, azure_openai_creds, api_type):
        kwargs = {"model": azure_openai_creds["completions_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["completions_name"]}

        completion = openai.Completion.create(
            prompt="How do I bake a chocolate cake?",
            best_of=2,
            max_tokens=50,
            **kwargs
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

    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure
    def test_completion_user(self, azure_openai_creds, api_type):
        kwargs = {"model": azure_openai_creds["completions_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["completions_name"]}

        completion = openai.Completion.create(
            prompt="How do I bake a chocolate cake?",
            user="krista",
            **kwargs
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

    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure
    def test_completion_logit_bias(self, azure_openai_creds, api_type):
        kwargs = {"model": azure_openai_creds["completions_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["completions_name"]}

        completion = openai.Completion.create(
            prompt="What color is the ocean?",
            logit_bias={17585: -100, 14573: -100},
            **kwargs
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

    @pytest.mark.parametrize("api_type", [AZURE])
    @configure
    def test_completion_rai_annotations(self, azure_openai_creds, api_type):
        kwargs = {"model": azure_openai_creds["completions_model"]} if api_type == "openai" \
          else {"deployment_id": azure_openai_creds["completions_name"]}

        # prompt filtered
        with pytest.raises(openai.error.InvalidRequestError) as e:
            completion = openai.Completion.create(
                prompt="how do I rob a bank?",
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
        completion = openai.Completion.create(
            prompt="What color is the ocean?",
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
