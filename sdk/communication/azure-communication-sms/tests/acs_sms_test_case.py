# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
from enum import auto, Enum
from devtools_testutils import AzureRecordedTestCase, is_live
from azure.communication.sms._shared.utils import parse_connection_str
from msal import PublicClientApplication

class CommunicationTestResourceType(Enum):
    """Type of ACS resource used for livetests."""
    UNSPECIFIED = auto()
    DYNAMIC = auto()
    STATIC = auto()

class ACSSMTestCase(AzureRecordedTestCase):
    def setUp(self, resource_type=CommunicationTestResourceType.UNSPECIFIED):
        self.connection_str = self._get_connection_str(resource_type)
        if is_live():
            self.phone_number = os.getenv("AZURE_PHONE_NUMBER")
            self.endpoint, _ = parse_connection_str(self.connection_str)
        else:
            self.endpoint, _ = parse_connection_str(self.connection_str)
            self.phone_number = "+14255550123"
        self._resource_name = self.endpoint.split(".")[0]

    # sms
    def _get_connection_str(self, resource_type):
        if self.is_playback():
            return "endpoint=https://sanitized.communication.azure.com/;accesskey=fake==="
        if resource_type == CommunicationTestResourceType.UNSPECIFIED:
            return os.getenv('COMMUNICATION_LIVETEST_DYNAMIC_CONNECTION_STRING') or \
                os.getenv('COMMUNICATION_LIVETEST_STATIC_CONNECTION_STRING')
        if resource_type == CommunicationTestResourceType.DYNAMIC:
            return os.getenv('COMMUNICATION_LIVETEST_DYNAMIC_CONNECTION_STRING')
        if resource_type == CommunicationTestResourceType.STATIC:
            return os.getenv('COMMUNICATION_LIVETEST_STATIC_CONNECTION_STRING')

    def verify_successful_sms_response(self, sms_response):
        if self.is_live:
            assert sms_response.to == self.phone_number
        assert sms_response.message_id is not None
        assert sms_response.http_status_code == 202
        assert sms_response.error_message is None
        assert sms_response.successful
