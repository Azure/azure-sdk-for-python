# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from typing import TYPE_CHECKING

from .aad_client_base import AadClientBase
from .._internal.pipeline import build_pipeline

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, Iterable, Optional, Union
    from azure.core.credentials import AccessToken
    from azure.core.pipeline import Pipeline
    from .._internal import AadClientCertificate


class AadClient(AadClientBase):
    def __enter__(self):
        self._pipeline.__enter__()
        return self

    def __exit__(self, *args):
        self._pipeline.__exit__(*args)

    def close(self):
        # type: () -> None
        self.__exit__()

    def obtain_token_by_authorization_code(self, scopes, code, redirect_uri, client_secret=None, **kwargs):
        # type: (Iterable[str], str, str, Optional[str], **Any) -> AccessToken
        request = self._get_auth_code_request(
            scopes=scopes, code=code, redirect_uri=redirect_uri, client_secret=client_secret, **kwargs
        )
        now = int(time.time())
        response = self._pipeline.run(request, stream=False, retry_on_methods=self._POST, **kwargs)
        return self._process_response(response, now)

    def obtain_token_by_client_certificate(self, scopes, certificate, **kwargs):
        # type: (Iterable[str], AadClientCertificate, **Any) -> AccessToken
        request = self._get_client_certificate_request(scopes, certificate, **kwargs)
        now = int(time.time())
        response = self._pipeline.run(request, stream=False, retry_on_methods=self._POST, **kwargs)
        return self._process_response(response, now)

    def obtain_token_by_client_secret(self, scopes, secret, **kwargs):
        # type: (Iterable[str], str, **Any) -> AccessToken
        request = self._get_client_secret_request(scopes, secret, **kwargs)
        now = int(time.time())
        response = self._pipeline.run(request, stream=False, retry_on_methods=self._POST, **kwargs)
        return self._process_response(response, now)

    def obtain_token_by_jwt_assertion(self, scopes, assertion, **kwargs):
        # type: (Iterable[str], str, **Any) -> AccessToken
        request = self._get_jwt_assertion_request(scopes, assertion)
        now = int(time.time())
        response = self._pipeline.run(request, stream=False, retry_on_methods=self._POST, **kwargs)
        return self._process_response(response, now)

    def obtain_token_by_refresh_token(self, scopes, refresh_token, **kwargs):
        # type: (Iterable[str], str, **Any) -> AccessToken
        request = self._get_refresh_token_request(scopes, refresh_token, **kwargs)
        now = int(time.time())
        response = self._pipeline.run(request, stream=False, retry_on_methods=self._POST, **kwargs)
        return self._process_response(response, now)

    def obtain_token_on_behalf_of(self, scopes, client_credential, user_assertion, **kwargs):
        # type: (Iterable[str], Union[str, AadClientCertificate], str, **Any) -> AccessToken
        # no need for an implementation, non-async OnBehalfOfCredential acquires tokens through MSAL
        raise NotImplementedError()

    # pylint:disable=no-self-use
    def _build_pipeline(self, **kwargs):
        # type: (**Any) -> Pipeline
        return build_pipeline(**kwargs)
