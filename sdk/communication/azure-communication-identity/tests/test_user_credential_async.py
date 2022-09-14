
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from unittest import TestCase
import pytest
from asyncio import Future
try:
    from unittest.mock import MagicMock, patch
except ImportError:  # python < 3.3
    from mock import MagicMock, patch
from azure.communication.identity._shared.user_credential_async import CommunicationTokenCredential
import azure.communication.identity._shared.user_credential_async as user_credential_async
from azure.communication.identity._shared.utils import create_access_token
from azure.communication.identity._shared.utils import get_current_utc_as_int
from _shared.helper import generate_token_with_custom_expiry


class TestCommunicationTokenCredential(TestCase):

    def get_completed_future(self, result=None):
        future = Future()
        future.set_result(result)
        return future
    
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
    async def test_communicationtokencredential_throws_if_proactive_refresh_enabled_without_token_refresher(self):
        with pytest.raises(ValueError) as err:
            CommunicationTokenCredential(self.sample_token, proactive_refresh=True)
        assert str(err.value) == "When 'proactive_refresh' is True, 'token_refresher' must not be None."
        with pytest.raises(ValueError) as err:
            CommunicationTokenCredential(
                self.sample_token, 
                proactive_refresh=True,
                token_refresher=None)
        assert str(err.value) == "When 'proactive_refresh' is True, 'token_refresher' must not be None."

    @pytest.mark.asyncio
    async def test_refresher_should_be_called_immediately_with_expired_token(self):
        refreshed_token = generate_token_with_custom_expiry(10 * 60)
        refresher = MagicMock(
            return_value=self.get_completed_future(create_access_token(refreshed_token)))
        expired_token = generate_token_with_custom_expiry(-(5 * 60))

        credential = CommunicationTokenCredential(
            expired_token, token_refresher=refresher)
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
            initial_token, token_refresher=refresher, proactive_refresh=True)
        access_token = await credential.get_token()

        refresher.assert_not_called()
        assert initial_token == access_token.token

    @pytest.mark.asyncio
    async def test_refresher_should_not_be_called_when_token_still_valid(self):
        generated_token = generate_token_with_custom_expiry(15 * 60)
        new_token = generate_token_with_custom_expiry(10 * 60)
        refresher = MagicMock(return_value=create_access_token(new_token))

        credential = CommunicationTokenCredential(
            generated_token, token_refresher=refresher, proactive_refresh=False)
        for _ in range(10):
            access_token = await credential.get_token()

        refresher.assert_not_called()
        assert generated_token == access_token.token

    @pytest.mark.asyncio
    async def test_raises_if_refresher_returns_expired_token(self):
        expired_token = generate_token_with_custom_expiry(-(10 * 60))
        refresher = MagicMock(return_value=self.get_completed_future(
            create_access_token(expired_token)))

        credential = CommunicationTokenCredential(
            expired_token, token_refresher=refresher)
        with self.assertRaises(ValueError):
            await credential.get_token()

        assert refresher.call_count == 1

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
                proactive_refresh=True)
            access_token = await credential.get_token()

        assert refresher.call_count == 0
        assert access_token.token == initial_token
        # check that next refresh is always scheduled
        assert credential._timer is not None

    @pytest.mark.asyncio
    async def test_proactive_refresher_should_be_called_after_specified_time(self):
        refresh_minutes = 10
        token_validity_minutes = 60
        start_timestamp = get_current_utc_as_int()
        skip_to_timestamp = start_timestamp + \
            (token_validity_minutes - refresh_minutes + 5) * 60

        initial_token = generate_token_with_custom_expiry(
            token_validity_minutes * 60)
        refreshed_token = generate_token_with_custom_expiry(
            2 * token_validity_minutes * 60)
        refresher = MagicMock(
            return_value=self.get_completed_future(create_access_token(refreshed_token)))

        with patch(user_credential_async.__name__+'.'+get_current_utc_as_int.__name__, return_value=skip_to_timestamp):
            credential = CommunicationTokenCredential(
                initial_token,
                token_refresher=refresher,
                proactive_refresh=True)
            access_token = await credential.get_token()

        assert refresher.call_count == 1
        assert access_token.token == refreshed_token
        # check that next refresh is always scheduled
        assert credential._timer is not None

    @pytest.mark.asyncio
    async def test_proactive_refresher_keeps_scheduling_again(self):
        refresh_minutes = 10
        token_validity_minutes = 60
        expired_token = generate_token_with_custom_expiry(-5 * 60)
        skip_to_timestamp = get_current_utc_as_int() + (token_validity_minutes -
                                                        refresh_minutes) * 60 + 1
        first_refreshed_token = create_access_token(
            generate_token_with_custom_expiry(token_validity_minutes * 60))
        last_refreshed_token = create_access_token(
            generate_token_with_custom_expiry(2 * token_validity_minutes * 60))
        refresher = MagicMock(
            side_effect=[self.get_completed_future(first_refreshed_token), self.get_completed_future(last_refreshed_token)])

        credential = CommunicationTokenCredential(
            expired_token,
            token_refresher=refresher,
            proactive_refresh=True)
        access_token = await credential.get_token()
        with patch(user_credential_async.__name__+'.'+get_current_utc_as_int.__name__, return_value=skip_to_timestamp):
            access_token = await credential.get_token()

        assert refresher.call_count == 2
        assert access_token.token == last_refreshed_token.token
        # check that next refresh is always scheduled
        assert credential._timer is not None

    @pytest.mark.asyncio
    async def test_fractional_backoff_applied_when_token_expiring(self):
        token_validity_seconds = 5 * 60
        expiring_token = generate_token_with_custom_expiry(
            token_validity_seconds)

        refresher = MagicMock(
            side_effect=[create_access_token(expiring_token), create_access_token(expiring_token)])

        credential = CommunicationTokenCredential(
            expiring_token,
            token_refresher=refresher,
            proactive_refresh=True)

        next_milestone = token_validity_seconds / 2
        assert credential._timer.interval == next_milestone

        with patch(user_credential_async.__name__+'.'+get_current_utc_as_int.__name__, return_value=(get_current_utc_as_int() + next_milestone)):
            await credential.get_token()

        assert refresher.call_count == 1
        next_milestone = next_milestone / 2
        assert credential._timer.interval == next_milestone

    @pytest.mark.asyncio
    async def test_exit_cancels_timer(self):
        refreshed_token = create_access_token(
            generate_token_with_custom_expiry(30 * 60))
        refresher = MagicMock(return_value=refreshed_token)
        expired_token = generate_token_with_custom_expiry(-10 * 60)
        credential = CommunicationTokenCredential(
                expired_token,
                token_refresher=refresher,
                proactive_refresh=True)
        credential.get_token()
        credential.close()
        assert credential._timer is not None
        assert refresher.call_count == 0
        assert credential._timer is not None
        
    @pytest.mark.asyncio
    async def test_exit_enter_scenario_throws_exception(self):
        refreshed_token = create_access_token(
            generate_token_with_custom_expiry(30 * 60))
        refresher = MagicMock(return_value=refreshed_token)
        expired_token = generate_token_with_custom_expiry(-10 * 60)
        credential = CommunicationTokenCredential(
                expired_token,
                token_refresher=refresher,
                proactive_refresh=True)
        credential.get_token()
        credential.close()
        assert credential._timer is not None
        
        with pytest.raises(RuntimeError) as err:
            credential.get_token()
        assert str(err.value) == "An instance of CommunicationTokenCredential cannot be reused once it has been closed."
