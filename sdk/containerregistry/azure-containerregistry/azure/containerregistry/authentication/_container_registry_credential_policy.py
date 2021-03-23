# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import re
from typing import TYPE_CHECKING

from azure.core.pipeline.policies import ChallengeAuthenticationPolicy

from ._container_registry_token_service import ContainerRegistryTokenService

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    from typing import List


# Follows challenge based authorization scheme

# For example:

# 1. GET /api/vr/acr/repositories (no authorization included)
#     Return Header: 401: www-authenticate header - Bearer realm="{url}",service="{service_name}",scope="{scope}",error="invalid_token".

# 2. Parse service_name, scope from the service

# 3. POST /api/oauth2/exchange (grant-type=refresh_token)
#     Request Body: {service, scope, grant-type, aadToken w/ ARM scope}
#     Response Body: {acr refresh token}

# 4. POST /api/oauth2/token  (grant-type=access_token)
#     Request Body: {acr refresh token, scope, grant-type}
#     Response Body: {acr access token}

# 5. GET /api/v1/acr/repositories
#     Request Header: {Bearer acr acces token}


class ContainerRegistryCredentialPolicy(ChallengeAuthenticationPolicy):
    """Challenge based authentication policy for ACR. This policy is used for getting
    the AAD Token, refresh token, and access token before performing a call to service.

    :param TokenCredential credential: Azure Token Credential for authenticating with Azure
    :param str url: base URL for ACR account
    """

    BEARER = "Bearer"
    AUTHENTICATION_CHALLENGE_PARAMS_PATTERN = re.compile("(?:(\\w+)=\"([^\"\"]*)\")+")
    WWW_AUTHENTICATE = "WWW-Authenticate"
    SCOPE_PARAMETER = "scope"
    SERVICE_PARAMETER = "service"
    AUTHORIZATION = "Authorization"

    def __init__(self, credential, url, pipeline):
        # type: (TokenCredential, str, HttpPipeline) -> None
        self.credential = credential
        self.url = url
        self.pipeline = pipeline
        self.container_registry_token_service = ContainerRegistryTokenService(
            credential, url, pipeline
        )

    @classmethod
    def from_token_service(cls, token_service):
        # type: (ContainerRegistryTokenService) -> ContainerRegistryCredentialPolicy
        return cls(token_service.credential, token_service.url, token_service.pipeline)

    def process(self, context, next):
        # type: (HttpPipelineContext, HttpPipelinePolicy) -> HttpResponse
        if not self.url.startswith("https"):
            raise ValueError("Token Credentials require a URL using the HTTPS protocol scheme")

        http_response = next.process()
        auth_header = http_response.headers[self.WWW_AUTHENTICATE]
        if http_response.status_code == 401 and auth_header is not None:
            return None

    def authorize_request(self, context, token_request_context):
        # type: (HttpPipelineContext, ContainerRegistryTokenRequestContext) -> None
        context.http_request.headers[self.AUTHORIZATION] = "{} {}".format(
            self.BEARER,
            self.token_service.get_token()
        )

    def on_request(self, request):
        # type: (PipelineRequest) -> None
        """Called before the policy sends a request"""
        pass

    def send(self, request):
        # type: (PipelineRequest) -> PipelineResponse
        """Authorizes a request with a bearer token, possibly handling an authentication challenge"""

        pass

    def authorize_request(self, context, token_request_context):
        # type: (HttpPipelineCallContext, ContainerRegistryTokenRequestContext) -> None
        pass

    def on_challenge(self, context, response):
        # type: (HttpPipelineCallContext, HttpResponse) -> bool
        return False

    def parse_bearer_challenge(self, header):
        # type: (str) -> dict[str, str]
        if header.startswith(self.BEARER):
            challenge_params = header[len(self.BEARER)+1:]

            matches = re.split(self.AUTHENTICATION_CHALLENGE_PARAMS_PATTERN, challenge_params)
            self._clean(matches)
            ret = {}
            for i in range(len(matches), 2):
                ret[matches[i]] = matches[i+1]

            return ret

        return {}

    def _clean(self, matches):
        # type: (List[str]) -> None
        while:
            try:
                matches.remove('')
            except ValueError:
                break

        while:
            try:
                matches.remove(',')
            except ValueError:
                return