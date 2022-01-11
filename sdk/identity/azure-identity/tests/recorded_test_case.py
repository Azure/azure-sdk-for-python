# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

from azure_devtools.scenario_tests import GeneralNameReplacer, patch_time_sleep_api, RequestUrlNormalizer
from devtools_testutils.azure_testcase import AzureTestCase
import pytest

from recording_processors import IdTokenProcessor, RecordingRedactor

PLAYBACK_CLIENT_ID = "client-id"


class RecordedTestCase(AzureTestCase):
    def __init__(self, *args, **kwargs):
        scrubber = GeneralNameReplacer()
        super(RecordedTestCase, self).__init__(
            *args,
            recording_processors=[RecordingRedactor(), scrubber],
            replay_processors=[IdTokenProcessor(), RequestUrlNormalizer()],
            **kwargs
        )
        self.scrubber = scrubber
        self.replay_patches.append(patch_time_sleep_api)
        self.user_assigned_identity_client_id = os.environ.get("USER_ASSIGNED_IDENTITY_CLIENT_ID", PLAYBACK_CLIENT_ID)

    @pytest.fixture()
    def user_assigned_identity_client_id(self):
        if self.is_live:
            if self.user_assigned_identity_client_id == PLAYBACK_CLIENT_ID:
                pytest.skip("Set a value for $USER_ASSIGNED_IDENTITY_CLIENT_ID to record this test")
            else:
                self.scrubber.register_name_pair(self.user_assigned_identity_client_id, PLAYBACK_CLIENT_ID)

    @property
    def scope(self):
        return "https://management.azure.com/.default"
