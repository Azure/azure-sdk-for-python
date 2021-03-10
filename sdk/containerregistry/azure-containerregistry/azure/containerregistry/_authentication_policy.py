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
        token = "{}:{}".format(self._user, self._password)
        token = bytes(token, "utf-8")
        return str(b64encode(token))


class ContainerRegistryUserCredentialPolicy(SansIOHTTPPolicy):
    """HTTP pipeline policy to authenticate using ContainerRegistryUserCredential"""
    def __init__(self, credential):
        self.credential = credential

    def _enforce_https(self, request):
        # Copied from BearerTokenCredentialPolicy
        option = request.context.options.pop("enforce_https", None)

        if option is False:
            request.context["enforce_https"] = option

        enforce_https = request.context.get("enforce_https", True)
        if enforce_https and not request.http_request.url.lower().startswith("https"):
            raise Exception(
                "Auth is not permitted for non-TLS protected (non-https) URLs."
            )

    @staticmethod
    def _update_headers(headers, token):
        headers["Authorization"] = "Basic {}".format(token)

    def on_request(self, request):
        # type: (PipelineRequest) -> None
        # self._enforce_https(request)
        self._update_headers(request.http_request.headers, self.credential.get_token())
