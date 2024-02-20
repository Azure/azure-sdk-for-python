import re

from azure_devtools.scenario_tests import RecordingProcessor

class DomainReplacerProcessor(RecordingProcessor):
    """Sanitize the domain name in both request and response"""

    def __init__(self, replacement=".sanitized.com", regex_pattern="\.[0-9a-fA-F]{32}\.com"):
        self._replacement = replacement
        self._regex_pattern = regex_pattern
        
    def process_request(self, request):
        if request.body is not None:
            request.body = re.sub(self._regex_pattern, self._replacement, request.body.decode()).encode()

        return request

    def process_response(self, response):
        if response['body']['string']:
            response['body']['string'] = re.sub(self._regex_pattern, self._replacement, response['body']['string'])

        return response
