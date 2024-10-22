# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.core.credentials import AccessToken, AccessTokenInfo
from azure.identity import get_bearer_token_provider


class MockCredential:
    def get_token(self, *scopes, **kwargs):
        assert len(scopes) == 1
        assert scopes[0] == "scope"
        return AccessToken("mock_token", 42)


class MockCredentialTokenInfo:
    def get_token_info(self, *scopes, **kwargs):
        assert len(scopes) == 1
        assert scopes[0] == "scope"
        return AccessTokenInfo("mock_token_2", 42)


def test_get_bearer_token_provider():

    func = get_bearer_token_provider(MockCredential(), "scope")
    assert func() == "mock_token"

    func = get_bearer_token_provider(MockCredentialTokenInfo(), "scope")  # type: ignore
    assert func() == "mock_token_2"
