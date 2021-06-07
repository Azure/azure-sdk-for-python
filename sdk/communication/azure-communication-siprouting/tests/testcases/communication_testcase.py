# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
from devtools_testutils import AzureTestCase
from azure_devtools.scenario_tests import ReplayableTest
from azure.core.pipeline.policies import HttpLoggingPolicy


class CommunicationTestCase(AzureTestCase):
    FILTER_HEADERS = ReplayableTest.FILTER_HEADERS + [
        "x-azure-ref",
        "x-ms-content-sha256",
        "location",
    ]

    def __init__(self, method_name, *args, **kwargs):
        super(CommunicationTestCase, self).__init__(method_name, *args, **kwargs)

    def setUp(self):
        super(CommunicationTestCase, self).setUp()

        if self.is_playback():
            self.connection_str = (
                "endpoint=https://sanitized.communication.azure.net/;accesskey=fake==="
            )
        else:
            self.connection_str = os.getenv(
                "COMMUNICATION_LIVETEST_STATIC_CONNECTION_STRING"
            )
            idx_left = self.connection_str.find("//")
            idx_right = self.connection_str.find(".communication")
            self._resource_name = self.connection_str[idx_left + 2 : idx_right]

            self.scrubber.register_name_pair(self._resource_name, "sanitized")

    def _get_http_logging_policy(self, **kwargs):
        http_logging_policy = HttpLoggingPolicy(**kwargs)
        http_logging_policy.allowed_header_names.update({"MS-CV"})
        return http_logging_policy
