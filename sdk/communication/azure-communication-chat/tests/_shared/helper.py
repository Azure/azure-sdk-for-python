# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import re
import base64
from azure_devtools.scenario_tests import RecordingProcessor
from datetime import datetime, timedelta
from functools import wraps
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
import sys

def generate_token_with_custom_expiry(valid_for_seconds):
    return generate_token_with_custom_expiry_epoch((datetime.now() + timedelta(seconds=valid_for_seconds)).timestamp())
 
def generate_token_with_custom_expiry_epoch(expires_on_epoch):
    expiry_json = f'{{"exp": {str(expires_on_epoch)} }}'
    base64expiry = base64.b64encode(
        expiry_json.encode('utf-8')).decode('utf-8').rstrip("=")
    token_template = (f'''eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
        {base64expiry}.adM-ddBZZlQ1WlN3pdPBOF5G4Wh9iZpxNP_fSvpF4cWs''')
    return token_template


class URIIdentityReplacer(RecordingProcessor):
    """Replace the identity in request uri"""
    def process_request(self, request):
        resource = (urlparse(request.uri).netloc).split('.')[0]
        request.uri = re.sub('/identities/([^/?]+)', '/identities/sanitized', request.uri) 
        request.uri = re.sub(resource, 'sanitized', request.uri)
        request.uri = re.sub('/identities/([^/?]+)', '/identities/sanitized', request.uri) 
        request.uri = re.sub(resource, 'sanitized', request.uri)
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