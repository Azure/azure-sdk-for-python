# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

from devtools_testutils import AzureRecordedTestCase, is_live
import pytest

PLAYBACK_CLIENT_ID = "client-id"


class RecordedTestCase(AzureRecordedTestCase):
    @pytest.fixture()
    def user_assigned_identity_client_id(self):
        self.user_assigned_identity_client_id = os.environ.get("USER_ASSIGNED_IDENTITY_CLIENT_ID", PLAYBACK_CLIENT_ID)
        if is_live():
            if self.user_assigned_identity_client_id == PLAYBACK_CLIENT_ID:
                pytest.skip("Set a value for $USER_ASSIGNED_IDENTITY_CLIENT_ID to record this test")

    @property
    def scope(self):
        return "https://management.azure.com/.default"
