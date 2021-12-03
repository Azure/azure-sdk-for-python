# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from unittest import TestCase
try:
    from unittest.mock import MagicMock, patch
except ImportError:  # python < 3.3
    from mock import MagicMock, patch  # type: ignore
import azure.communication.chat._shared.user_credential as user_credential
from azure.communication.chat._shared.user_credential import CommunicationTokenCredential
from azure.communication.chat._shared.utils import create_access_token
from azure.communication.chat._shared.utils import get_current_utc_as_int
from datetime import timedelta
from _shared.helper import generate_token_with_custom_expiry_epoch, generate_token_with_custom_expiry


class TestCommunicationTokenCredential(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.sample_token = generate_token_with_custom_expiry_epoch(
            32503680000)  # 1/1/2030
        cls.expired_token = generate_token_with_custom_expiry_epoch(
            100)  # 1/1/1970

    def test_communicationtokencredential_decodes_token(self):
        credential = CommunicationTokenCredential(self.sample_token)
        access_token = credential.get_token()
        self.assertEqual(access_token.token, self.sample_token)

    def test_communicationtokencredential_throws_if_invalid_token(self):
        self.assertRaises(
            ValueError, lambda: CommunicationTokenCredential("foo.bar.tar"))

    def test_communicationtokencredential_throws_if_nonstring_token(self):
        self.assertRaises(TypeError, lambda: CommunicationTokenCredential(454))

    def test_communicationtokencredential_static_token_returns_expired_token(self):
        credential = CommunicationTokenCredential(self.expired_token)
        self.assertEqual(credential.get_token().token, self.expired_token)

    def test_communicationtokencredential_token_expired_refresh_called(self):
        refresher = MagicMock(return_value=self.sample_token)
        access_token = CommunicationTokenCredential(
            self.expired_token,
            token_refresher=refresher).get_token()
        refresher.assert_called_once()
        self.assertEqual(access_token, self.sample_token)

    def test_communicationtokencredential_token_expired_refresh_called_as_necessary(self):
        refresher = MagicMock(
            return_value=create_access_token(self.expired_token))
        credential = CommunicationTokenCredential(
            self.expired_token, token_refresher=refresher)

        credential.get_token()
        access_token = credential.get_token()

        self.assertEqual(refresher.call_count, 2)
        self.assertEqual(access_token.token, self.expired_token)

    # @patch_threading_timer(user_credential.__name__+'.Timer')
    def test_uses_initial_token_as_expected(self):  # , timer_mock):
        refresher = MagicMock(
            return_value=self.expired_token)
        credential = CommunicationTokenCredential(
            self.sample_token, token_refresher=refresher, refresh_proactively=True)
        with credential:
            access_token = credential.get_token()

        self.assertEqual(refresher.call_count, 0)
        self.assertEqual(access_token.token, self.sample_token)

    def test_proactive_refresher_should_not_be_called_before_specified_time(self):
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

        with patch(user_credential.__name__+'.'+get_current_utc_as_int.__name__, return_value=skip_to_timestamp):
            credential = CommunicationTokenCredential(
                initial_token,
                token_refresher=refresher,
                refresh_proactively=True,
                refresh_time_before_expiry=timedelta(minutes=refresh_minutes))
            with credential:
                access_token = credential.get_token()

        assert refresher.call_count == 0
        assert access_token.token == initial_token
        # check that next refresh is always scheduled
        assert credential._timer is not None

    def test_proactive_refresher_should_be_called_after_specified_time(self):
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

        with patch(user_credential.__name__+'.'+get_current_utc_as_int.__name__, return_value=skip_to_timestamp):
            credential = CommunicationTokenCredential(
                initial_token,
                token_refresher=refresher,
                refresh_proactively=True,
                refresh_time_before_expiry=timedelta(minutes=refresh_minutes))
            with credential:
                access_token = credential.get_token()

        assert refresher.call_count == 1
        assert access_token.token == refreshed_token
        # check that next refresh is always scheduled
        assert credential._timer is not None

    def test_proactive_refresher_keeps_scheduling_again(self):
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
        with credential:
            access_token = credential.get_token()
            with patch(user_credential.__name__+'.'+get_current_utc_as_int.__name__, return_value=skip_to_timestamp):
                access_token = credential.get_token()

        assert refresher.call_count == 2
        assert access_token.token == last_refreshed_token.token
        # check that next refresh is always scheduled
        assert credential._timer is not None

    def test_exit_cancels_timer(self):
        refreshed_token = create_access_token(
            generate_token_with_custom_expiry(30 * 60))
        refresher = MagicMock(return_value=refreshed_token)
        expired_token = generate_token_with_custom_expiry(-10 * 60)

        with CommunicationTokenCredential(
                expired_token,
                token_refresher=refresher,
                refresh_proactively=True) as credential:
            assert credential._timer is not None
        assert credential._timer.finished.is_set() == True

    def test_refresher_should_not_be_called_when_token_still_valid(self):
        generated_token = generate_token_with_custom_expiry(15 * 60)
        new_token = generate_token_with_custom_expiry(10 * 60)
        refresher = MagicMock(return_value=create_access_token(new_token))

        credential = CommunicationTokenCredential(
            generated_token, token_refresher=refresher, refresh_proactively=False)
        with credential:
            for _ in range(10):
                access_token = credential.get_token()

        refresher.assert_not_called()
        assert generated_token == access_token.token
