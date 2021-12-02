
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from datetime import timedelta
import pytest
try:
    from unittest.mock import MagicMock, patch
except ImportError:  # python < 3.3
    from mock import MagicMock, patch
from azure.communication.sms._shared.user_credential_async import CommunicationTokenCredential
import azure.communication.sms._shared.user_credential_async as user_credential_async
from azure.communication.sms._shared.utils import create_access_token
from azure.communication.sms._shared.utils import get_current_utc_as_int
from _shared.helper import generate_token_with_custom_expiry


class TestCommunicationTokenCredential:

    @pytest.mark.asyncio
    async def test_raises_error_for_init_with_nonstring_token(self):
        with pytest.raises(TypeError) as err:
            CommunicationTokenCredential(1234)
        assert str(err.value) == "Token must be a string."

    @pytest.mark.asyncio
    async def test_raises_error_for_init_with_invalid_token(self):
        with pytest.raises(ValueError) as err:
            CommunicationTokenCredential("not a token")
        assert str(err.value) == "Token is not formatted correctly"

    @pytest.mark.asyncio
    async def test_init_with_valid_token(self):
        initial_token = generate_token_with_custom_expiry(5 * 60)
        credential = CommunicationTokenCredential(initial_token)
        access_token = await credential.get_token()
        assert initial_token == access_token.token

    @pytest.mark.asyncio
    async def test_refresher_should_be_called_immediately_with_expired_token(self):
        refreshed_token = generate_token_with_custom_expiry(10 * 60)
        refresher = MagicMock(
            return_value=create_access_token(refreshed_token))
        expired_token = generate_token_with_custom_expiry(-(5 * 60))

        credential = CommunicationTokenCredential(
            expired_token, token_refresher=refresher)
        async with credential:
            access_token = await credential.get_token()

        refresher.assert_called_once()
        assert refreshed_token == access_token.token

    @pytest.mark.asyncio
    async def test_refresher_should_not_be_called_before_expiring_time(self):
        initial_token = generate_token_with_custom_expiry(15 * 60)
        refreshed_token = generate_token_with_custom_expiry(10 * 60)
        refresher = MagicMock(
            return_value=create_access_token(refreshed_token))

        credential = CommunicationTokenCredential(
            initial_token, token_refresher=refresher, refresh_proactively=True)
        async with credential:
            access_token = await credential.get_token()

        refresher.assert_not_called()
        assert initial_token == access_token.token

    @pytest.mark.asyncio
    async def test_refresher_should_not_be_called_when_token_still_valid(self):
        generated_token = generate_token_with_custom_expiry(15 * 60)
        new_token = generate_token_with_custom_expiry(10 * 60)
        refresher = MagicMock(return_value=create_access_token(new_token))

        credential = CommunicationTokenCredential(
            generated_token, token_refresher=refresher, refresh_proactively=False)
        async with credential:
            for _ in range(10):
                access_token = await credential.get_token()

        refresher.assert_not_called()
        assert generated_token == access_token.token

    @pytest.mark.asyncio
    async def test_refresher_should_be_called_as_necessary(self):
        expired_token = generate_token_with_custom_expiry(-(10 * 60))
        refresher = MagicMock(return_value=create_access_token(expired_token))

        credential = CommunicationTokenCredential(
            expired_token, token_refresher=refresher)
        async with credential:
            await credential.get_token()
            access_token = await credential.get_token()

        assert refresher.call_count == 2
        assert expired_token == access_token.token

    @pytest.mark.asyncio
    async def test_proactive_refresher_should_not_be_called_before_specified_time(self):
        refresh_minutes = 30
        token_validity_minutes = 60
        start_timestamp = get_current_utc_as_int()
        skip_to_timestamp = start_timestamp + (refresh_minutes - 5) * 60

        initial_token = generate_token_with_custom_expiry(
            token_validity_minutes * 60)
        refreshed_token = generate_token_with_custom_expiry(
            2 * token_validity_minutes * 60)
        refresher = MagicMock(
            return_value=create_access_token(refreshed_token))

        with patch(user_credential_async.__name__+'.'+get_current_utc_as_int.__name__, return_value=skip_to_timestamp):
            credential = CommunicationTokenCredential(
                initial_token,
                token_refresher=refresher,
                refresh_proactively=True,
                refresh_time_before_expiry=timedelta(minutes=refresh_minutes))
            async with credential:
                access_token = await credential.get_token()

        assert refresher.call_count == 0
        assert access_token.token == initial_token
        # check that next refresh is always scheduled
        assert credential._timer is not None

    @pytest.mark.asyncio
    async def test_proactive_refresher_should_be_called_after_specified_time(self):
        refresh_minutes = 30
        token_validity_minutes = 60
        start_timestamp = get_current_utc_as_int()
        skip_to_timestamp = start_timestamp + (refresh_minutes + 5) * 60

        initial_token = generate_token_with_custom_expiry(
            token_validity_minutes * 60)
        refreshed_token = generate_token_with_custom_expiry(
            2 * token_validity_minutes * 60)
        refresher = MagicMock(
            return_value=create_access_token(refreshed_token))

        with patch(user_credential_async.__name__+'.'+get_current_utc_as_int.__name__, return_value=skip_to_timestamp):
            credential = CommunicationTokenCredential(
                initial_token,
                token_refresher=refresher,
                refresh_proactively=True,
                refresh_time_before_expiry=timedelta(minutes=refresh_minutes))
            async with credential:
                access_token = await credential.get_token()

        assert refresher.call_count == 1
        assert access_token.token == refreshed_token
        # check that next refresh is always scheduled
        assert credential._timer is not None

    @pytest.mark.asyncio
    async def test_proactive_refresher_keeps_scheduling_again(self):
        refresh_seconds = 2
        expired_token = generate_token_with_custom_expiry(-5 * 60)
        skip_to_timestamp = get_current_utc_as_int() + refresh_seconds + 4
        first_refreshed_token = create_access_token(
            generate_token_with_custom_expiry(4))
        last_refreshed_token = create_access_token(
            generate_token_with_custom_expiry(10 * 60))
        refresher = MagicMock(
            side_effect=[first_refreshed_token, last_refreshed_token])

        credential = CommunicationTokenCredential(
            expired_token,
            token_refresher=refresher,
            refresh_proactively=True,
            refresh_time_before_expiry=timedelta(seconds=refresh_seconds))
        async with credential:
            access_token = await credential.get_token()
            with patch(user_credential_async.__name__+'.'+get_current_utc_as_int.__name__, return_value=skip_to_timestamp):
                access_token = await credential.get_token()

        assert refresher.call_count == 2
        assert access_token.token == last_refreshed_token.token
        # check that next refresh is always scheduled
        assert credential._timer is not None

    @pytest.mark.asyncio
    async def test_exit_cancels_timer(self):
        refreshed_token = create_access_token(
            generate_token_with_custom_expiry(30 * 60))
        refresher = MagicMock(return_value=refreshed_token)
        expired_token = generate_token_with_custom_expiry(-10 * 60)

        async with CommunicationTokenCredential(
                expired_token,
                token_refresher=refresher,
                refresh_proactively=True) as credential:
            assert credential._timer is not None
        assert refresher.call_count == 0
