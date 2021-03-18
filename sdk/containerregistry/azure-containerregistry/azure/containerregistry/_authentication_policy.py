# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from base64 import b64encode

from azure.core.pipeline.policies import SansIOHTTPPolicy


class ContainerRegistryUserCredential(object):
    """Credential used to authenticate with Container Registry service"""

    def __init__(self, username, password):
        self._user = username
        self._password = password

    def get_token(self):
        token_str = "{}:{}".format(self._user, self._password)
        token_bytes = token_str.encode("ascii")
        b64_bytes = b64encode(token_bytes)
        return b64_bytes.decode("ascii")


class ContainerRegistryUserCredentialPolicy(SansIOHTTPPolicy):
    """HTTP pipeline policy to authenticate using ContainerRegistryUserCredential"""

    def __init__(self, credential):
        self.credential = credential

    @staticmethod
    def _update_headers(headers, token):
        headers["Authorization"] = "Basic {}".format(token)

    def on_request(self, request):
        # type: (PipelineRequest) -> None
        self._update_headers(request.http_request.headers, self.credential.get_token())
