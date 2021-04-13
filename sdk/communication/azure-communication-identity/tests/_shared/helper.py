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
        from urllib.parse import urlparse
        resource_group = (urlparse(request.uri).netloc).split('.')[0]
        request.uri = re.sub('/identities/([^/?]+)', '/identities/sanitized', request.uri) 
        request.uri = re.sub(resource_group, 'sanitized', request.uri)
        return request
    
    def process_response(self, response):
        import re
        if 'url' in response:
            response['url'] = re.sub('/identities/([^/?]+)', '/identities/sanitized', response['url'])
        return response