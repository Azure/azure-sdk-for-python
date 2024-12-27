# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import json
import azure.ai.inference as sdk

from model_inference_test_base import ModelClientTestBase


# The test class name needs to start with "Test" to get collected by pytest
class TestUnitTests(ModelClientTestBase):

    # **********************************************************************************
    #
    #                               UNIT TESTS
    #
    # **********************************************************************************

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
