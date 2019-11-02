from azure.core.pipeline.policies import SansIOHTTPPolicy


class CognitiveServicesCredentialPolicy(SansIOHTTPPolicy):

    def __init__(self, cognitiveservices_key, **kwargs):
        if cognitiveservices_key is None:
            raise ValueError("Parameter 'credential' must not be None.")
        self.cognitiveservices_key = cognitiveservices_key
        super(CognitiveServicesCredentialPolicy, self).__init__()

    def on_request(self, request):
        request.http_request.headers["Ocp-Apim-Subscription-Key"] = self.cognitiveservices_key
        request.http_request.headers["X-BingApis-SDK-Client"] = "Python-SDK"