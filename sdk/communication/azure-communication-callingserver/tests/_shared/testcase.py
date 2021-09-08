# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import re
from devtools_testutils import AzureTestCase
from azure.communication.callingserver._shared.utils import parse_connection_str
from azure_devtools.scenario_tests import RecordingProcessor, ReplayableTest
from azure_devtools.scenario_tests.utilities import is_text_payload

class ResponseReplacerProcessor(RecordingProcessor):
    def __init__(self, keys=None, replacement="sanitized"):
        self._keys = keys if keys else []
        self._replacement = replacement

    def process_response(self, response):
        def sanitize_dict(dictionary):
            for key in dictionary:
                value = dictionary[key]
                if isinstance(value, str):
                    dictionary[key] = re.sub(
                        r"("+'|'.join(self._keys)+r")",
                        self._replacement,
                        dictionary[key])
                elif isinstance(value, dict):
                    sanitize_dict(value)

        sanitize_dict(response)

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
            response['body'] = self._replace_keys(response['body']['string'])

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
        self.variables_map = {
             "CONNECTION_STRING": os.getenv("COMMUNICATION_LIVETEST_STATIC_CONNECTION_STRING",
                 "endpoint=https://REDACTED.communication.azure.com/;accesskey=QWNjZXNzS2V5"),
             "AZURE_TENANT_ID": os.getenv("COMMUNICATION_LIVETEST_STATIC_RESOURCE_IDENTIFIER",
                 "016a7064-0581-40b9-be73-6dde64d69d72"),
             "FROM_PHONE_NUMBER": os.getenv("AZURE_PHONE_NUMBER", "+15551234567"),
             "TO_PHONE_NUMBER": os.getenv("AZURE_PHONE_NUMBER", "+15551234567"),
             "CALLBACK_URI": os.getenv("CALLBACK_URI", "https://host.app/api/callback/calling"),
             "AUDIO_FILE_URI": os.getenv("AUDIO_FILE_URI", "https://host.app/audio/bot-callcenter-intro.wav"),
             "METADATA_URL": os.getenv("METADATA_URL",
                 "https://storage.asm.skype.com/v1/objects/0-eus-d2-3cca2175891f21c6c9a5975a12c0141c/content/acsmetadata"),
             "VIDEO_URL": os.getenv("VIDEO_URL",
                 "https://storage.asm.skype.com/v1/objects/0-eus-d2-3cca2175891f21c6c9a5975a12c0141c/content/video"),
             "CONTENT_URL_404": os.getenv("CONTENT_URL_404", 
                 "https://storage.asm.skype.com/v1/objects/0-eus-d2-3cca2175891f21c6c9a5975a12c0141d/content/acsmetadata")
         }

    def setUp(self):
        super(CommunicationTestCase, self).setUp()
        if self.is_playback():
            self.connection_str = "endpoint=https://sanitized.communication.azure.com/;accesskey=fake==="
        else:
            #self.connection_str = os.getenv('COMMUNICATION_LIVETEST_DYNAMIC_CONNECTION_STRING')
            self.connection_str = "endpoint=https://acstestbot1.communication.azure.com/;accesskey=wuK/FrGFfWsRhQpBE6VtljXF1GsDaCr2H1ry4EEeQFmlrVDkaUGSLUiqkC8jq1fkqByGJxsvLAJq/9RAU/v7/w=="
            endpoint, _ = parse_connection_str(self.connection_str)
            self._resource_name = endpoint.split(".")[0]
            self.scrubber.register_name_pair(self._resource_name, "sanitized")
