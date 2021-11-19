# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from unittest import TestCase
from unittest.mock import MagicMock
from azure.communication.identity._shared.user_credential import CommunicationTokenCredential
from azure.communication.identity._shared.utils import create_access_token


class TestCommunicationTokenCredential(TestCase):
    sample_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9." +\
        "eyJleHAiOjMyNTAzNjgwMDAwfQ.9i7FNNHHJT8cOzo-yrAUJyBSfJ-tPPk2emcHavOEpWc"
    sample_token_expiry = 32503680000
    expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9." +\
        "eyJleHAiOjEwMH0.1h_scYkNp-G98-O4cW6KvfJZwiz54uJMyeDACE4nypg"

    def test_communicationtokencredential_decodes_token(self):
        credential = CommunicationTokenCredential(self.sample_token)
        access_token = credential.get_token()
        self.assertEqual(access_token.token, self.sample_token)

    def test_communicationtokencredential_throws_if_invalid_token(self):
        self.assertRaises(
            ValueError, lambda: CommunicationTokenCredential("foo.bar.tar"))

    def test_communicationtokencredential_throws_if_nonstring_token(self):
        self.assertRaises(TypeError, lambda: CommunicationTokenCredential(454))

    def test_communicationtokencredential_static_token_returns_expired_token(self):
        credential = CommunicationTokenCredential(self.expired_token)
        self.assertEqual(credential.get_token().token, self.expired_token)

    def test_communicationtokencredential_token_expired_refresh_called(self):
        refresher = MagicMock(return_value=self.sample_token)
        access_token = CommunicationTokenCredential(
            self.expired_token,
            token_refresher=refresher).get_token()
        refresher.assert_called_once()
        self.assertEqual(access_token, self.sample_token)

    def test_communicationtokencredential_token_expired_refresh_called_as_necessary(self):
        refresher = MagicMock(
            return_value=create_access_token(self.expired_token))
        credential = CommunicationTokenCredential(
            self.expired_token, token_refresher=refresher)

        credential.get_token()
        access_token = credential.get_token()

        self.assertEqual(refresher.call_count, 2)
        self.assertEqual(access_token.token, self.expired_token)
