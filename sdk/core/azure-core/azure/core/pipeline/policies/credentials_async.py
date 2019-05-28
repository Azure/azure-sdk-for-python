# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core.pipeline import PipelineRequest, PipelineResponse
from azure.core.pipeline.policies import AsyncHTTPPolicy
from azure.core.pipeline.policies.credentials import _BearerTokenCredentialPolicyBase


class AsyncBearerTokenCredentialPolicy(_BearerTokenCredentialPolicyBase, AsyncHTTPPolicy):
    # pylint:disable=too-few-public-methods
    """Adds a bearer token Authorization header to requests.

    :param credential: The credential.
    :type credential: ~azure.core.SupportsGetToken
    :param str scopes: Lets you specify the type of access needed.
    """

    async def send(self, request: PipelineRequest) -> PipelineResponse:
        """Aync flavor that adds a bearer token Authorization header to request and sends request to next policy.

        :param request: The pipeline request object to be modified.
        :type request: ~azure.core.pipeline.PipelineRequest
        :return: The pipeline response object
        :rtype: ~azure.core.pipeline.PipelineResponse
        """
        token = await self._credential.get_token(self._scopes) # type: ignore
        self._update_headers(request.http_request.headers, token) # type: ignore
        return await self.next.send(request) # type: ignore
