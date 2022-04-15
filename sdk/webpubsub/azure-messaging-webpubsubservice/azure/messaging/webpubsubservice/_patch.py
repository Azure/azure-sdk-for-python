# coding=utf-8
# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
from typing import Any, TYPE_CHECKING, Optional, Union, Awaitable
from datetime import datetime, timedelta
import jwt
import six

from azure.core.pipeline import PipelineRequest
from azure.core.pipeline.policies import SansIOHTTPPolicy, ProxyPolicy
from azure.core.credentials import AzureKeyCredential

from ._client import WebPubSubServiceClient as WebPubSubServiceClientGenerated
from ._operations._patch import _UTC_TZ


if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from azure.core.credentials import TokenCredential


def _parse_connection_string(connection_string: str, **kwargs: Any) -> Any:
    for segment in connection_string.split(";"):
        if "=" in segment:
            key, value = segment.split("=", 1)
            key = key.lower()
            if key not in ("version",):
                kwargs.setdefault(key, value)
        elif segment:
            raise ValueError(
                "Malformed connection string - expected 'key=value', found segment '{}' in '{}'".format(
                    segment, connection_string
                )
            )

    if "endpoint" not in kwargs:
        raise ValueError("connection_string missing 'endpoint' field")

    if "accesskey" not in kwargs:
        raise ValueError("connection_string missing 'accesskey' field")

    return kwargs


class JwtCredentialPolicy(SansIOHTTPPolicy):

    NAME_CLAIM_TYPE = "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name"

    def __init__(
        self,
        credential: AzureKeyCredential,
        *,
        user: Optional[str] = None,
        origin_endpoint: Optional[str] = None,
        reverse_proxy_endpoint: Optional[str] = None,
    ) -> None:
        """Create a new instance of the policy associated with the given credential.

        :param credential: The azure.core.credentials.AzureKeyCredential instance to use
        :type credential: ~azure.core.credentials.AzureKeyCredential
        :param user: Optional user name associated with the credential.
        :type user: str
        """
        self._credential = credential
        self._user = user
        self._original_url = origin_endpoint
        self._reverse_proxy_endpoint = reverse_proxy_endpoint

    def on_request(self, request: PipelineRequest) -> Union[None, Awaitable[None]]:
        """Is executed before sending the request from next policy.

        :param request: Request to be modified before sent from next policy.
        :type request: ~azure.core.pipeline.PipelineRequest
        """
        url = request.http_request.url
        if self._reverse_proxy_endpoint:
            url = url.replace(self._reverse_proxy_endpoint, self._original_url, 1)
        request.http_request.headers["Authorization"] = "Bearer " + self._encode(url)
        return super(JwtCredentialPolicy, self).on_request(request)

    def _encode(self, url: AzureKeyCredential) -> str:
        data = {
            "aud": url,
            "exp": datetime.now(tz=_UTC_TZ()) + timedelta(seconds=60),
        }
        if self._user:
            data[self.NAME_CLAIM_TYPE] = self._user

        encoded = jwt.encode(
            payload=data,
            key=self._credential.key,
            algorithm="HS256",
        )
        return six.ensure_str(encoded)


class ApiManagementProxy(ProxyPolicy):
    def __init__(self, **kwargs: Any) -> None:
        """Create a new instance of the policy.

        :param endpoint: endpoint to be replaced
        :type endpoint: str
        :param proxy_endpoint: proxy endpoint
        :type proxy_endpoint: str
        """
        super(ApiManagementProxy, self).__init__(**kwargs)
        self._endpoint = kwargs.pop("origin_endpoint", None)
        self._reverse_proxy_endpoint = kwargs.pop("reverse_proxy_endpoint", None)

    def on_request(self, request: PipelineRequest) -> None:
        """Is executed before sending the request from next policy.

        :param request: Request to be modified before sent from next policy.
        :type request: ~azure.core.pipeline.PipelineRequest
        """
        super(ApiManagementProxy, self).on_request(request)
        if self._endpoint and self._reverse_proxy_endpoint:
            request.http_request.url = request.http_request.url.replace(self._endpoint, self._reverse_proxy_endpoint)


class WebPubSubServiceClientBase:
    """Base class for init"""

    def __init__(self, endpoint: str, hub: str, credential, **kwargs) -> None:
        if kwargs.get("port") and endpoint:
            endpoint = endpoint.rstrip("/") + ":{}".format(kwargs.pop("port"))
        kwargs["origin_endpoint"] = endpoint
        if isinstance(credential, AzureKeyCredential):
            kwargs["authentication_policy"] = JwtCredentialPolicy(
                credential,
                user=kwargs.get("user"),
                origin_endpoint=kwargs.get("origin_endpoint"),
                reverse_proxy_endpoint=kwargs.get("reverse_proxy_endpoint"),
            )
        kwargs["proxy_policy"] = kwargs.pop("proxy_policy", ApiManagementProxy(**kwargs))
        super().__init__(endpoint=endpoint, hub=hub, credential=credential, **kwargs)


class WebPubSubServiceClient(WebPubSubServiceClientBase, WebPubSubServiceClientGenerated):
    """WebPubSubServiceClient.

    :param endpoint: HTTP or HTTPS endpoint for the Web PubSub service instance.
    :type endpoint: str
    :param hub: Target hub name, which should start with alphabetic characters and only contain
     alpha-numeric characters or underscore.
    :type hub: str
    :param credential: Credential needed for the client to connect to Azure.
    :type credential: ~azure.core.credentials.TokenCredential or ~azure.core.credentials.AzureKeyCredential
    :keyword api_version: Api Version. The default value is "2021-10-01". Note that overriding this
     default value may result in unsupported behavior.
    :paramtype api_version: str
    """

    def __init__(
        self, endpoint: str, hub: str, credential: Union["TokenCredential", AzureKeyCredential], **kwargs: Any
    ) -> None:
        super().__init__(endpoint=endpoint, hub=hub, credential=credential, **kwargs)

    @classmethod
    def from_connection_string(cls, connection_string: str, hub: str, **kwargs: Any) -> "WebPubSubServiceClient":
        """Create a new WebPubSubServiceClient from a connection string.

        :param connection_string: Connection string
        :type connection_string: str
        :param hub: Target hub name, which should start with alphabetic characters and only contain
         alpha-numeric characters or underscore.
        :type hub: str
        :rtype: WebPubSubServiceClient
        """
        kwargs = _parse_connection_string(connection_string, **kwargs)

        credential = AzureKeyCredential(kwargs.pop("accesskey"))
        return cls(hub=hub, credential=credential, **kwargs)


__all__ = ["WebPubSubServiceClient"]


def patch_sdk():
    pass
