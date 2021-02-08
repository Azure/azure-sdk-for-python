# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.core.credentials import AccessToken, AzureKeyCredential

from azure.mixedreality.authentication._shared.aio.mixed_reality_token_credential import get_mixedreality_credential, MixedRealityTokenCredential
from azure.mixedreality.authentication._shared.aio.static_access_token_credential import StaticAccessTokenCredential
from azure.mixedreality.authentication._shared.aio.mixedreality_account_key_credential import MixedRealityAccountKeyCredential

class TestMixedRealityTokenCredential:
    def test_get_mixedreality_credential_static_credential(self):
        access_token = AccessToken("My access token", 0)
        credential = StaticAccessTokenCredential(access_token)

        actualCredential = get_mixedreality_credential(
            account_id="account_id",
            account_domain="account_domain",
            endpoint_url="http://my.endpoint.url",
            credential=credential)

        assert credential == actualCredential

    def test_get_mixedreality_credential_other_credential(self):
        keyCredential = AzureKeyCredential("my_account_key")
        credential = MixedRealityAccountKeyCredential("account_id", keyCredential)

        actualCredential = get_mixedreality_credential(
            account_id="account_id",
            account_domain="account_domain",
            endpoint_url="http://my.endpoint.url",
            credential=credential)

        assert credential != actualCredential
        assert isinstance(actualCredential, MixedRealityTokenCredential)
