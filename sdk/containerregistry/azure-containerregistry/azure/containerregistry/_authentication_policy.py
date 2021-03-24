# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from base64 import b64encode
import re
from typing import TYPE_CHECKING

from azure.core.pipeline.policies import SansIOHTTPPolicy

if TYPE_CHECKING:
    from azure.core.pipeline import PipelineRequest


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
        self._credential = credential

    @staticmethod
    def _update_headers(headers, token):
        headers["Authorization"] = "Basic {}".format(token)

    def on_request(self, request):
        # type: (PipelineRequest) -> None
        self._update_headers(request.http_request.headers, self._credential.get_token())


class ContainerRegistryCredentialPolicy(SansIOHTTPPolicy):
    """Challenge based authentication policy for ACR. This policy is used for getting
    the AAD Token, refresh token, and access token before performing a call to service.

    :param credential: Azure Token Credential for authenticating with Azure
    :type credential: TokenCredential
    """

    BEARER = "Bearer"
    AUTHENTICATION_CHALLENGE_PARAMS_PATTERN = re.compile('(?:(\\w+)="([^""]*)")+')
    WWW_AUTHENTICATE = "WWW-Authenticate"
    SCOPE_PARAMETER = "scope"
    SERVICE_PARAMETER = "service"
    AUTHORIZATION = "Authorization"

    def __init__(self, credential, url, pipeline):
        self._credential = credential
        self.url = url
        self.pipeline = pipeline
