# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
from azure.communication.phonenumbers._shared.utils import parse_connection_str
from devtools_testutils import AzureRecordedTestCase


class PhoneNumbersTestCase(AzureRecordedTestCase):

    def setUp(self, use_dynamic_resource=False):
        if self.is_playback():
            self.connection_str = "endpoint=https://sanitized.communication.azure.com/;accesskey=fake==="
        else:
            if use_dynamic_resource:
                self.connection_str = os.environ["COMMUNICATION_LIVETEST_DYNAMIC_CONNECTION_STRING"]
            else:
                self.connection_str = os.environ["COMMUNICATION_LIVETEST_STATIC_CONNECTION_STRING"]
            endpoint, *_ = parse_connection_str(self.connection_str)
            self._resource_name = endpoint.split(".")[0]
