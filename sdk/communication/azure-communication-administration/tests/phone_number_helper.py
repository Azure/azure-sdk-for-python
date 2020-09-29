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
        request.uri = re.sub('/identities/([^/?]+)', '/identities/sanitized', request.uri)
        return request

    def process_response(self, response):
        import re
        if 'url' in response:
            response['url'] = re.sub('/identities/([^/?]+)', '/identities/sanitized', response['url'])
            response['url'] = re.sub('phonePlanId=([^/?&]+)', 'phonePlanId=sanitized', response['url'])
            response['url'] = re.sub('capabilities/([^/?&]+)', 'capabilities/sanitized', response['url'])
            response['url'] = re.sub('phoneplangroups/([^/?&]+)', 'phoneplangroups/sanitized', response['url'])
            response['url'] = re.sub('phoneplans/([^/?&]+)', 'phoneplans/sanitized', response['url'])
            response['url'] = re.sub('releases/([^/?&]+)', 'releases/sanitized', response['url'])
            response['url'] = re.sub('searches/([^/?&]+)', 'searches/sanitized', response['url'])
        return response