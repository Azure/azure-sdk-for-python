# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure_devtools.scenario_tests import RecordingProcessor
import re
class URIIdentityReplacer(RecordingProcessor):
    """Replace the identity in request uri"""
    def process_request(self, request):
        request.uri = re.sub('/identities/([^/?]+)', '/identities/sanitized', request.uri)
        return request

    def process_response(self, response):
        if 'url' in response:
            response['url'] = re.sub('/identities/([^/?]+)', '/identities/sanitized', response['url'])
        return response

class URIMsalUsernameReplacer(RecordingProcessor):
    """Replace the MSAL username in request uri"""
    def process_request(self, request):
        resource = (urlparse(request.uri).netloc).split('.')[0]
        request.uri = re.sub('common/userrealm/([^/.]+)', 'common/userrealm/sanitized@test', request.uri) 
        request.uri = re.sub(resource, 'sanitized', request.uri)
        return request
    
    def process_response(self, response):
        if 'url' in response:
            response['url'] = re.sub('common/userrealm/([^/.]+)', 'common/userrealm/sanitized@test', response['url'])
        return response