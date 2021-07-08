
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import re
from devtools_testutils import AzureTestCase
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
            response['body']['string'] = self._replace_keys(response['body']['string'])

        return response
    
    def _replace_keys(self, body):
        def _replace_recursively(dictionary):
            for key in dictionary:
                value = dictionary[key]
                if key in self._keys:
                    dictionary[key] = self._replacement
                elif isinstance(value, dict):
                    _replace_recursively(value)

        import json
        try:
            body = json.loads(body)
            _replace_recursively(body)

        except (KeyError, ValueError):
            return body

        return json.dumps(body)

class CommunicationTestCase(AzureTestCase):
    FILTER_HEADERS = ReplayableTest.FILTER_HEADERS + ['x-azure-ref', 'x-ms-content-sha256', 'location']

    def __init__(self, method_name, *args, **kwargs):
        super(CommunicationTestCase, self).__init__(method_name, *args, **kwargs)