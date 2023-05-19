# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
from devtools_testutils import AzureRecordedTestCase, is_live
from azure.communication.rooms._shared.utils import parse_connection_str

class ACSRoomsTestCase(AzureRecordedTestCase):
    def setUp(self):
        if is_live():
            self.connection_str = os.getenv('COMMUNICATION_CONNECTION_STRING_ROOMS')
            self.endpoint, _ = parse_connection_str(self.connection_str)
            self._resource_name = self.endpoint.split(".")[0]
        else:
            self.connection_str = "endpoint=https://sanitized.communication.azure.com/;accesskey=fake==="
            self.endpoint, _ = parse_connection_str(self.connection_str)
            self._resource_name = self.endpoint.split(".")[0]

