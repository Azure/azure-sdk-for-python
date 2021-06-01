# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure_devtools.scenario_tests import RecordingProcessor

class PhoneNumberUriReplacer(RecordingProcessor):
    """Replace the identity in request uri"""

    def process_request(self, request):
        import re
        request.uri = re.sub('phoneNumbers/[%2B\d]+', 'phoneNumbers/sanitized', request.uri)
        return request

    def process_response(self, response):
        import re
        if 'url' in response:
            response['url'] = re.sub('capabilities/([^/?&]+)', 'capabilities/sanitized', response['url'])
            response['url'] = re.sub('releases/([^/?&]+)', 'releases/sanitized', response['url'])
            response['url'] = re.sub('searches/([^/?&]+)', 'searches/sanitized', response['url'])
            response['url'] = re.sub('phoneNumbers/[%2B\d]+', 'phoneNumbers/sanitized', response['url'])
            response['url'] = re.sub('^(.*?)\.communication.azure.com', 'https://sanitized.communication.azure.com', response['url'])
        return response 