# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import threading
from typing import TYPE_CHECKING

from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.core.pipeline.policies._authentication import _BearerTokenCredentialPolicyBase

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any
    from azure.core.credentials_async import AsyncTokenCredential
    from azure.core.pipeline import PipelineRequest


class AsyncBearerTokenCredentialPolicy(_BearerTokenCredentialPolicyBase, SansIOHTTPPolicy):
    # pylint:disable=too-few-public-methods
    """Adds a bearer token Authorization header to requests.

    :param credential: The credential.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential
    :param str scopes: Lets you specify the type of access needed.
    """

    def __init__(self, credential: "AsyncTokenCredential", *scopes: str, **kwargs: "Any") -> None:
        self._credential = credential
        self._lock = threading.Lock()
        super().__init__(*scopes, **kwargs)

    async def on_request(self, request: "PipelineRequest"):
        """Adds a bearer token Authorization header to request and sends request to next policy.

        :param request: The pipeline request object to be modified.
        :type request: ~azure.core.pipeline.PipelineRequest
        :raises: :class:`~azure.core.exceptions.ServiceRequestError`
        """
        self._enforce_tls(request)

        with self._lock:
            if self._need_new_token:
                self._token = await self._credential.get_token(*self._scopes)  # type: ignore
        self._update_headers(request.http_request.headers, self._token.token)  # type: ignore
