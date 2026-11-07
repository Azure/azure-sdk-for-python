# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Rust-path copy of the sync AAD credential test that runs query_items.

Source: ``tests/test_aad.py::TestAAD``. Only ``test_aad_credentials`` calls
query_items, so only it is copied. Its steps and assertions are unchanged. Settings
come from ``config.settings`` and the client pins ``_backend="rust"``. Like the
original, it signs requests with a fake emulator credential (localhost audience), so
it keeps the original's emulator-only gate and is skipped against a live account.
"""
import base64
import json
import time
import unittest
from io import StringIO

import pytest
from azure.core.credentials import AccessToken

import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos import DatabaseProxy, ContainerProxy
from config.settings import TestSettings


def _remove_padding(encoded_string):
    while encoded_string.endswith("="):
        encoded_string = encoded_string[0:len(encoded_string) - 1]

    return encoded_string


def get_test_item(num):
    test_item = {
        'pk': 'pk',
        'id': 'Item_' + str(num),
        'test_object': True,
        'lastName': 'Smith'
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
        emulator_key = TestSettings.masterKey
        first = _remove_padding(str(base64.urlsafe_b64encode(aad_header_cosmos_emulator.encode("utf-8")), "utf-8"))
        str_io_obj = StringIO()
        json.dump(aad_claim_cosmos_emulator_format, str_io_obj)
        second = _remove_padding(
            str(base64.urlsafe_b64encode(str(str_io_obj.getvalue()).replace(" ", "").encode("utf-8")), "utf-8"))
        third = _remove_padding(str(base64.urlsafe_b64encode(emulator_key.encode("utf-8")), "utf-8"))
        return AccessToken(first + "." + second + "." + third, int(time.time() + 7200))


@pytest.mark.cosmosEmulator
class TestAAD(unittest.TestCase):
    client: cosmos_client.CosmosClient = None
    database: DatabaseProxy = None
    container: ContainerProxy = None
    configs = TestSettings
    host = configs.host
    masterKey = configs.masterKey
    # Emulator-only credential used by this class.
    credential = CosmosEmulatorCredential()
    _skip_on_non_emulator = pytest.mark.skipif(
        not configs.is_emulator,
        reason="environment-gap: emulator credential tests are emulator-specific (localhost audience), "
               "and the target account is not the emulator (original emulator-only gate from tests/test_aad.py)."
    )

    @classmethod
    def setUpClass(cls):
        cls.client = cosmos_client.CosmosClient(cls.host, cls.credential, _backend="rust")
        cls.database = cls.client.get_database_client(cls.configs.TEST_DATABASE_ID)
        cls.container = cls.database.get_container_client(cls.configs.TEST_SINGLE_PARTITION_CONTAINER_ID)

    @_skip_on_non_emulator
    def test_aad_credentials_rust(self):
        # Source: tests/test_aad.py::TestAAD.test_aad_credentials
        print("Container info: " + str(self.container.read()))
        self.container.create_item(get_test_item(0))
        print("Point read result: " + str(self.container.read_item(item='Item_0', partition_key='pk')))
        query_results = list(self.container.query_items(query='select * from c', partition_key='pk'))
        assert len(query_results) == 1
        print("Query result: " + str(query_results[0]))
        self.container.delete_item(item='Item_0', partition_key='pk')


if __name__ == "__main__":
    unittest.main()
