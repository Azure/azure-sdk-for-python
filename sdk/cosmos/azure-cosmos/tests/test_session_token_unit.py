# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest

import pytest

from azure.cosmos._vector_session_token import VectorSessionToken
from azure.cosmos.exceptions import CosmosHttpResponseError


@pytest.mark.cosmosEmulator
class TestSessionTokenUnitTest(unittest.TestCase):
    """Test to ensure escaping of non-ascii characters from partition key"""

    def test_validate_successful_session_token_parsing(self):
        # valid session token
        session_token = "1#100#1=20#2=5#3=30"
        self.assertEqual(VectorSessionToken.create(session_token).convert_to_string(), "1#100#1=20#2=5#3=30")

    def test_validate_session_token_parsing_with_invalid_version(self):
        session_token = "foo#100#1=20#2=5#3=30"
        self.assertIsNone(VectorSessionToken.create(session_token))

    def test_validate_session_token_parsing_with_invalid_global_lsn(self):
        session_token = "1#foo#1=20#2=5#3=30"
        self.assertIsNone(VectorSessionToken.create(session_token))

    def test_validate_session_token_parsing_with_invalid_region_progress(self):
        session_token = "1#100#1=20#2=x#3=30"
        self.assertIsNone(VectorSessionToken.create(session_token))

    def test_validate_session_token_parsing_with_invalid_format(self):
        session_token = "1;100#1=20#2=40"
        self.assertIsNone(VectorSessionToken.create(session_token))

    def test_validate_session_token_parsing_from_empty_string(self):
        session_token = ""
        self.assertIsNone(VectorSessionToken.create(session_token))

    def test_validate_session_token_comparison(self):
        # valid session token
        session_token1 = VectorSessionToken.create("1#100#1=20#2=5#3=30")
        session_token2 = VectorSessionToken.create("2#105#4=10#2=5#3=30")
        self.assertIsNotNone(session_token1)
        self.assertIsNotNone(session_token2)
        self.assertFalse(session_token1.equals(session_token2))
        self.assertFalse(session_token2.equals(session_token1))

        session_token_merged = VectorSessionToken.create("2#105#2=5#3=30#4=10")
        self.assertIsNotNone(session_token_merged)
        self.assertTrue(session_token1.merge(session_token2).equals(session_token_merged))

        session_token1 = VectorSessionToken.create("1#100#1=20#2=5#3=30")
        session_token2 = VectorSessionToken.create("1#100#1=10#2=8#3=30")
        self.assertIsNotNone(session_token1)
        self.assertIsNotNone(session_token2)
        self.assertFalse(session_token1.equals(session_token2))
        self.assertFalse(session_token2.equals(session_token1))

        session_token_merged = VectorSessionToken.create("1#100#1=20#2=8#3=30")
        self.assertIsNotNone(session_token_merged)
        self.assertTrue(session_token_merged.equals(session_token1.merge(session_token2)))

        session_token1 = VectorSessionToken.create("1#100#1=20#2=5#3=30")
        session_token2 = VectorSessionToken.create("1#102#1=100#2=8#3=30")
        self.assertIsNotNone(session_token1)
        self.assertIsNotNone(session_token1)
        self.assertFalse(session_token1.equals(session_token2))
        self.assertFalse(session_token2.equals(session_token1))

        session_token_merged = VectorSessionToken.create("1#102#2=8#3=30#1=100")
        self.assertIsNotNone(session_token_merged)
        self.assertTrue(session_token_merged.equals(session_token1.merge(session_token2)))

        session_token1 = VectorSessionToken.create("1#101#1=20#2=5#3=30")
        session_token2 = VectorSessionToken.create("1#100#1=20#2=5#3=30#4=40")
        self.assertIsNotNone(session_token1)
        self.assertIsNotNone(session_token2)

        try:
            session_token1.merge(session_token2)
            self.fail("Region progress can not be different when version is same")
        except CosmosHttpResponseError as e:
            self.assertEqual(str(e),
                             "Status code: 500\nCompared session tokens '1#101#1=20#2=5#3=30' "
                             "and '1#100#1=20#2=5#3=30#4=40' have unexpected regions.")


if __name__ == '__main__':
    unittest.main()
