# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from . import HTTPPolicy

try:
    from typing import TYPE_CHECKING  # pylint:disable=unused-import
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, Dict, Iterable, Mapping
    from azure.core.credentials import SupportsGetToken
    from azure.core.pipeline import PipelineRequest, PipelineResponse


# pylint:disable=too-few-public-methods
class _BearerTokenCredentialPolicyBase(object):
    def __init__(self, credential, scopes, **kwargs):  # pylint:disable=unused-argument
        # type: (SupportsGetToken, Iterable[str], Mapping[str, Any]) -> None
        super(_BearerTokenCredentialPolicyBase, self).__init__()
        self._scopes = scopes
        self._credential = credential

    @staticmethod
    def _update_headers(headers, token):
        # type: (Dict[str, str], str) -> None
        headers["Authorization"] = "Bearer {}".format(token)


class BearerTokenCredentialPolicy(_BearerTokenCredentialPolicyBase, HTTPPolicy):
    """Adds a bearer token Authorization header to requests."""

    def send(self, request):
        # type: (PipelineRequest) -> PipelineResponse
        token = self._credential.get_token(self._scopes)
        self._update_headers(request.http_request.headers, token) # type: ignore
        return self.next.send(request)
