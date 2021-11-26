# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from unittest import TestCase
try:
    from unittest.mock import MagicMock, Mock, patch
except ImportError:  # python < 3.3
    from mock import MagicMock, Mock, patch  # type: ignore
import azure.communication.identity._shared.user_credential as user_credential
from azure.communication.identity._shared.user_credential import CommunicationTokenCredential
from azure.communication.identity._shared.utils import create_access_token
from azure.communication.identity._shared.utils import get_current_utc_as_int
#from unittest.mock import patch
from datetime import timedelta
from functools import wraps
import base64


def patch_threading_timer(target_timer):
    """patch_threading_timer acts similarly to unittest.mock.patch as a
    function decorator, but specifically for threading.Timer. The function
    passed to threading.Timer is called right away with all given arguments.

    :arg str target_timer: the target Timer (threading.Timer) to be patched
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            def side_effect(interval, function, args=None, kwargs=None):
                args = args if args is not None else []
                kwargs = kwargs if kwargs is not None else {}
                # Call the original function
                if(interval <= 0):
                    function(*args, **kwargs)
                # Return a mock object to allow function calls on the returned value
                return Mock()

            with patch(target_timer, side_effect=side_effect) as timer_mock:
                # Pass the mock object to the decorated function for further assertions
                return f(*(args[0], timer_mock), **kwargs)

        return wrapper

    return decorator


class TestCommunicationTokenCredential(TestCase):

    @staticmethod
    def get_token_with_custom_expiry(expires_on):
        expiry_json = '{"exp": ' + str(expires_on) + '}'
        base64expiry = base64.b64encode(
            expiry_json.encode('utf-8')).decode('utf-8').rstrip("=")
        token_template = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9." +\
            base64expiry + ".adM-ddBZZlQ1WlN3pdPBOF5G4Wh9iZpxNP_fSvpF4cWs"
        return token_template

    @classmethod
    def setUpClass(cls):
        cls.sample_token = cls.get_token_with_custom_expiry(
            32503680000)  # 1/1/2030
        cls.expired_token = cls.get_token_with_custom_expiry(100)  # 1/1/1970

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

    def test_uses_initial_token_as_expected(self):
        refresher = MagicMock(
            return_value=self.expired_token)
        credential = CommunicationTokenCredential(
            self.sample_token, token_refresher=refresher, refresh_proactively=True)

        access_token = credential.get_token()

        self.assertEqual(refresher.call_count, 0)
        self.assertEqual(access_token.token, self.sample_token)

    @patch_threading_timer(user_credential.__name__+'.Timer')
    def test_communicationtokencredential_does_not_proactively_refresh_before_specified_time(self, timer_mock):
        refresh_minutes = 30
        token_validity_minutes = 60
        start_timestamp = get_current_utc_as_int()
        skip_to_timestamp = start_timestamp + (refresh_minutes - 5) * 60

        initial_token = create_access_token(
            self.get_token_with_custom_expiry(start_timestamp + token_validity_minutes * 60))

        refresher = MagicMock(return_value=create_access_token(self.get_token_with_custom_expiry(
            skip_to_timestamp + token_validity_minutes * 60)))

        # travel in time to the point where the token should still not be refreshed
        with patch(user_credential.__name__+'.get_current_utc_as_int', return_value=skip_to_timestamp):
            credential = CommunicationTokenCredential(
                initial_token.token,
                token_refresher=refresher,
                refresh_proactively=True,
                refresh_time_before_expiry=timedelta(minutes=refresh_minutes))

        access_token = credential.get_token()

        self.assertEqual(refresher.call_count, 0)
        self.assertEqual(access_token.token, initial_token.token)
        # check that next refresh is always scheduled
        self.assertTrue(credential._timer is not None)

    @patch_threading_timer(user_credential.__name__+'.Timer')
    def test_communicationtokencredential_proactively_refreshes_after_specified_time(self, timer_mock):
        refresh_minutes = 30
        token_validity_minutes = 60
        start_timestamp = get_current_utc_as_int()
        skip_to_timestamp = start_timestamp + (refresh_minutes + 5) * 60

        initial_token = create_access_token(
            self.get_token_with_custom_expiry(start_timestamp + token_validity_minutes * 60))

        refresher = MagicMock(return_value=create_access_token(self.get_token_with_custom_expiry(
            skip_to_timestamp + token_validity_minutes * 60)))

        # travel in time to the point where the token should be refreshed
        with patch(user_credential.__name__+'.get_current_utc_as_int', return_value=skip_to_timestamp):
            credential = CommunicationTokenCredential(
                initial_token.token,
                token_refresher=refresher,
                refresh_proactively=True,
                refresh_time_before_expiry=timedelta(minutes=refresh_minutes))

        access_token = credential.get_token()

        self.assertEqual(refresher.call_count, 1)
        self.assertNotEqual(access_token.token, initial_token.token)
        # check that next refresh is always scheduled
        self.assertTrue(credential._timer is not None)

    def test_communicationtokencredential_repeats_scheduling(self):
        refresh_seconds = 1
        token_validity_minutes = 60
        start_timestamp = get_current_utc_as_int()
        skip_to_timestamp = start_timestamp + refresh_seconds

        refresher = MagicMock(return_value=create_access_token(self.get_token_with_custom_expiry(
            skip_to_timestamp + token_validity_minutes * 60)))

        # travel in time to the point where the token should be refreshed
        with patch(user_credential.__name__+'.get_current_utc_as_int', return_value=skip_to_timestamp):
            credential = CommunicationTokenCredential(
                self.expired_token,
                token_refresher=refresher,
                refresh_proactively=True,
                refresh_time_before_expiry=timedelta(seconds=refresh_seconds))

        access_token = credential.get_token()

        self.assertEqual(refresher.call_count, 1)
        self.assertNotEqual(access_token.token, self.expired_token)
        # check that next refresh is always scheduled
        self.assertTrue(credential._timer is not None)
        credential._timer.cancel()

    @patch_threading_timer(user_credential.__name__+'.Timer')
    def test_exit_cancels_timer(self, timer_mock):
        refresher = MagicMock(return_value=self.sample_token)

        with CommunicationTokenCredential(
                self.sample_token,
                token_refresher=refresher,
                refresh_proactively=True) as credential:
            self.assertTrue(credential._timer.is_alive())

        self.assertEqual(credential._timer.is_alive.call_count, 1)
        self.assertEqual(credential._timer.cancel.call_count, 1)
        self.assertEqual(refresher.call_count, 0)

    @patch_threading_timer(user_credential.__name__+'.Timer')
    def test_refresher_called_only_once(self, timer_mock):
        refresher = MagicMock(
            return_value=create_access_token(self.sample_token))

        credential = CommunicationTokenCredential(
            self.expired_token,
            token_refresher=refresher,
            refresh_proactively=True)

        for _ in range(10):
            credential.get_token()

        self.assertEqual(refresher.call_count, 1)
