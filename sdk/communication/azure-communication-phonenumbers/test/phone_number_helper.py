# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure_devtools.scenario_tests import RecordingProcessor
from _shared.testcase import ResponseReplacerProcessor

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

class PhoneNumberResponseReplacerProcessor(ResponseReplacerProcessor):

    def process_response(self, response):
        import json
        try:
            body = json.loads(response['body']['string'])
            if 'phoneNumbers' in body:
                for item in body["phoneNumbers"]:
                    if isinstance(item, str):
                        body["phoneNumbers"] = [self._replacement]
                        break
                    if "phoneNumber" in item:
                        item['phoneNumber'] = self._replacement
                    if "id" in item:
                        item['id'] = self._replacement
            response['body']['string'] = json.dumps(body)
            response['url'] = self._replacement
            return response
        except (KeyError, ValueError, TypeError):
            return response

 