# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import openai
from devtools_testutils import AzureRecordedTestCase


class TestChatCompletions(AzureRecordedTestCase):

    def test_chat_completion_bad_deployment_name(self, azure_openai_creds):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]
        with pytest.raises(openai.error.InvalidRequestError) as e:
            openai.ChatCompletion.create(messages=messages, deployment_id="deployment")
        assert e.value.http_status == 404
        assert "The API deployment for this resource does not exist" in str(e.value)

    def test_chat_completion_kw_input(self, azure_openai_creds):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]
        deployment = azure_openai_creds["chat_completions_name"]

        completion = openai.ChatCompletion.create(messages=messages, deployment_id=deployment)
        assert completion
        completion = openai.ChatCompletion.create(messages=messages, engine=deployment)
        assert completion
        with pytest.raises(openai.error.InvalidRequestError) as e:
            openai.ChatCompletion.create(messages=messages, model=deployment)
        assert "Must provide an 'engine' or 'deployment_id' parameter" in str(e.value)

    def test_chat_completion(self, azure_openai_creds):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]
        deployment = azure_openai_creds["chat_completions_name"]

        completion = openai.ChatCompletion.create(messages=messages, deployment_id=deployment)
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

    def test_streamed_chat_completions(self, azure_openai_creds):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]
        deployment = azure_openai_creds["chat_completions_name"]

        response = openai.ChatCompletion.create(messages=messages, deployment_id=deployment, stream=True)

        for completion in response:
            assert completion.id
            assert completion.object == "chat.completion.chunk"
            assert completion.created
            assert completion.model
            for c in completion.choices:
                assert c.index is not None
                assert c.delta is not None

    def test_chat_completion_max_tokens(self, azure_openai_creds):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]
        deployment = azure_openai_creds["chat_completions_name"]

        completion = openai.ChatCompletion.create(messages=messages, deployment_id=deployment, max_tokens=50)

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

    def test_chat_completion_temperature(self, azure_openai_creds):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]
        deployment = azure_openai_creds["chat_completions_name"]

        completion = openai.ChatCompletion.create(messages=messages, deployment_id=deployment, temperature=0.8)

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

    def test_chat_completion_top_p(self, azure_openai_creds):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]
        deployment = azure_openai_creds["chat_completions_name"]

        completion = openai.ChatCompletion.create(messages=messages, deployment_id=deployment, top_p=0.1)

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

    def test_chat_completion_n(self, azure_openai_creds):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]
        deployment = azure_openai_creds["chat_completions_name"]

        completion = openai.ChatCompletion.create(messages=messages, deployment_id=deployment, n=2)

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

    def test_chat_completion_stop(self, azure_openai_creds):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]
        deployment = azure_openai_creds["chat_completions_name"]

        completion = openai.ChatCompletion.create(messages=messages, deployment_id=deployment, stop=" ")

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

    def test_chat_completion_token_penalty(self, azure_openai_creds):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]
        deployment = azure_openai_creds["chat_completions_name"]

        completion = openai.ChatCompletion.create(
            messages=messages,
            deployment_id=deployment,
            presence_penalty=2,
            frequency_penalty=2
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

    def test_chat_completion_user(self, azure_openai_creds):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]
        deployment = azure_openai_creds["chat_completions_name"]

        completion = openai.ChatCompletion.create(
            messages=messages,
            deployment_id=deployment,
            user="krista"
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

    def test_chat_completion_logit_bias(self, azure_openai_creds):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What color is the ocean?"}
        ]
        deployment = azure_openai_creds["chat_completions_name"]

        completion = openai.ChatCompletion.create(
            deployment_id=deployment,
            messages=messages,
            logit_bias={17585: -100, 14573: -100}
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