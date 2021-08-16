from azure.core.credentials import AzureKeyCredential
from azure.core.pipeline._base import SansIOHTTPPolicy
from azure.core.pipeline.transport._base import HttpRequest
from azure.core.pipeline import PipelineRequest

class AzureKeyInQueryCredentialPolicy(SansIOHTTPPolicy):
    """Adds a key in query for the provided credential.

    :param credential: The credential used to authenticate requests.
    :type credential: ~azure.core.credentials.AzureKeyCredential
    :param str name: The name of the key in query used for the credential.
    :raises: ValueError or TypeError
    """

    def __init__(self, credential, name, **kwargs):  # pylint: disable=unused-argument
        # type: (AzureKeyCredential, str, **Any) -> None
        super(AzureKeyInQueryCredentialPolicy, self).__init__()
        self._credential = credential
        self._name = name

    def on_request(self, request: PipelineRequest):
        http_request: HttpRequest = request.http_request
        query = http_request.query
        query.update({self._name: self._credential.key})
        http_request.format_parameters(query)
        request.http_request = http_request

