# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

# cspell:ignore reranker
"""Regression test for lazy initialization of _InferenceService with AAD credentials.

Verifies that constructing a CosmosClient with AAD credentials does not crash
when AZURE_COSMOS_SEMANTIC_RERANKER_INFERENCE_ENDPOINT is not set.
"""
import base64
import json
import os
import time
import unittest
from io import StringIO

import pytest
from azure.core.credentials import AccessToken

import azure.cosmos.cosmos_client as cosmos_client
import test_config
from azure.cosmos import DatabaseProxy, ContainerProxy


def _remove_padding(encoded_string):
    while encoded_string.endswith("="):
        encoded_string = encoded_string[0:len(encoded_string) - 1]
    return encoded_string


def get_test_item(num):
    test_item = {
        'pk': 'pk',
        'id': 'LazyInit_' + str(num),
        'test_object': True,
    }
    return test_item


class CosmosEmulatorCredential(object):
    """Fake AAD credential for the Cosmos emulator."""
    def get_token(self, *scopes, **kwargs):
        aad_header_cosmos_emulator = "{\"typ\":\"JWT\",\"alg\":\"RS256\",\"x5t\":\"" \
                                     "CosmosEmulatorPrimaryMaster\",\"kid\":\"CosmosEmulatorPrimaryMaster\"}"
        aad_claim_cosmos_emulator_format = {
            "aud": "https://localhost.localhost",
            "iss": "https://sts.fake-issuer.net/7b1999a1-dfd7-440e-8204-00170979b984",
            "iat": int(time.time()), "nbf": int(time.time()),
            "exp": int(time.time() + 7200), "aio": "", "appid": "localhost",
            "appidacr": "1", "idp": "https://localhost:8081/",
            "oid": "96313034-4739-43cb-93cd-74193adbe5b6", "rh": "", "sub": "localhost",
            "tid": "EmulatorFederation", "uti": "", "ver": "1.0",
            "scp": "user_impersonation",
            "groups": ["7ce1d003-4cb3-4879-b7c5-74062a35c66e",
                       "e99ff30c-c229-4c67-ab29-30a6aebc3e58",
                       "5549bb62-c77b-4305-bda9-9ec66b85d9e4",
                       "c44fd685-5c58-452c-aaf7-13ce75184f65",
                       "be895215-eab5-43b7-9536-9ef8fe130330"]}
        emulator_key = test_config.TestConfig.masterKey
        first = _remove_padding(str(base64.urlsafe_b64encode(aad_header_cosmos_emulator.encode("utf-8")), "utf-8"))
        str_io_obj = StringIO()
        json.dump(aad_claim_cosmos_emulator_format, str_io_obj)
        second = _remove_padding(
            str(base64.urlsafe_b64encode(str(str_io_obj.getvalue()).replace(" ", "").encode("utf-8")), "utf-8"))
        third = _remove_padding(str(base64.urlsafe_b64encode(emulator_key.encode("utf-8")), "utf-8"))
        return AccessToken(first + "." + second + "." + third, int(time.time() + 7200))


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosLong
class TestAADInferenceServiceLazyInit(unittest.TestCase):
    """Verify AAD client construction succeeds without the semantic reranker env var.

    Before the fix, _InferenceService was eagerly initialized during CosmosClient
    construction whenever AAD credentials were used, causing a ValueError if
    AZURE_COSMOS_SEMANTIC_RERANKER_INFERENCE_ENDPOINT was missing.
    """

    client: cosmos_client.CosmosClient = None
    database: DatabaseProxy = None
    container: ContainerProxy = None
    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    credential = CosmosEmulatorCredential() if configs.is_emulator else configs.credential

    def setUp(self):
        """Save the env var state before each test."""
        self._saved_endpoint = os.environ.get("AZURE_COSMOS_SEMANTIC_RERANKER_INFERENCE_ENDPOINT")

    def tearDown(self):
        """Ensure the env var is always unset after each test to prevent leakage."""
        os.environ.pop("AZURE_COSMOS_SEMANTIC_RERANKER_INFERENCE_ENDPOINT", None)

    def test_aad_client_construction_without_inference_endpoint(self):
        """Constructing a CosmosClient with AAD creds must not raise when
        AZURE_COSMOS_SEMANTIC_RERANKER_INFERENCE_ENDPOINT is unset."""
        os.environ.pop("AZURE_COSMOS_SEMANTIC_RERANKER_INFERENCE_ENDPOINT", None)

        client = cosmos_client.CosmosClient(self.host, self.credential)
        db = client.get_database_client(self.configs.TEST_DATABASE_ID)
        container = db.get_container_client(self.configs.TEST_SINGLE_PARTITION_CONTAINER_ID)

        item = get_test_item(0)
        container.create_item(item)
        read_result = container.read_item(item=item['id'], partition_key='pk')
        assert read_result['id'] == item['id']

        query_results = list(container.query_items(
            query='SELECT * FROM c WHERE c.id=@id',
            parameters=[{"name": "@id", "value": item['id']}],
            partition_key='pk'
        ))
        assert len(query_results) == 1

        container.delete_item(item=item['id'], partition_key='pk')

    def test_aad_client_construction_with_inference_endpoint(self):
        """Constructing a CosmosClient with AAD creds must also work when
        AZURE_COSMOS_SEMANTIC_RERANKER_INFERENCE_ENDPOINT IS set."""
        os.environ["AZURE_COSMOS_SEMANTIC_RERANKER_INFERENCE_ENDPOINT"] = "https://example.com"

        client = cosmos_client.CosmosClient(self.host, self.credential)
        db = client.get_database_client(self.configs.TEST_DATABASE_ID)
        container = db.get_container_client(self.configs.TEST_SINGLE_PARTITION_CONTAINER_ID)

        item = get_test_item(1)
        container.create_item(item)
        read_result = container.read_item(item=item['id'], partition_key='pk')
        assert read_result['id'] == item['id']
        container.delete_item(item=item['id'], partition_key='pk')


if __name__ == "__main__":
    unittest.main()
