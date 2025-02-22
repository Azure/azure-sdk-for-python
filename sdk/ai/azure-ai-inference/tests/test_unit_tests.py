# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import json
import azure.ai.inference as sdk

from typing import List
from model_inference_test_base import ModelClientTestBase, HttpResponseForUnitTests, AsyncHttpResponseForUnitTests


# The test class name needs to start with "Test" to get collected by pytest
class TestUnitTests(ModelClientTestBase):

    # **********************************************************************************
    #
    #                               UNIT TESTS
    #
    # **********************************************************************************

    # Test custom class UserMessage(), which allow specifying "content" as a positional argument
    def test_user_message(self, **kwargs):

        # Verify that all these objects get serialized into the same dictionary
        messages = [
            sdk.models.UserMessage(content="some content"),
            sdk.models.UserMessage("some content"),
            sdk.models.UserMessage({"role": "user", "content": "some content"}),
        ]
        for message in messages:
            assert message.as_dict() == {"role": "user", "content": "some content"}

        # Also verify that these two objects get serialized into the same dictionary
        messages = [
            sdk.models.UserMessage(
                content=[
                    sdk.models.TextContentItem(text="some text"),
                    sdk.models.ImageContentItem(
                        image_url=sdk.models.ImageUrl(
                            url="https://does.not.exit/image.png",
                            detail=sdk.models.ImageDetailLevel.HIGH,
                        ),
                    ),
                ],
            ),
            sdk.models.UserMessage(
                [
                    sdk.models.TextContentItem(text="some text"),
                    sdk.models.ImageContentItem(
                        image_url=sdk.models.ImageUrl(
                            url="https://does.not.exit/image.png",
                            detail=sdk.models.ImageDetailLevel.HIGH,
                        ),
                    ),
                ],
            ),
        ]
        for message in messages:
            assert message.as_dict() == {
                "role": "user",
                "content": [
                    {"text": "some text", "type": "text"},
                    {"type": "image_url", "image_url": {"detail": "high", "url": "https://does.not.exit/image.png"}},
                ],
            }

        # Test invalid input arguments
        try:
            _ = (sdk.models.UserMessage("some content", content="some content"),)
            assert False
        except ValueError as e:
            assert str(e) == "content cannot be provided as positional and keyword arguments"

    # Test custom class SystemMessage(), which allow specifying "content" as a positional argument
    def test_system_message(self, **kwargs):

        # Verify that all these objects get serialized into the same dictionary
        messages = [
            sdk.models.SystemMessage(content="some content"),
            sdk.models.SystemMessage("some content"),
            sdk.models.SystemMessage({"role": "system", "content": "some content"}),
        ]
        for message in messages:
            assert message.as_dict() == {"role": "system", "content": "some content"}

        # Test invalid input arguments
        try:
            _ = (sdk.models.SystemMessage("some content", content="some content"),)
            assert False
        except ValueError as e:
            assert str(e) == "content cannot be provided as positional and keyword arguments"

    # Test custom class DeveloperMessage(), which allow specifying "content" as a positional argument
    def test_developer_message(self, **kwargs):

        # Verify that all these objects get serialized into the same dictionary
        messages = [
            sdk.models.DeveloperMessage(content="some content"),
            sdk.models.DeveloperMessage("some content"),
            sdk.models.DeveloperMessage({"role": "developer", "content": "some content"}),
        ]
        for message in messages:
            assert message.as_dict() == {"role": "developer", "content": "some content"}

        # Test invalid input arguments
        try:
            _ = (sdk.models.DeveloperMessage("some content", content="some content"),)
            assert False
        except ValueError as e:
            assert str(e) == "content cannot be provided as positional and keyword arguments"

    # Test custom class AssistantMessage(), which allow specifying "content" as a positional argument
    def test_assistant_message(self, **kwargs):

        # Verify that all these objects get serialized into the same dictionary
        messages = [
            sdk.models.AssistantMessage(content="some content"),
            sdk.models.AssistantMessage("some content"),
            sdk.models.AssistantMessage({"role": "assistant", "content": "some content"}),
        ]
        for message in messages:
            assert message.as_dict() == {"role": "assistant", "content": "some content"}

        # Also verify that these two objects get serialized into the same dictionary
        messages = [
            sdk.models.AssistantMessage(
                content="some content",
                tool_calls=[
                    sdk.models.ChatCompletionsToolCall(
                        function=sdk.models.FunctionCall(
                            name="my-first-function-name",
                            arguments={"first_argument": "value1", "second_argument": "value2"},
                        ),
                        id="some-id",
                    ),
                ],
            ),
            sdk.models.AssistantMessage(
                "some content",
                tool_calls=[
                    sdk.models.ChatCompletionsToolCall(
                        function=sdk.models.FunctionCall(
                            name="my-first-function-name",
                            arguments={"first_argument": "value1", "second_argument": "value2"},
                        ),
                        id="some-id",
                    ),
                ],
            ),
        ]
        for message in messages:
            assert message.as_dict() == {
                "role": "assistant",
                "content": "some content",
                "tool_calls": [
                    {
                        "function": {
                            "name": "my-first-function-name",
                            "arguments": {"first_argument": "value1", "second_argument": "value2"},
                        },
                        "id": "some-id",
                        "type": "function",
                    }
                ],
            }

        # Also check the case where the "content" is not present
        message = sdk.models.AssistantMessage(
            tool_calls=[
                sdk.models.ChatCompletionsToolCall(
                    function=sdk.models.FunctionCall(
                        name="my-first-function-name",
                        arguments={"first_argument": "value1", "second_argument": "value2"},
                    ),
                    id="some-id",
                ),
            ],
        )
        assert message.as_dict() == {
            "role": "assistant",
            "tool_calls": [
                {
                    "function": {
                        "name": "my-first-function-name",
                        "arguments": {"first_argument": "value1", "second_argument": "value2"},
                    },
                    "id": "some-id",
                    "type": "function",
                }
            ],
        }

        # Test invalid input arguments
        try:
            _ = (sdk.models.AssistantMessage("some content", content="some content"),)
            assert False
        except ValueError as e:
            assert str(e) == "content cannot be provided as positional and keyword arguments"

    # Test custom class ToolMessage(), which allow specifying "content" as a positional argument
    def test_tool_message(self, **kwargs):

        # Verify that all these objects get serialized into the same dictionary
        messages = [
            sdk.models.ToolMessage(content="some content"),
            sdk.models.ToolMessage("some content"),
            sdk.models.ToolMessage({"role": "tool", "content": "some content"}),
        ]
        for message in messages:
            assert message.as_dict() == {"role": "tool", "content": "some content"}

        # Verify that all these objects get serialized into the same dictionary. This time with tool call ID.
        messages = [
            sdk.models.ToolMessage(content="some content", tool_call_id="some-id"),
            sdk.models.ToolMessage("some content", tool_call_id="some-id"),
            sdk.models.ToolMessage({"role": "tool", "content": "some content", "tool_call_id": "some-id"}),
        ]
        for message in messages:
            assert message.as_dict() == {"role": "tool", "content": "some content", "tool_call_id": "some-id"}

        # Test invalid input arguments
        try:
            _ = (sdk.models.ToolMessage("some content", content="some content"),)
            assert False
        except ValueError as e:
            assert str(e) == "content cannot be provided as positional and keyword arguments"

    # Test custom code in ChatCompletions class to print its content in a nice multi-line JSON format
    def test_print_method_of_chat_completions_class(self, **kwargs):
        response = sdk.models.ChatCompletions(
            {
                "choices": [
                    {
                        "message": {
                            "content": "some content",
                            "role": "assistant",
                        }
                    }
                ]
            }
        )
        print(response)  # This will invoke the customized __str__ method
        assert json.dumps(response.as_dict(), indent=2) == response.__str__()

    # Test custom code in EmbeddingsResult class to print its content in a nice multi-line JSON format
    def test_print_method_of_embeddings_result_class(self, **kwargs):
        response = sdk.models.ChatCompletions(
            {
                "id": "f060ce24-0bbf-4aef-8341-62659b6e19be",
                "data": [
                    {
                        "index": 0,
                        "embedding": [
                            0.0013399124,
                            -0.01576233,
                        ],
                    },
                    {
                        "index": 1,
                        "embedding": [
                            0.036590576,
                            -0.0059547424,
                        ],
                    },
                ],
                "model": "model-name",
                "usage": {"prompt_tokens": 6, "completion_tokens": 0, "total_tokens": 6},
            }
        )
        print(response)  # This will invoke the customized __str__ method
        assert json.dumps(response.as_dict(), indent=2) == response.__str__()

    # Test custom code in ImageUrl class to load an image file
    def test_image_url_load(self, **kwargs):
        local_folder = os.path.dirname(os.path.abspath(__file__))
        image_file = os.path.join(local_folder, "test_image1.png")
        image_url = sdk.models.ImageUrl.load(
            image_file=image_file,
            image_format="png",
            detail=sdk.models.ImageDetailLevel.AUTO,
        )
        assert image_url
        assert image_url.url.startswith("data:image/png;base64,iVBORw")
        assert image_url.detail == sdk.models.ImageDetailLevel.AUTO

    # Test custom code in ImageEmbeddingInput class to load an image file
    def test_image_embedding_input_load(self, **kwargs):
        image_embedding_input = ModelClientTestBase._get_image_embeddings_input()
        assert image_embedding_input
        assert image_embedding_input.image.startswith(
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEsAAAApCAYAAAB9ctS7AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsEAAA7BAbiRa+0AAB0CSURBVGhDRZpZzK33ddbXnufh2"
        )
        assert image_embedding_input.text == "some text"

    # **********************************************************************************
    #
    #            UNIT TESTS (REGRESSION TESTS) FOR STREAMING RESPONSE PARSING
    #
    # **********************************************************************************

    # Recorded from real chat completions streaming response
    # - Using sample code `samples\sample_chat_completions_streaming.py`,
    # - With SSE logging turned on (_ENABLE_CLASS_LOGS = True`),
    # - With Mistral Large model, with user message "how many feet are in a mile?", with content safety turned on.
    # - The bytes below are from the log output of `[Original element]`.
    STREAMING_RESPONSE_BYTES: List[bytes] = [
        b'data: {"choices":[{"delta":{"content":"","role":"assistant"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\n',
        b'data: {"choices":[{"delta":{"content":"There"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":" are"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":" "},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":"5"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":","},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":"2"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":"8"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":"0"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":" feet"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":" in"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":" a"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":" mile"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":"."},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":" This"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\n',
        b'data: {"choices":[{"delta":{"content":" is"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":" a"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":" standard"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":" measurement"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":" used"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":" in"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":" the"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":" United"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":" States"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":" and"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":" a"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":" few"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":" other"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":" countries"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":"."},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":" If"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":" you"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":" need"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":" help"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.',
        b'chunk"}\n\ndata: {"choices":[{"delta":{"content":" conver"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":"ting"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":" other"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":" units"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":" of"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":" measurement"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":","},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":" feel"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":" free"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":" to"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":" ask"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\n',
        b'data: {"choices":[{"delta":{"content":"!"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":""},"finish_reason":"stop","index":0,"logprobs":null}],"created":1739300519,"id":"f9a9e06e5c844339aee30ecb9f61ca8b","model":"mistral-large","object":"chat.completion.chunk","usage":{"completion_tokens":45,"prompt_tokens":19,"total_tokens":64}}\n\ndata: [DONE]\n\n',
    ]
    EXPECTED_STREAMING_RESPONSE = "There are 5,280 feet in a mile. This is a standard measurement used in the United States and a few other countries. If you need help converting other units of measurement, feel free to ask!"

    # To test the case where a Chinese character (3 bytes in UTF8 encoding) is broken between two SSE "lines".
    # See GitHub issue https://github.com/Azure/azure-sdk-for-python/issues/39565
    # Recorded from real chat completions streaming response
    # - Using sample code `samples\sample_chat_completions_streaming.py`,
    # - With SSE logging turned on (_ENABLE_CLASS_LOGS = True`),
    # - With Mistral Large model, with user message "Translate 'the sky is blue' to Chinese. Don't add any extra text before or after the Chinese translation. Just give the translation.", with content safety turned on.
    # - The bytes below are from the log output of `[Original element]`.
    # This was the original response:
    # STREAMING_RESPONSE_BYTES_SPLIT_CHINISE_CHAR: List[bytes] = [
    #     b'data: {"choices":[{"delta":{"content":"","role":"assistant"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739388793,"id":"97f3900d75c94c028984e58bef2a2584","model":"mistral-large","object":"chat.completion.chunk"}\n\n',
    #     b'data: {"choices":[{"delta":{"content":"\xe5\xa4\xa9"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739388793,"id":"97f3900d75c94c028984e58bef2a2584","model":"mistral-large","object":"chat.completion.chunk"}\n\n',
    #     b'data: {"choices":[{"delta":{"content":"\xe7\xa9\xba"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739388793,"id":"97f3900d75c94c028984e58bef2a2584","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":"\xe6\x98\xaf"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739388793,"id":"97f3900d75c94c028984e58bef2a2584","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":"\xe8\x93\x9d"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739388793,"id":"97f3900d75c94c028984e58bef2a2584","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":"\xe8\x89\xb2"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739388793,"id":"97f3900d75c94c028984e58bef2a2584","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":"\xe7\x9a\x84"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739388793,"id":"97f3900d75c94c028984e58bef2a2584","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":""},"finish_reason":"stop","index":0,"logprobs":null}],"created":1739388793,"id":"97f3900d75c94c028984e58bef2a2584","model":"mistral-large","object":"chat.completion.chunk","usage":{"completion_tokens":7,"prompt_tokens":41,"total_tokens":48}}\n\ndata: [DONE]\n\n'
    # ]
    # Below is a manually modifed response of the above, after splitting the 2nd line into two lines, in the middle of the 3-byte Chinese charcater. This is an
    # This represents the case presented in the above GitHub issue:
    STREAMING_RESPONSE_BYTES_SPLIT_CHINISE_CHAR: List[bytes] = [
        b'data: {"choices":[{"delta":{"content":"","role":"assistant"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739388793,"id":"97f3900d75c94c028984e58bef2a2584","model":"mistral-large","object":"chat.completion.chunk"}\n\n',
        b'data: {"choices":[{"delta":{"content":"\xe5\xa4',
        b'\xa9"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739388793,"id":"97f3900d75c94c028984e58bef2a2584","model":"mistral-large","object":"chat.completion.chunk"}\n\n',
        b'data: {"choices":[{"delta":{"content":"\xe7\xa9\xba"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739388793,"id":"97f3900d75c94c028984e58bef2a2584","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":"\xe6\x98\xaf"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739388793,"id":"97f3900d75c94c028984e58bef2a2584","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":"\xe8\x93\x9d"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739388793,"id":"97f3900d75c94c028984e58bef2a2584","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":"\xe8\x89\xb2"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739388793,"id":"97f3900d75c94c028984e58bef2a2584","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":"\xe7\x9a\x84"},"finish_reason":null,"index":0,"logprobs":null}],"created":1739388793,"id":"97f3900d75c94c028984e58bef2a2584","model":"mistral-large","object":"chat.completion.chunk"}\n\ndata: {"choices":[{"delta":{"content":""},"finish_reason":"stop","index":0,"logprobs":null}],"created":1739388793,"id":"97f3900d75c94c028984e58bef2a2584","model":"mistral-large","object":"chat.completion.chunk","usage":{"completion_tokens":7,"prompt_tokens":41,"total_tokens":48}}\n\ndata: [DONE]\n\n',
    ]
    EXPECTED_STREAMING_RESPONSE_SPLIT_CHINESE_CHAR = "天空是蓝色的"  # "The sky is blue" in Chinese

    # Regression test for the implementation of StreamingChatCompletions class,
    # which does the SSE parsing for streaming response
    def test_streaming_response_parsing(self, **kwargs):

        http_response = HttpResponseForUnitTests(TestUnitTests.STREAMING_RESPONSE_BYTES)
        response = sdk.models.StreamingChatCompletions(response=http_response)

        actual_response: str = ""
        for update in response:
            print(update.choices[0].delta.content or "", end="", flush=True)
            actual_response += update.choices[0].delta.content or ""

        assert actual_response == TestUnitTests.EXPECTED_STREAMING_RESPONSE

    # Regression test for the implementation of AsyncStreamingChatCompletions class,
    # which does the async SSE parsing for streaming response
    async def test_streaming_response_parsing_async(self, **kwargs):

        async_http_response = AsyncHttpResponseForUnitTests(TestUnitTests.STREAMING_RESPONSE_BYTES)
        response = sdk.models.AsyncStreamingChatCompletions(response=async_http_response)

        actual_response: str = ""
        async for update in response:
            print(update.choices[0].delta.content or "", end="", flush=True)
            actual_response += update.choices[0].delta.content or ""

        assert actual_response == TestUnitTests.EXPECTED_STREAMING_RESPONSE

    # Regression test for the implementation of StreamingChatCompletions class,
    # which does the SSE parsing for streaming response, with input SSE "lines"
    # that have a Chinese character (3 bytes in UTF8 encoding) split between between two "lines".
    def test_streaming_response_parsing_split_chinese_char(self, **kwargs):

        http_response = HttpResponseForUnitTests(TestUnitTests.STREAMING_RESPONSE_BYTES_SPLIT_CHINISE_CHAR)
        response = sdk.models.StreamingChatCompletions(response=http_response)

        actual_response: str = ""
        for update in response:
            print(update.choices[0].delta.content or "", end="", flush=True)
            actual_response += update.choices[0].delta.content or ""

        assert actual_response == TestUnitTests.EXPECTED_STREAMING_RESPONSE_SPLIT_CHINESE_CHAR
