# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import jwt
import time
import asyncio
from azure.communication.phonenumbers._shared.user_credential_async import CommunicationTokenCredential
from azure.communication.phonenumbers._shared.utils import create_access_token


async def generate_test_token(expiry_time_seconds=1000):
    payload = {
        "sub": "1234567890",
        "name": "John Doe",
        "iat": 1516239022,
        "exp": time.time() + expiry_time_seconds,  # Expiration time
    }
    return jwt.encode(payload, "secret", algorithm="HS256")


async def token_refresher(expiry_time_seconds=1000):
    new_token = await generate_test_token(expiry_time_seconds)
    return create_access_token(new_token)


@pytest.mark.asyncio
async def test_communication_token_credential_initialization():
    test_token = await generate_test_token()
    CommunicationTokenCredential(token=test_token)


@pytest.mark.asyncio
async def test_communication_token_credential_with_token_refresher():
    test_token = await generate_test_token()
    CommunicationTokenCredential(token=test_token, token_refresher=token_refresher)


@pytest.mark.asyncio
async def test_communication_token_credential_with_proactive_refresh():
    test_token = await generate_test_token()
    CommunicationTokenCredential(token=test_token, token_refresher=token_refresher, proactive_refresh=True)


@pytest.mark.asyncio
async def test_communication_token_credential_get_token():
    test_token = await generate_test_token()
    token_credential = CommunicationTokenCredential(token=test_token)
    result = await token_credential.get_token()
    assert result.token == test_token


@pytest.mark.asyncio
async def test_communication_token_credential_get_token_with_refresh():
    test_token = await generate_test_token()
    token_credential = CommunicationTokenCredential(token=test_token, token_refresher=token_refresher)
    result = await token_credential.get_token()
    assert result.token == test_token


@pytest.mark.asyncio
async def test_communication_token_credential_get_token_with_proactive_refresh():
    test_token = await generate_test_token()
    token_credential = CommunicationTokenCredential(
        token=test_token, token_refresher=token_refresher, proactive_refresh=True
    )
    result = await token_credential.get_token()
    assert result.token == test_token


@pytest.mark.asyncio
async def test_communication_token_credential_with_non_string_token():
    with pytest.raises(TypeError):
        CommunicationTokenCredential(token=12345)


@pytest.mark.asyncio
async def test_communication_token_credential_with_proactive_refresh_but_no_token_refresher():
    test_token = await generate_test_token()
    with pytest.raises(ValueError):
        CommunicationTokenCredential(token=test_token, proactive_refresh=True)


@pytest.mark.asyncio
async def test_communication_token_credential_get_token_no_refresh():
    test_token = await generate_test_token()
    token_credential = CommunicationTokenCredential(token=test_token)
    assert (await token_credential.get_token()).token == test_token


@pytest.mark.asyncio
async def test_communication_token_credential_context_manager():
    test_token = await generate_test_token()
    async with CommunicationTokenCredential(
        token=test_token, token_refresher=token_refresher, proactive_refresh=True
    ) as token_credential:
        assert (await token_credential.get_token()).token == test_token


@pytest.mark.asyncio
async def test_communication_token_credential_close():
    test_token = await generate_test_token()
    token_credential = CommunicationTokenCredential(
        token=test_token, token_refresher=token_refresher, proactive_refresh=True
    )
    await token_credential.close()
    assert token_credential._is_closed.is_set()
    assert token_credential._timer is None


@pytest.mark.asyncio
async def test_communication_token_credential_get_token_with_refresh_and_expiring_soon():
    test_token = await generate_test_token(3)
    token_credential = CommunicationTokenCredential(token=test_token, token_refresher=lambda: token_refresher())
    await asyncio.sleep(4)
    new_token = await token_credential.get_token()
    decoded_test_token = jwt.decode(test_token, "secret", options={"verify_exp": False}, algorithms=["HS256"])
    decoded_new_token = jwt.decode(new_token.token, "secret", options={"verify_exp": False}, algorithms=["HS256"])
    assert decoded_new_token["exp"] > decoded_test_token["exp"]
