# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import asyncio
import json
import time
from unittest.mock import Mock
import uuid

import pytest
import requests
from azure.identity import AuthenticationError, AsyncClientSecretCredential, AsyncTokenCredentialChain


@pytest.mark.asyncio
async def test_client_secret_credential_cache(monkeypatch):
    expired = "this token's expired"
    now = time.time()
    token_payload = {
        "access_token": expired,
        "expires_in": 0,
        "ext_expires_in": 0,
        "expires_on": now - 300,  # expired 5 minutes ago
        "not_before": now,
        "token_type": "Bearer",
        "resource": str(uuid.uuid1()),
    }

    # monkeypatch requests so we can test pipeline configuration
    mock_response = Mock(text=json.dumps(token_payload), headers={"content-type": "application/json"}, status_code=200)
    mock_send = Mock(return_value=mock_response)
    monkeypatch.setattr(requests.Session, "send", value=mock_send)

    credential = AsyncClientSecretCredential("client_id", "secret", tenant_id=str(uuid.uuid1()))
    scopes = ("https://foo.bar/.default", "https://bar.qux/.default")
    token = await credential.get_token(scopes)
    assert token == expired

    token = await credential.get_token(scopes)
    assert token == expired
    assert mock_send.call_count == 2


@pytest.mark.asyncio
async def test_credential_chain_error_message():
    async def raise_authn_error(message):
        raise AuthenticationError(message)

    first_error = "first_error"
    first_credential = Mock(spec=AsyncClientSecretCredential, get_token=lambda _: raise_authn_error(first_error))
    second_error = "second_error"
    second_credential = Mock(get_token=lambda _: raise_authn_error(second_error))

    with pytest.raises(AuthenticationError) as ex:
        await AsyncTokenCredentialChain([first_credential, second_credential]).get_token(("scope",))

    assert "AsyncClientSecretCredential" in ex.value.message
    assert first_error in ex.value.message
    assert second_error in ex.value.message


@pytest.mark.asyncio
async def test_chain_attempts_all_credentials():
    async def raise_authn_error(message="it didn't work"):
        raise AuthenticationError(message)

    expected_token = "expected_token"
    credentials = [
        Mock(get_token=Mock(wraps=raise_authn_error)),
        Mock(get_token=Mock(wraps=raise_authn_error)),
        Mock(get_token=asyncio.coroutine(lambda _: expected_token)),
    ]

    token = await AsyncTokenCredentialChain(credentials).get_token(("scope",))
    assert token is expected_token

    for credential in credentials[:-1]:
        assert credential.get_token.call_count == 1


@pytest.mark.asyncio
async def test_chain_returns_first_token():
    expected_token = Mock()
    first_credential = Mock(get_token=asyncio.coroutine(lambda _: expected_token))
    second_credential = Mock(get_token=Mock())

    aggregate = AsyncTokenCredentialChain([first_credential, second_credential])
    credential = await aggregate.get_token(("scope",))

    assert credential is expected_token
    assert second_credential.get_token.call_count == 0
