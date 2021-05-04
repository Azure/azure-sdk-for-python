
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import re
import os
from devtools_testutils import AzureTestCase
from azure_devtools.scenario_tests import RecordingProcessor, ReplayableTest
from azure_devtools.scenario_tests.utilities import is_text_payload
from azure.communication.phonenumbers._shared.utils import parse_connection_str

class ResponseReplacerProcessor(RecordingProcessor):
    def __init__(self, keys=None, replacement="sanitized"):
        self._keys = keys if keys else []
        self._replacement = replacement

    def process_response(self, response):
        import json
        try:
            body = json.loads(response['body']['string'])
            if 'phoneNumbers' in body:
                for item in body["phoneNumbers"]:
                    if isinstance(item, str):
                        body["phoneNumbers"] = [self._replacement]
                        break
                    if "phoneNumber" in item:
                        item['phoneNumber'] = self._replacement
                    if "id" in item:
                        item['id'] = self._replacement
            response['body']['string'] = json.dumps(body)
            response['url'] = self._replacement
            return response
        except (KeyError, ValueError, TypeError):
            return response

class BodyReplacerProcessor(RecordingProcessor):
    """Sanitize the sensitive info inside request or response bodies"""

    def __init__(self, keys=None, replacement="sanitized"):
        self._replacement = replacement
        self._keys = keys if keys else []

    def process_request(self, request):
        if is_text_payload(request) and request.body:
            request.body = self._replace_keys(request.body.decode()).encode()

        return request

    def process_response(self, response):
        if is_text_payload(response) and response['body']['string']:
            response['body']['string'] = self._replace_keys(response['body']['string'])

        return response

    def _replace_keys(self, body):
        import json
        try:
            body = json.loads(body)
            for key in self._keys:
                if key in body:
                    body[key] = self._replacement

        except (KeyError, ValueError):
            return body

        return json.dumps(body)

class CommunicationTestCase(AzureTestCase):
    FILTER_HEADERS = ReplayableTest.FILTER_HEADERS + ['x-azure-ref', 'x-ms-content-sha256', 'location']
    def __init__(self, method_name, *args, **kwargs):
        super(CommunicationTestCase, self).__init__(method_name, *args, **kwargs)

    def setUp(self):
        super(CommunicationTestCase, self).setUp()

        if self.is_playback():
            self.connection_str = "endpoint=https://sanitized.communication.azure.com/;accesskey=fake==="
        else:
            self.connection_str = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')
            endpoint, _ = parse_connection_str(self.connection_str)
            self._resource_name = endpoint.split(".")[0]
            self.scrubber.register_name_pair(self._resource_name, "sanitized")