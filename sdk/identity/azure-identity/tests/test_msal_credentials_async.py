# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from unittest.mock import Mock

from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.identity._internal import ConfidentialClientCredential
import pytest


@pytest.mark.asyncio
async def test_confidential_client_credential_exceptions():
    expected_message = "expectations met"
    expected_exception = HttpResponseError(expected_message)
    raises = Mock(side_effect=expected_exception)

    # credential should raise a ClientAuthenticationError from any exception raised by MSAL
    credential = ConfidentialClientCredential("client_id", "https://spam.eggs/spam")
    credential._msal_app = Mock(acquire_token_silent=lambda _, **__: None, acquire_token_for_client=raises)
    with pytest.raises(ClientAuthenticationError) as ex:
        await credential.get_token("scope")
    assert expected_message in ex.value.message
    assert expected_exception is ex.value.__context__

    # credential should raise a ClientAuthenticationError from any exception raised by the transport adapter
    adapter = Mock(get=raises)
    credential = ConfidentialClientCredential("client_id", "https://spam.eggs/spam", msal_adapter=adapter)

    with pytest.raises(ClientAuthenticationError) as ex:
        await credential.get_token("scope")
    assert expected_message in ex.value.message
    assert expected_exception is ex.value.__context__

    # for AAD errors, credential should raise a ClientAuthenticationError with MSAL's error_description
    adapter = Mock(get=raises)
    credential = ConfidentialClientCredential("client_id", "https://spam.eggs/spam", msal_adapter=adapter)
    credential._msal_app = Mock(
        acquire_token_silent=lambda _, **__: None,
        acquire_token_for_client=lambda _, **__: {"error_description": expected_message},
    )

    with pytest.raises(ClientAuthenticationError) as ex:
        await credential.get_token("scope")
    assert expected_message in ex.value.message
