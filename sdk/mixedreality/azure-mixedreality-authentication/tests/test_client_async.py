# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

from devtools_testutils import AzureRecordedTestCase

from azure.mixedreality.authentication.aio import MixedRealityStsClient
from azure.mixedreality.authentication._shared.aio.mixedreality_account_key_credential import MixedRealityAccountKeyCredential


class TestAsyncClient(AzureRecordedTestCase):

    def test_create_client(self, account_info):
        client = MixedRealityStsClient(
            account_id=account_info["account_id"],
            account_domain=account_info["account_domain"],
            credential=account_info["key_credential"])

        assert client is not None

    def test_create_client_custom_with_endpoint(self, account_info):
        custom_endpoint_url = "https://my.custom.endpoint"
        client = MixedRealityStsClient(
            account_id=account_info["account_id"],
            account_domain=account_info["account_domain"],
            credential=account_info["key_credential"],
            custom_endpoint_url=custom_endpoint_url)

        assert client._endpoint_url == custom_endpoint_url

    def test_create_client_with_credential(self, account_info):
        token_credential = MixedRealityAccountKeyCredential(
            account_info["account_id"], account_info["key_credential"])
        client = MixedRealityStsClient(
            account_id=account_info["account_id"],
            account_domain=account_info["account_domain"],
            credential=token_credential)

        assert client._credential == token_credential

    def test_create_client_with_invalid_arguments(self, account_info):
        with pytest.raises(ValueError):
            MixedRealityStsClient(
                account_id=None,
                account_domain=account_info["account_domain"],
                credential=account_info["key_credential"])

        with pytest.raises(ValueError):
            MixedRealityStsClient(
                account_id=account_info["account_id"],
                account_domain=None,
                credential=account_info["key_credential"])

        with pytest.raises(ValueError):
            MixedRealityStsClient(
                account_id=account_info["account_id"],
                account_domain=account_info["account_domain"],
                credential=None)

        with pytest.raises(ValueError):
            MixedRealityStsClient(
                account_id=account_info["account_id"],
                account_domain=account_info["account_domain"],
                credential=account_info["key_credential"],
                custom_endpoint_url="#")

    @pytest.mark.asyncio
    async def test_get_token(self, recorded_test, account_info):
        client = MixedRealityStsClient(
            account_id=account_info["account_id"],
            account_domain=account_info["account_domain"],
            credential=account_info["key_credential"])

        token = await client.get_token()

        assert token is not None
        assert token.token is not None
        assert token.expires_on is not None
