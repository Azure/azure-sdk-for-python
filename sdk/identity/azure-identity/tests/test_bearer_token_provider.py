# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.core.credentials import AccessToken
from azure.identity import get_bearer_token_provider


class MockCredential:
    def get_token(self, *scopes, **kwargs):
        assert len(scopes) == 1
        assert scopes[0] == "scope"
        return AccessToken("mock_token", 42)


def test_get_bearer_token_provider():

    func = get_bearer_token_provider(MockCredential(), "scope")
    assert func() == "mock_token"
