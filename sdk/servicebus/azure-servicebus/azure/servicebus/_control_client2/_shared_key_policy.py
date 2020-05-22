import time
from threading import Lock
import six
from azure.core.pipeline.policies import SansIOHTTPPolicy
from .._base_handler import ServiceBusSharedKeyCredential


class ServiceBusSharedKeyCredentialPolicy(SansIOHTTPPolicy):
    def __init__(self, endpoint, credential, name):
        # type: (str, ServiceBusSharedKeyCredential, str) -> None
        super(ServiceBusSharedKeyCredentialPolicy, self).__init__()
        self._credential = credential
        self._endpoint = endpoint
        if not name:
            raise ValueError("name can not be None or empty")
        if not isinstance(name, six.string_types):
            raise TypeError("name must be a string.")
        self._name = name
        self._token_expiry_on = 0
        self._token = None
        self._lock = Lock()

    def _update_token(self):
        if self._token_expiry_on + 60 <= time.time():  # Update token if it's expiring in 60 seconds
            with self._lock:
                if self._token_expiry_on + 60 <= time.time():  # recheck to avoid concurrent update
                    token, expiry_on = self._credential.get_token(self._endpoint)
                    self._token = token.decode("utf-8")
                    self._token_expiry_on = expiry_on

    def on_request(self, request):
        self._update_token()
        request.http_request.headers[self._name] = self._token
