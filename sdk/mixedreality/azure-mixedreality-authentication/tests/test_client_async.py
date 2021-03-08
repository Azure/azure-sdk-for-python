# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import pytest

from devtools_testutils import AzureTestCase

from azure.core.credentials import AzureKeyCredential
from azure.mixedreality.authentication.aio import MixedRealityStsClient
from azure.mixedreality.authentication._shared.aio.mixedreality_account_key_credential import MixedRealityAccountKeyCredential

# Import fake account details matching recordings.
from _constants import (
    MIXEDREALITY_ACCOUNT_DOMAIN,
    MIXEDREALITY_ACCOUNT_ID,
    MIXEDREALITY_ACCOUNT_KEY
)


class ClientTests(AzureTestCase):
    def __init__(self, *args, **kwargs):
        super(ClientTests, self).__init__(*args, **kwargs)
        self.account_domain = self.get_var('MIXEDREALITY_ACCOUNT_DOMAIN', MIXEDREALITY_ACCOUNT_DOMAIN)
        self.account_id = self.get_var('MIXEDREALITY_ACCOUNT_ID', MIXEDREALITY_ACCOUNT_ID)
        self.account_key = self.get_var('MIXEDREALITY_ACCOUNT_KEY', MIXEDREALITY_ACCOUNT_KEY)
        self.key_credential = AzureKeyCredential(self.account_key)

    def setUp(self):
        super(ClientTests, self).setUp()

    def tearDown(self):
        super(ClientTests, self).tearDown()

    def get_var(self, variable_name, default_or_playback_value):
        # type: (str, str) -> str
        if self.is_live:
            return os.environ.get(variable_name, default_or_playback_value)

        return default_or_playback_value

    def test_create_client(self):
        client = MixedRealityStsClient(
            account_id=self.account_id,
            account_domain=self.account_domain,
            credential=self.key_credential)

        assert client is not None

    def test_create_client_custom_with_endpoint(self):
        custom_endpoint_url = "https://my.custom.endpoint"
        client = MixedRealityStsClient(
            account_id=self.account_id,
            account_domain=self.account_domain,
            credential=self.key_credential,
            custom_endpoint_url=custom_endpoint_url)

        assert client._endpoint_url == custom_endpoint_url

    def test_create_client_with_credential(self):
        token_credential = MixedRealityAccountKeyCredential(self.account_id, self.key_credential)
        client = MixedRealityStsClient(
            account_id=self.account_id,
            account_domain=self.account_domain,
            credential=token_credential)

        assert client._credential == token_credential

    def test_create_client_with_invalid_arguments(self):
        with pytest.raises(ValueError):
            MixedRealityStsClient(
                account_id=None,
                account_domain=self.account_domain,
                credential=self.key_credential)

        with pytest.raises(ValueError):
            MixedRealityStsClient(
                account_id=self.account_id,
                account_domain=None,
                credential=self.key_credential)

        with pytest.raises(ValueError):
            MixedRealityStsClient(
                account_id=self.account_id,
                account_domain=self.account_domain,
                credential=None)

        with pytest.raises(ValueError):
            MixedRealityStsClient(
                account_id=self.account_id,
                account_domain=self.account_domain,
                credential=self.key_credential,
                custom_endpoint_url="#")

    @AzureTestCase.await_prepared_test
    async def test_get_token(self):
        client = MixedRealityStsClient(
            account_id=self.account_id,
            account_domain=self.account_domain,
            credential=self.key_credential)

        token = await client.get_token()

        assert token is not None
        assert token.token is not None
        assert token.expires_on is not None
