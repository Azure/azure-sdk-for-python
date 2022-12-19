# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure_devtools.scenario_tests import RecordingProcessor
from azure_devtools.scenario_tests.utilities import is_text_payload

class URIIdentityReplacer(RecordingProcessor):
    """Replace the identity in request uri"""
    def process_request(self, request):
        import re
        request.uri = re.sub('/identities/[A-Za-z0-9-_%]+', '/identities/sanitized', request.uri)
        return request

    def process_response(self, response):
        import re
        if 'url' in response:
            response['url'] = re.sub('/identities/[A-Za-z0-9-_%]+', '/identities/sanitized', response['url'])
        return response

class RequestBodyIdentityReplacer(RecordingProcessor):
    """Replace the identity in request uri"""
    def process_request(self, request):
        import re
        if is_text_payload(request) and request.body:
            request.body = re.sub('8:acs:[A-Za-z0-9-_]+', 'sanitized', request.body.decode()).encode()
        return request

    def process_response(self, response):
        return response
