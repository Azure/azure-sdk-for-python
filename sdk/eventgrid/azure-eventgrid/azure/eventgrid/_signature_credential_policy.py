import six

from azure.core.pipeline.policies import SansIOHTTPPolicy

class EventGridSharedAccessSignatureCredentialPolicy(SansIOHTTPPolicy):
    """Adds a token header for the provided credential.
    :param credential: The credential used to authenticate requests.
    :type credential: ~azure.eventgrid.EventGridSharedAccessSignatureCredential
    :param str name: The name of the token header used for the credential.
    :raises: ValueError or TypeError
    """
    def __init__(self, credential, name, **kwargs):  # pylint: disable=unused-argument
        # type: (EventGridSharedAccessSignatureCredential, str, Any) -> None
        super(EventGridSharedAccessSignatureCredentialPolicy, self).__init__()
        self._credential = credential
        if not name:
            raise ValueError("name can not be None or empty")
        if not isinstance(name, six.string_types):
            raise TypeError("name must be a string.")
        self._name = name

    def on_request(self, request):
        request.http_request.headers[self._name] = self._credential.signature
