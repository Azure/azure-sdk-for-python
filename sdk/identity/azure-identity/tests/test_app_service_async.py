# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from unittest import mock

from azure.identity.aio._credentials.app_service import AppServiceCredential
from azure.identity._constants import EnvironmentVariables
import pytest

from helpers_async import await_test
from recorded_test_case import RecordedTestCase
from test_app_service import PLAYBACK_URL


class RecordedTests(RecordedTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

    @await_test
    async def test_system_assigned(self):
        with self.patch:
            credential = AppServiceCredential()
        token = await credential.get_token(self.scope)
        assert token.token
        assert isinstance(token.expires_on, int)

    @pytest.mark.usefixtures("user_assigned_identity_client_id")
    @await_test
    async def test_user_assigned(self):
        with self.patch:
            credential = AppServiceCredential(client_id=self.user_assigned_identity_client_id)
        token = await credential.get_token(self.scope)
        assert token.token
        assert isinstance(token.expires_on, int)
