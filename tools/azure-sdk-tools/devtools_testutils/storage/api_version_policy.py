from azure.core.pipeline.policies import SansIOHTTPPolicy


class ApiVersionAssertPolicy(SansIOHTTPPolicy):
    """
    Assert the ApiVersion is set properly on the response
    """

    def __init__(self, api_version):
        self.api_version = api_version

    def on_request(self, request):
        assert request.http_request.headers["x-ms-version"] == self.api_version
