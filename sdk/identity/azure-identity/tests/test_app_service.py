# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

from azure.identity._credentials.app_service import AppServiceCredential
from azure.identity._constants import EnvironmentVariables
import pytest

from helpers import mock
from recorded_test_case import RecordedTestCase

PLAYBACK_URL = "https://msi-endpoint/token"


class RecordedTests(RecordedTestCase):
    def __init__(self, *args, **kwargs):
        super(RecordedTests, self).__init__(*args, **kwargs)

        if self.is_live:
            url = os.environ.get(EnvironmentVariables.MSI_ENDPOINT)
            if not (url and EnvironmentVariables.MSI_SECRET in os.environ):
                pytest.skip("Recording requires values for $MSI_ENDPOINT and $MSI_SECRET")
            else:
                self.scrubber.register_name_pair(url, PLAYBACK_URL)
            self.patch = mock.MagicMock()  # no need to patch anything when recording
        else:
            # in playback we need to set environment variables and clear any that would interfere
            # (MSI_SECRET ends up in a header; vcr.py doesn't match headers, so the value doesn't matter)
            env = {EnvironmentVariables.MSI_ENDPOINT: PLAYBACK_URL, EnvironmentVariables.MSI_SECRET: "redacted"}
            self.patch = mock.patch.dict(os.environ, env, clear=True)

    def test_system_assigned(self):
        with self.patch:
            credential = AppServiceCredential()
        token = credential.get_token(self.scope)
        assert token.token
        assert isinstance(token.expires_on, int)

    @pytest.mark.usefixtures("user_assigned_identity_client_id")
    def test_user_assigned(self):
        with self.patch:
            credential = AppServiceCredential(client_id=self.user_assigned_identity_client_id)
        token = credential.get_token(self.scope)
        assert token.token
        assert isinstance(token.expires_on, int)
