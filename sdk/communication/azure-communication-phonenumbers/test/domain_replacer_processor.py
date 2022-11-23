from azure_devtools.scenario_tests import RecordingProcessor

class DomainReplacerProcessor(RecordingProcessor):
    """Sanitize the domain name in both request and response"""

    def __init__(self, replacement="sanitized.com", domain=None):
        self._replacement = replacement
        self._domain = domain
        
    def process_request(self, request):
        if request.body is not None:
            request.body = request.body.decode().replace(self._domain,self._replacement).encode()

        return request

    def process_response(self, response):
        if response['body']['string']:
            response['body']['string'] = response['body']['string'].replace(self._domain,self._replacement)

        return response
