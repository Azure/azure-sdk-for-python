# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from typing import TYPE_CHECKING

from ..._internal import AadClientBase
from ..._internal.pipeline import build_async_pipeline

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, Iterable, Optional, Union
    from azure.core.credentials import AccessToken
    from azure.core.pipeline import AsyncPipeline
    from azure.core.pipeline.policies import AsyncHTTPPolicy, SansIOHTTPPolicy
    from azure.core.pipeline.transport import HttpRequest
    from ..._internal import AadClientCertificate

    Policy = Union[AsyncHTTPPolicy, SansIOHTTPPolicy]


# pylint:disable=invalid-overridden-method
class AadClient(AadClientBase):
    async def __aenter__(self):
        await self._pipeline.__aenter__()
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def close(self) -> None:
        """Close the client's transport session."""

        await self._pipeline.__aexit__()

    async def obtain_token_by_authorization_code(
        self,
        scopes: "Iterable[str]",
        code: str,
        redirect_uri: str,
        client_secret: "Optional[str]" = None,
        **kwargs: "Any"
    ) -> "AccessToken":
        request = self._get_auth_code_request(
            scopes=scopes, code=code, redirect_uri=redirect_uri, client_secret=client_secret, **kwargs
        )
        return await self._run_pipeline(request, **kwargs)

    async def obtain_token_by_client_certificate(
        self, scopes: "Iterable[str]", certificate: "AadClientCertificate", **kwargs: "Any"
    ) -> "AccessToken":
        request = self._get_client_certificate_request(scopes, certificate, **kwargs)
        return await self._run_pipeline(request, stream=False, **kwargs)

    async def obtain_token_by_client_secret(
        self, scopes: "Iterable[str]", secret: str, **kwargs: "Any"
    ) -> "AccessToken":
        request = self._get_client_secret_request(scopes, secret, **kwargs)
        return await self._run_pipeline(request, **kwargs)

    async def obtain_token_by_jwt_assertion(
        self, scopes: "Iterable[str]", assertion: str, **kwargs: "Any"
    ) -> "AccessToken":
        request = self._get_jwt_assertion_request(scopes, assertion)
        return await self._run_pipeline(request, stream=False, **kwargs)

    async def obtain_token_by_refresh_token(
        self, scopes: "Iterable[str]", refresh_token: str, **kwargs: "Any"
    ) -> "AccessToken":
        request = self._get_refresh_token_request(scopes, refresh_token, **kwargs)
        return await self._run_pipeline(request, **kwargs)

    async def obtain_token_on_behalf_of(
        self,
        scopes: "Iterable[str]",
        client_credential: "Union[str, AadClientCertificate]",
        user_assertion: str,
        **kwargs: "Any"
    ) -> "AccessToken":
        request = self._get_on_behalf_of_request(
            scopes=scopes, client_credential=client_credential, user_assertion=user_assertion, **kwargs
        )
        return await self._run_pipeline(request, **kwargs)

    # pylint:disable=no-self-use
    def _build_pipeline(self, **kwargs: "Any") -> "AsyncPipeline":
        return build_async_pipeline(**kwargs)

    async def _run_pipeline(self, request: "HttpRequest", **kwargs: "Any") -> "AccessToken":
        # remove tenant_id kwarg that could have been passed from credential's get_token method
        # tenant_id is already part of `request` at this point
        kwargs.pop("tenant_id", None)
        now = int(time.time())
        response = await self._pipeline.run(request, retry_on_methods=self._POST, **kwargs)
        return self._process_response(response, now)
