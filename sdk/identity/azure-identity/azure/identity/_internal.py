# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# ------------------------------------------------------------------------
import os

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, Mapping, Optional, Type
    from azure.core.credentials import AccessToken

from azure.core import Configuration
from azure.core.pipeline.policies import ContentDecodePolicy, HeadersPolicy, NetworkTraceLoggingPolicy, RetryPolicy

from ._authn_client import AuthnClient
from .constants import Endpoints, MSI_ENDPOINT, MSI_SECRET
from .exceptions import AuthenticationError


class _ManagedIdentityBase(object):
    def __init__(self, endpoint, client_cls, config=None, **kwargs):
        # type: (str, Type, Optional[Configuration], Mapping[str, Any]) -> None
        config = config or self.create_config(**kwargs)
        policies = [ContentDecodePolicy(), config.headers_policy, config.retry_policy, config.logging_policy]
        self._client = client_cls(endpoint, config, policies, **kwargs)

    @staticmethod
    def create_config(**kwargs):
        # type: (Mapping[str, Any]) -> Configuration
        timeout = kwargs.pop("connection_timeout", 2)
        config = Configuration(connection_timeout=timeout, **kwargs)

        # retry is the only IO policy, so its class is a kwarg to increase async code sharing
        retry_policy = kwargs.pop("retry_policy", RetryPolicy)  # type: ignore
        config.retry_policy = retry_policy(**_ManagedIdentityBase._retry_settings, **kwargs)  # type: ignore

        # Metadata header is required by IMDS and in Cloud Shell; App Service ignores it
        config.headers_policy = HeadersPolicy(base_headers={"Metadata": "true"}, **kwargs)
        config.logging_policy = NetworkTraceLoggingPolicy(**kwargs)

        return config

    # given RetryPolicy's implementation, these settings most closely match the documented guidance for IMDS
    # https://docs.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/how-to-use-vm-token#retry-guidance
    _retry_settings = {
        "retry_total": 5,
        "retry_status": 5,
        "retry_backoff_factor": 4,
        "retry_backoff_max": 60,
        "retry_on_status_codes": [404, 429] + list(range(500, 600)),
    }


class ImdsCredential(_ManagedIdentityBase):
    """Authenticates with a managed identity via the IMDS endpoint"""

    def __init__(self, config=None, **kwargs):
        # type: (Optional[Configuration], Mapping[str, Any]) -> None
        super(ImdsCredential, self).__init__(endpoint=Endpoints.IMDS, client_cls=AuthnClient, config=config, **kwargs)
        self._endpoint_available = None  # type: Optional[bool]

    def get_token(self, *scopes):
        # type: (*str) -> AccessToken
        if self._endpoint_available is None:
            # Lacking another way to determine whether the IMDS endpoint is listening,
            # we send a request it would immediately reject (missing header, wrong verb),
            # setting a short timeout. The timeout was chosen by benchmarking: of 2000
            # requests, the slowest was 14ms, 99th percentile was 7ms, mean was 3.7ms.
            try:
                self._client.request_token(scopes, connection_timeout=0.17)
                self._endpoint_available = True
            except AuthenticationError:
                # received a response that couldn't be deserialized because it was an error response)
                self._endpoint_available = True
            except Exception:  # pylint:disable=broad-except
                self._endpoint_available = False

        if not self._endpoint_available:
            raise AuthenticationError("IMDS endpoint unavailable")

        if len(scopes) != 1:
            raise ValueError("this credential supports one scope per request")

        token = self._client.get_cached_token(scopes)
        if not token:
            resource = scopes[0]
            if resource.endswith("/.default"):
                resource = resource[: -len("/.default")]
            token = self._client.request_token(
                scopes, method="GET", params={"api-version": "2018-02-01", "resource": resource}
            )
        return token


class MsiCredential(_ManagedIdentityBase):
    """Authenticates via the MSI endpoint"""

    def __init__(self, config=None, **kwargs):
        # type: (Optional[Configuration], Mapping[str, Any]) -> None
        endpoint = os.environ.get(MSI_ENDPOINT)
        self._endpoint_available = endpoint is not None
        if self._endpoint_available:
            super(MsiCredential, self).__init__(  # type: ignore
                endpoint=endpoint, client_cls=AuthnClient, config=config, **kwargs
            )

    def get_token(self, *scopes):
        # type: (*str) -> AccessToken
        if not self._endpoint_available:
            raise AuthenticationError("MSI endpoint unavailable")

        if len(scopes) != 1:
            raise ValueError("this credential supports only one scope per request")

        token = self._client.get_cached_token(scopes)
        if not token:
            resource = scopes[0]
            if resource.endswith("/.default"):
                resource = resource[: -len("/.default")]
            # TODO: support user-assigned client id
            secret = os.environ.get(MSI_SECRET)
            if secret:
                # MSI_ENDPOINT and MSI_SECRET set -> App Service
                token = self._client.request_token(
                    scopes,
                    method="GET",
                    headers={"secret": secret},
                    params={"api-version": "2017-09-01", "resource": resource},
                )
            else:
                # only MSI_ENDPOINT set -> legacy-style MSI (Cloud Shell)
                token = self._client.request_token(scopes, method="POST", form_data={"resource": resource})
        return token
