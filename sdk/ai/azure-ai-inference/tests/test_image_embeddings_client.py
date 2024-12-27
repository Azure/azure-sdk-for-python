# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
import azure.ai.inference as sdk

from model_inference_test_base import (
    ModelClientTestBase,
    ServicePreparerImageEmbeddings,
)

from devtools_testutils import recorded_by_proxy
from azure.core.exceptions import ServiceRequestError
from azure.core.credentials import AzureKeyCredential


# The test class name needs to start with "Test" to get collected by pytest
class TestImageEmbeddingsClient(ModelClientTestBase):

    # **********************************************************************************
    #
    #         IMAGE EMBEDDINGS REGRESSION TESTS - NO SERVICE RESPONSE REQUIRED
    #
    # **********************************************************************************

    # Regression test. Send a request that includes all supported types of input objects. Make sure the resulting
    # JSON payload that goes up to the service (including headers) is the correct one after hand-inspection.
    def test_image_embeddings_request_payload(self, **kwargs):
        client = sdk.ImageEmbeddingsClient(
            endpoint="http://does.not.exist",
            credential=AzureKeyCredential("key-value"),
            headers={"some_header": "some_header_value"},
            user_agent="MyAppId",
        )
        image_embedding_input = ModelClientTestBase._get_image_embeddings_input()
        for _ in range(2):
            try:
                _ = client.embed(
                    input=[image_embedding_input],
                    dimensions=2048,
                    encoding_format=sdk.models.EmbeddingEncodingFormat.UBINARY,
                    input_type=sdk.models.EmbeddingInputType.QUERY,
                    model_extras={
                        "key1": 1,
                        "key2": True,
                        "key3": "Some value",
                        "key4": [1, 2, 3],
                        "key5": {"key6": 2, "key7": False, "key8": "Some other value", "key9": [4, 5, 6, 7]},
                    },
                    model="some-model-id",
                    raw_request_hook=self.request_callback,
                )
                assert False
            except ServiceRequestError as _:
                # The test should throw this exception!
                self._validate_image_embeddings_json_request_payload()
                continue

    # Regression test. Send a request that includes all supported types of input objects, with embedding settings
    # specified in the constructor. Make sure the resulting JSON payload that goes up to the service
    # is the correct one after hand-inspection.
    def test_image_embeddings_request_payload_with_defaults(self, **kwargs):
        client = sdk.ImageEmbeddingsClient(
            endpoint="http://does.not.exist",
            credential=AzureKeyCredential("key-value"),
            headers={"some_header": "some_header_value"},
            user_agent="MyAppId",
            dimensions=2048,
            encoding_format=sdk.models.EmbeddingEncodingFormat.UBINARY,
            input_type=sdk.models.EmbeddingInputType.QUERY,
            model_extras={
                "key1": 1,
                "key2": True,
                "key3": "Some value",
                "key4": [1, 2, 3],
                "key5": {"key6": 2, "key7": False, "key8": "Some other value", "key9": [4, 5, 6, 7]},
            },
            model="some-model-id",
        )
        image_embedding_input = ModelClientTestBase._get_image_embeddings_input()
        for _ in range(2):
            try:
                response = client.embed(input=[image_embedding_input], raw_request_hook=self.request_callback)
                assert False
            except ServiceRequestError as _:
                # The test should throw this exception!
                self._validate_image_embeddings_json_request_payload()
                continue

    # Regression test. Send a request that includes all supported types of input objects, with embeddings settings
    # specified in the constructor and all of them overwritten in the 'embed' call.
    # Make sure the resulting JSON payload that goes up to the service is the correct one after hand-inspection.
    def test_image_embeddings_request_payload_with_defaults_and_overrides(self, **kwargs):
        client = sdk.ImageEmbeddingsClient(
            endpoint="http://does.not.exist",
            credential=AzureKeyCredential("key-value"),
            headers={"some_header": "some_header_value"},
            user_agent="MyAppId",
            dimensions=1024,
            encoding_format=sdk.models.EmbeddingEncodingFormat.UINT8,
            input_type=sdk.models.EmbeddingInputType.DOCUMENT,
            model_extras={
                "hey1": 2,
                "key2": False,
                "key3": "Some other value",
                "key9": "Yet another value",
            },
            model="some-other-model-id",
        )
        image_embedding_input = ModelClientTestBase._get_image_embeddings_input()
        for _ in range(2):
            try:
                _ = client.embed(
                    input=[image_embedding_input],
                    dimensions=2048,
                    encoding_format=sdk.models.EmbeddingEncodingFormat.UBINARY,
                    input_type=sdk.models.EmbeddingInputType.QUERY,
                    model_extras={
                        "key1": 1,
                        "key2": True,
                        "key3": "Some value",
                        "key4": [1, 2, 3],
                        "key5": {"key6": 2, "key7": False, "key8": "Some other value", "key9": [4, 5, 6, 7]},
                    },
                    model="some-model-id",
                    raw_request_hook=self.request_callback,
                )
                assert False
            except ServiceRequestError as _:
                # The test should throw this exception!
                self._validate_image_embeddings_json_request_payload()
                continue

    # **********************************************************************************
    #
    #                      HAPPY PATH SERVICE TESTS - IMAGE EMBEDDINGS
    #
    # **********************************************************************************

    # TODO: At the moment the /info route shows  "model_type": "embedding", so load_client
    # will return an EmbeddingsClient instead of ImageEmbeddingsClient. How can we resolve this?
    # This Cohere model (cohere-embed-v2-english) supports both text embeddings and image embeddings.
    @ServicePreparerImageEmbeddings()
    @recorded_by_proxy
    def test_load_image_embeddings_client(self, **kwargs):

        client = self._load_image_embeddings_client(**kwargs)
        assert isinstance(client, sdk.EmbeddingsClient)
        assert client._model_info
        response1 = client.get_model_info()
        self._print_model_info_result(response1)
        self._validate_model_info_result(response1, "embedding")  # TODO: What should this be?
        client.close()

    # TODO: At the moment the /info route shows  "model_type": "embedding", so load_client
    # will return an EmbeddingsClient instead of ImageEmbeddingsClient. How can we resolve this?
    # This Cohere model (cohere-embed-v2-english) supports both text embeddings and image embeddings.
    @ServicePreparerImageEmbeddings()
    @recorded_by_proxy
    def test_get_model_info_on_image_embeddings_client(self, **kwargs):

        client = self._create_image_embeddings_client(**kwargs)
        assert not client._model_info  # pylint: disable=protected-access

        response1 = client.get_model_info()
        assert client._model_info  # pylint: disable=protected-access

        self._print_model_info_result(response1)
        self._validate_model_info_result(response1, "embedding")  # TODO: what should this be?

        # Get the model info again. No network calls should be made here,
        # as the response is cached in the client.
        response2 = client.get_model_info()
        self._print_model_info_result(response2)
        assert response1 == response2
        client.close()

    @ServicePreparerImageEmbeddings()
    @recorded_by_proxy
    def test_image_embeddings_with_entra_id_auth(self, **kwargs):
        with self._create_image_embeddings_client(key_auth=False, **kwargs) as client:
            image_embedding_input = ModelClientTestBase._get_image_embeddings_input(False)

            # Request image embeddings with default service format (list of floats)
            response1 = client.embed(input=[image_embedding_input])
            self._print_embeddings_result(response1)
            self._validate_image_embeddings_result(response1)
            assert json.dumps(response1.as_dict(), indent=2) == response1.__str__()

    @ServicePreparerImageEmbeddings()
    @recorded_by_proxy
    def test_image_embeddings(self, **kwargs):
        client = self._create_image_embeddings_client(**kwargs)
        image_embedding_input = ModelClientTestBase._get_image_embeddings_input(False)

        # Request image embeddings with default service format (list of floats)
        response1 = client.embed(input=[image_embedding_input])
        self._print_embeddings_result(response1)
        self._validate_image_embeddings_result(response1)
        assert json.dumps(response1.as_dict(), indent=2) == response1.__str__()

        # Request embeddings as base64 encoded strings
        response2 = client.embed(
            input=[image_embedding_input], encoding_format=sdk.models.EmbeddingEncodingFormat.BASE64
        )
        self._print_embeddings_result(response2, sdk.models.EmbeddingEncodingFormat.BASE64)
        self._validate_image_embeddings_result(response2, sdk.models.EmbeddingEncodingFormat.BASE64)

        client.close()
