# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from unittest import TestCase
from unittest.mock import MagicMock
from .user_credential import CommunicationUserCredential
from .utils import create_access_token


class TestCommunicationUserCredential(TestCase):
    sample_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."+\
        "eyJleHAiOjMyNTAzNjgwMDAwfQ.9i7FNNHHJT8cOzo-yrAUJyBSfJ-tPPk2emcHavOEpWc"
    sample_token_expiry = 32503680000
    expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."+\
        "eyJleHAiOjEwMH0.1h_scYkNp-G98-O4cW6KvfJZwiz54uJMyeDACE4nypg"


    def test_communicationusercredential_decodes_token(self):
        credential = CommunicationUserCredential(self.sample_token)
        access_token = credential.get_token()

        self.assertEqual(access_token.token, self.sample_token)

    def test_communicationusercredential_throws_if_invalid_token(self):
        self.assertRaises(ValueError, lambda: CommunicationUserCredential("foo.bar.tar"))

    def test_communicationusercredential_throws_if_nonstring_token(self):
        self.assertRaises(TypeError, lambda: CommunicationUserCredential(454))

    def test_communicationusercredential_static_token_returns_expired_token(self):
        credential = CommunicationUserCredential(self.expired_token)

        self.assertEqual(credential.get_token().token, self.expired_token)

    def test_communicationusercredential_token_expired_refresh_called(self):
        refresher = MagicMock(return_value=self.sample_token)
        access_token = CommunicationUserCredential(
            self.expired_token,
            token_refresher=refresher).get_token()
        refresher.assert_called_once()
        self.assertEqual(access_token, self.sample_token)


    def test_communicationusercredential_token_expired_refresh_called_asnecessary(self):
        refresher = MagicMock(return_value=create_access_token(self.expired_token))
        credential = CommunicationUserCredential(
            self.expired_token,
            token_refresher=refresher)

        credential.get_token()
        access_token = credential.get_token()

        self.assertEqual(refresher.call_count, 2)
        self.assertEqual(access_token.token, self.expired_token)
