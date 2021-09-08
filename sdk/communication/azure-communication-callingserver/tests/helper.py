# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure_devtools.scenario_tests import RecordingProcessor

class URIIdentityReplacer(RecordingProcessor):
    """Replace the identity in request uri"""
    def process_request(self, request):
        import re
        request.uri = re.sub('/identities/([^/?]+)', '/identities/sanitized', request.uri)
        return request

    def process_response(self, response):
        import re
        if 'url' in response:
            response['url'] = re.sub('/identities/([^/?]+)', '/identities/sanitized', response['url'])
        return response

class CallingServerURIReplacer(RecordingProcessor):
    """Replace the identity in request uri"""
    def process_request(self, request):
        import re
        request.uri = re.sub('/calling/serverCalls/([^/?]+)', '/calling/serverCalls/sanitized', request.uri)
        request.uri = re.sub('/calling/callConnections/([^/?]+)', '/calling/callConnections/sanitized', request.uri)
        request.uri = re.sub('recordings/([^/?]+)', 'recordings/sanitized', request.uri)
        return request

    def process_response(self, response):
        import re
        if 'url' in response:
            response['url'] = re.sub('/calling/serverCalls/([^/?]+)', '/calling/serverCalls/sanitized', response['url'])
            response['url'] = re.sub('/calling/callConnections/([^/?]+)', '/calling/callConnections/sanitized', response['url'])
            response['url'] = re.sub('recordings/([^/?]+)', 'recordings/sanitized', response['url'])
        return response