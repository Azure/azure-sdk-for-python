
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

class IdentityReplacer(RecordingProcessor):
    """Replace the identity id in a request/response body."""

    def __init__(self, replacement='sanitized'):
        self._replacement = replacement

    def process_request(self, request):
        if is_text_payload(request) and request.body:
            request.body = self._replace_ids(request.body.decode()).encode()
        return request

    def process_response(self, response):
        if is_text_payload(response) and response['body']['string']:
            response['body']['string'] = self._replace_ids(response['body']['string'])
            return response
    
    def _replace_ids(self, body):
        import json
        try:
            body = json.loads(body)
            if 'identity' in body:
                body['identity']['id'] = self._replacement
            elif 'id' in body:
                body['id'] = self._replacement
        except (KeyError, ValueError):
            return body

        return json.dumps(body)

class AccessTokenReplacer(RecordingProcessor):
    """Replace the access token in a request/response body."""

    def __init__(self, replacement='sanitized'):
        self._replacement = replacement

    def process_request(self, request):
        import re
        if is_text_payload(request) and request.body:
            body = str(request.body.decode())
            body = re.sub(r'"token": "([0-9a-f-]{36})"', r'"token": 00000000-0000-0000-0000-000000000000', body)
            request.body = body.encode()
        return request

    def process_response(self, response):
        import json
        try:
            body = json.loads(response['body']['string'])
            if 'accessToken' in body:
                body['accessToken']['token'] = self._replacement
            elif 'token' in body:
                body['token'] = self._replacement

            response['body']['string'] = json.dumps(body)
            return response
        except (KeyError, ValueError):
            return response

class CommunicationTestCase(AzureTestCase):
    FILTER_HEADERS = ReplayableTest.FILTER_HEADERS + ['x-azure-ref', 'x-ms-content-sha256', 'location']

    def __init__(self, method_name, *args, **kwargs):
        super(CommunicationTestCase, self).__init__(method_name, *args, **kwargs)