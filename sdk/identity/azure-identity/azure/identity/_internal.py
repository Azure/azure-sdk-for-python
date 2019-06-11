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
    from typing import Any, Dict, Optional

from azure.core import Configuration
from azure.core.pipeline.policies import ContentDecodePolicy, HeadersPolicy, NetworkTraceLoggingPolicy, RetryPolicy

from ._authn_client import AuthnClient
from .constants import Endpoints, MSI_ENDPOINT, MSI_SECRET
from .exceptions import AuthenticationError


class ImdsCredential:
    """Authenticates with a managed identity via the IMDS endpoint"""

    def __init__(self, config=None, **kwargs):
        # type: (Optional[Configuration], Dict[str, Any]) -> None
        config = config or self.create_config(**kwargs)
        policies = [config.header_policy, ContentDecodePolicy(), config.logging_policy, config.retry_policy]
        self._client = AuthnClient(Endpoints.IMDS, config, policies, **kwargs)

    @staticmethod
    def create_config(**kwargs):
        # type: (Dict[str, str]) -> Configuration
        timeout = kwargs.pop("connection_timeout", 2)
        config = Configuration(connection_timeout=timeout, **kwargs)
        config.header_policy = HeadersPolicy(base_headers={"Metadata": "true"}, **kwargs)
        config.logging_policy = NetworkTraceLoggingPolicy(**kwargs)
        retries = kwargs.pop("retry_total", 5)
        config.retry_policy = RetryPolicy(
            retry_total=retries, retry_on_status_codes=[404, 429] + list(range(500, 600)), **kwargs
        )
        return config

    def get_token(self, *scopes):
        # type: (*str) -> str
        if len(scopes) != 1:
            raise ValueError("this credential supports one scope per request")
        token = self._client.get_cached_token(scopes)
        if not token:
            resource = scopes[0]
            if resource.endswith("/.default"):
                resource = resource[:-len("/.default")]
            token = self._client.request_token(
                scopes, method="GET", params={"api-version": "2018-02-01", "resource": resource}
            )
        return token


class MsiCredential:
    """Authenticates via the MSI endpoint"""

    def __init__(self, config=None, **kwargs):
        # type: (Optional[Configuration], Dict[str, Any]) -> None
        config = config or self.create_config(**kwargs)
        policies = [ContentDecodePolicy(), config.retry_policy, config.logging_policy]
        endpoint = os.environ.get(MSI_ENDPOINT)
        if not endpoint:
            raise ValueError("expected environment variable {} has no value".format(MSI_ENDPOINT))
        self._client = AuthnClient(endpoint, config, policies, **kwargs)

    @staticmethod
    def create_config(**kwargs):
        # type: (Dict[str, str]) -> Configuration
        timeout = kwargs.pop("connection_timeout", 2)
        config = Configuration(connection_timeout=timeout, **kwargs)
        config.logging_policy = NetworkTraceLoggingPolicy(**kwargs)
        retries = kwargs.pop("retry_total", 5)
        config.retry_policy = RetryPolicy(
            retry_total=retries, retry_on_status_codes=[404, 429] + list(range(500, 600)), **kwargs
        )
        return config

    def get_token(self, *scopes):
        # type: (*str) -> str
        if len(scopes) != 1:
            raise ValueError("this credential supports only one scope per request")
        token = self._client.get_cached_token(scopes)
        if not token:
            secret = os.environ.get(MSI_SECRET)
            if not secret:
                raise AuthenticationError("{} environment variable has no value".format(MSI_SECRET))
            resource = scopes[0]
            if resource.endswith("/.default"):
                resource = resource[:-len("/.default")]
            # TODO: support user-assigned client id
            token = self._client.request_token(
                scopes,
                method="GET",
                headers={"secret": secret},
                params={"api-version": "2017-09-01", "resource": resource},
            )
        return token
