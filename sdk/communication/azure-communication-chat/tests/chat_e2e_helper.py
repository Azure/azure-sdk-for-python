# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure_devtools.scenario_tests import RecordingProcessor


class ChatURIReplacer(RecordingProcessor):
    """Replace the identity in request uri"""
    def process_request(self, request):
        import re
        request.uri = re.sub('/chat/threads/([^/?]+)', '/chat/threads/sanitized', request.uri)
        request.uri = re.sub('/messages/([^/?]+)', '/messages/sanitized', request.uri)
        request.uri = re.sub(r'syncState=([\d\w]+)', 'syncState=sanitized', request.uri)
        return request

    def process_response(self, response):
        import re
        if 'url' in response:
            response['url'] = re.sub('/chat/threads/([^/?]+)', '/chat/threads/sanitized', response['url'])
            response['url'] = re.sub('/messages/([^/?]+)', '/messages/sanitized', response['url'])
            response['url'] = re.sub(r'syncState=([\d\w]+)', 'syncState=sanitized', response['url'])
        return response
