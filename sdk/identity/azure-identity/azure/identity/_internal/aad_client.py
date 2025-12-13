# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
import logging
import os
from typing import Iterable, Union, Optional, Any

from azure.core.credentials import AccessTokenInfo
from azure.core.pipeline import Pipeline
from azure.core.pipeline.transport import HttpRequest
from .aad_client_base import AadClientBase
from .aadclient_certificate import AadClientCertificate
from .pipeline import build_pipeline
from .._enums import RegionalAuthority


_LOGGER = logging.getLogger(__name__)


class AadClient(AadClientBase):  # pylint:disable=client-accepts-api-version-keyword

    # pylint:disable=missing-client-constructor-parameter-credential
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def __enter__(self) -> "AadClient":
        self._pipeline.__enter__()
        return self

    def __exit__(self, *args):
        self._pipeline.__exit__(*args)

    def close(self) -> None:
        self.__exit__()

    def obtain_token_by_authorization_code(
        self, scopes: Iterable[str], code: str, redirect_uri: str, client_secret: Optional[str] = None, **kwargs: Any
    ) -> AccessTokenInfo:
        self._initialize_regional_authority()
        request = self._get_auth_code_request(
            scopes=scopes, code=code, redirect_uri=redirect_uri, client_secret=client_secret, **kwargs
        )
        return self._run_pipeline(request, **kwargs)

    def obtain_token_by_client_certificate(
        self, scopes: Iterable[str], certificate: AadClientCertificate, **kwargs: Any
    ) -> AccessTokenInfo:
        self._initialize_regional_authority()
        request = self._get_client_certificate_request(scopes, certificate, **kwargs)
        return self._run_pipeline(request, **kwargs)

    def obtain_token_by_client_secret(self, scopes: Iterable[str], secret: str, **kwargs: Any) -> AccessTokenInfo:
        self._initialize_regional_authority()
        request = self._get_client_secret_request(scopes, secret, **kwargs)
        return self._run_pipeline(request, **kwargs)

    def obtain_token_by_jwt_assertion(self, scopes: Iterable[str], assertion: str, **kwargs: Any) -> AccessTokenInfo:
        self._initialize_regional_authority()
        request = self._get_jwt_assertion_request(scopes, assertion, **kwargs)
        return self._run_pipeline(request, **kwargs)

    def obtain_token_by_refresh_token(
        self, scopes: Iterable[str], refresh_token: str, **kwargs: Any
    ) -> AccessTokenInfo:
        self._initialize_regional_authority()
        request = self._get_refresh_token_request(scopes, refresh_token, **kwargs)
        return self._run_pipeline(request, **kwargs)

    def obtain_token_on_behalf_of(
        self,
        scopes: Iterable[str],
        client_credential: Union[str, AadClientCertificate],
        user_assertion: str,
        **kwargs: Any
    ) -> AccessTokenInfo:
        # no need for an implementation, non-async OnBehalfOfCredential acquires tokens through MSAL
        raise NotImplementedError()

    def _initialize_regional_authority(self) -> None:
        # This is based on MSAL's regional authority logic.
        if self._regional_authority is not False:
            return

        regional_authority = self._get_regional_authority_from_env()
        if not regional_authority:
            self._regional_authority = None
            return

        if regional_authority in [RegionalAuthority.AUTO_DISCOVER_REGION, "true"]:
            regional_authority = self._discover_region()
            if not regional_authority:
                _LOGGER.info("Failed to auto-discover region. Using the non-regional authority.")
                self._regional_authority = None
                return

        self._regional_authority = self._build_regional_authority_url(regional_authority)

    def _discover_region(self) -> Optional[str]:
        region = os.environ.get("REGION_NAME", "").replace(" ", "").lower()
        if region:
            return region
        try:
            request = self._get_region_discovery_request()
            response = self._pipeline.run(request)
            return self._process_region_discovery_response(response)
        except Exception as ex:  # pylint: disable=broad-except
            _LOGGER.debug("Failed to discover Azure region from IMDS: %s", ex)
            return None

    def _build_pipeline(self, **kwargs: Any) -> Pipeline:
        return build_pipeline(**kwargs)

    def _run_pipeline(self, request: HttpRequest, **kwargs: Any) -> AccessTokenInfo:
        # remove tenant_id and claims kwarg that could have been passed from credential's get_token method
        # tenant_id is already part of `request` at this point
        kwargs.pop("tenant_id", None)
        kwargs.pop("claims", None)
        kwargs.pop("client_secret", None)
        enable_cae = kwargs.pop("enable_cae", False)
        now = int(time.time())
        response = self._pipeline.run(request, retry_on_methods=self._POST, **kwargs)
        return self._process_response(response, now, enable_cae=enable_cae, **kwargs)
