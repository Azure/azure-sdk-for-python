# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from typing import Iterable, Union

from azure.core.credentials import AccessToken
from azure.core.pipeline import Pipeline
from azure.core.pipeline.transport import HttpRequest
from .aad_client_base import AadClientBase
from .aadclient_certificate import AadClientCertificate
from .pipeline import build_pipeline


class AadClient(AadClientBase):
    def __enter__(self):
        self._pipeline.__enter__()
        return self

    def __exit__(self, *args):
        self._pipeline.__exit__(*args)

    def close(self) -> None:
        self.__exit__()

    def obtain_token_by_authorization_code(
            self,
            scopes: Iterable[str],
            code: str,
            redirect_uri: str,
            client_secret: str = None,
            **kwargs
    ) -> AccessToken:
        request = self._get_auth_code_request(
            scopes=scopes, code=code, redirect_uri=redirect_uri, client_secret=client_secret, **kwargs
        )
        return self._run_pipeline(request, **kwargs)

    def obtain_token_by_client_certificate(
            self,
            scopes: Iterable[str],
            certificate: AadClientCertificate,
            **kwargs
    ) -> AccessToken:
        request = self._get_client_certificate_request(scopes, certificate, **kwargs)
        return self._run_pipeline(request, **kwargs)

    def obtain_token_by_client_secret(
            self,
            scopes: Iterable[str],
            secret: str,
            **kwargs
    ) -> AccessToken:
        request = self._get_client_secret_request(scopes, secret, **kwargs)
        return self._run_pipeline(request, **kwargs)

    def obtain_token_by_jwt_assertion(
            self,
            scopes: Iterable[str],
            assertion: str,
            **kwargs
    ) -> AccessToken:
        request = self._get_jwt_assertion_request(scopes, assertion)
        return self._run_pipeline(request, **kwargs)

    def obtain_token_by_refresh_token(
            self,
            scopes: Iterable[str],
            refresh_token: str,
            **kwargs
    ) -> AccessToken:
        request = self._get_refresh_token_request(scopes, refresh_token, **kwargs)
        return self._run_pipeline(request, **kwargs)

    def obtain_token_on_behalf_of(
            self,
            scopes: Iterable[str],
            client_credential: Union[str, AadClientCertificate],
            user_assertion: str,
            **kwargs
    ) -> AccessToken:
        # no need for an implementation, non-async OnBehalfOfCredential acquires tokens through MSAL
        raise NotImplementedError()

    # pylint:disable=no-self-use
    def _build_pipeline(self, **kwargs) -> Pipeline:
        return build_pipeline(**kwargs)

    def _run_pipeline(self, request: HttpRequest, **kwargs) -> AccessToken:
        # remove tenant_id and claims kwarg that could have been passed from credential's get_token method
        # tenant_id is already part of `request` at this point
        kwargs.pop("tenant_id", None)
        kwargs.pop("claims", None)
        now = int(time.time())
        response = self._pipeline.run(request, retry_on_methods=self._POST, **kwargs)
        return self._process_response(response, now)
