# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
import os
import time
from typing import Iterable, Optional, Union, Dict, Any

from azure.core.credentials import AccessTokenInfo
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.policies import AsyncHTTPPolicy, SansIOHTTPPolicy
from azure.core.pipeline.transport import HttpRequest
from ..._internal import AadClientCertificate
from ..._internal import AadClientBase
from ..._internal.pipeline import build_async_pipeline
from ..._enums import RegionalAuthority

Policy = Union[AsyncHTTPPolicy, SansIOHTTPPolicy]

_LOGGER = logging.getLogger(__name__)


# pylint:disable=invalid-overridden-method
class AadClient(AadClientBase):
    async def __aenter__(self) -> "AadClient":
        await self._pipeline.__aenter__()
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def close(self) -> None:
        """Close the client's transport session."""

        await self._pipeline.__aexit__()

    async def obtain_token_by_authorization_code(
        self, scopes: Iterable[str], code: str, redirect_uri: str, client_secret: Optional[str] = None, **kwargs
    ) -> AccessTokenInfo:
        await self._initialize_regional_authority()
        request = self._get_auth_code_request(
            scopes=scopes, code=code, redirect_uri=redirect_uri, client_secret=client_secret, **kwargs
        )
        return await self._run_pipeline(request, **kwargs)

    async def obtain_token_by_client_certificate(
        self, scopes: Iterable[str], certificate: AadClientCertificate, **kwargs
    ) -> AccessTokenInfo:
        await self._initialize_regional_authority()
        request = self._get_client_certificate_request(scopes, certificate, **kwargs)
        return await self._run_pipeline(request, stream=False, **kwargs)

    async def obtain_token_by_client_secret(self, scopes: Iterable[str], secret: str, **kwargs) -> AccessTokenInfo:
        await self._initialize_regional_authority()
        request = self._get_client_secret_request(scopes, secret, **kwargs)
        return await self._run_pipeline(request, **kwargs)

    async def obtain_token_by_jwt_assertion(self, scopes: Iterable[str], assertion: str, **kwargs) -> AccessTokenInfo:
        await self._initialize_regional_authority()
        request = self._get_jwt_assertion_request(scopes, assertion, **kwargs)
        return await self._run_pipeline(request, stream=False, **kwargs)

    async def obtain_token_by_refresh_token(
        self, scopes: Iterable[str], refresh_token: str, **kwargs
    ) -> AccessTokenInfo:
        await self._initialize_regional_authority()
        request = self._get_refresh_token_request(scopes, refresh_token, **kwargs)
        return await self._run_pipeline(request, **kwargs)

    async def obtain_token_by_refresh_token_on_behalf_of(  # pylint: disable=name-too-long
        self,
        scopes: Iterable[str],
        client_credential: Union[str, AadClientCertificate, Dict[str, Any]],
        refresh_token: str,
        **kwargs
    ) -> AccessTokenInfo:
        await self._initialize_regional_authority()
        request = self._get_refresh_token_on_behalf_of_request(
            scopes, client_credential=client_credential, refresh_token=refresh_token, **kwargs
        )
        return await self._run_pipeline(request, **kwargs)

    async def obtain_token_on_behalf_of(
        self,
        scopes: Iterable[str],
        client_credential: Union[str, AadClientCertificate, Dict[str, Any]],
        user_assertion: str,
        **kwargs
    ) -> AccessTokenInfo:
        await self._initialize_regional_authority()
        request = self._get_on_behalf_of_request(
            scopes=scopes, client_credential=client_credential, user_assertion=user_assertion, **kwargs
        )
        return await self._run_pipeline(request, **kwargs)

    def _build_pipeline(self, **kwargs) -> AsyncPipeline:
        return build_async_pipeline(**kwargs)

    async def _initialize_regional_authority(self) -> None:
        # This is based on MSAL's regional authority logic.
        if self._regional_authority is not False:
            return

        regional_authority = self._get_regional_authority_from_env()
        if not regional_authority:
            self._regional_authority = None
            return

        if regional_authority == RegionalAuthority.AUTO_DISCOVER_REGION:
            # Attempt to discover the region from IMDS
            regional_authority = await self._discover_region()
            if not regional_authority:
                _LOGGER.info("Failed to auto-discover region. Using the non-regional authority.")
                self._regional_authority = None
                return

        self._regional_authority = self._build_regional_authority_url(regional_authority)

    async def _discover_region(self) -> Optional[str]:
        region = os.environ.get("REGION_NAME", "").replace(" ", "").lower()
        if region:
            return region
        try:
            request = self._get_region_discovery_request()
            response = await self._pipeline.run(request)
            return self._process_region_discovery_response(response)
        except Exception as ex:  # pylint: disable=broad-except
            _LOGGER.debug("Failed to discover Azure region from IMDS: %s", ex)
            return None

    async def _run_pipeline(self, request: HttpRequest, **kwargs) -> AccessTokenInfo:
        # remove tenant_id and claims kwarg that could have been passed from credential's get_token method
        # tenant_id is already part of `request` at this point
        kwargs.pop("tenant_id", None)
        kwargs.pop("claims", None)
        kwargs.pop("client_secret", None)
        enable_cae = kwargs.pop("enable_cae", False)
        now = int(time.time())
        response = await self._pipeline.run(request, retry_on_methods=self._POST, **kwargs)
        return self._process_response(response, now, enable_cae=enable_cae, **kwargs)
