# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
import msal
from azure.core.exceptions import ClientAuthenticationError
from azure.identity._credentials.azure_arc import AzureArcCredential

from helpers import GET_TOKEN_METHODS


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_msal_managed_identity_error(get_token_method):
    scopes = ["scope1"]

    def mock_request_token(*args, **kwargs):
        raise msal.ManagedIdentityError()

    cred = AzureArcCredential()
    cred._msal_client.acquire_token_for_client = mock_request_token

    with pytest.raises(ClientAuthenticationError):
        getattr(cred, get_token_method)(*scopes)
