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
from typing import Any, TYPE_CHECKING, Union

from azure.core.credentials import AzureKeyCredential

from .._patch import _parse_connection_string, WebPubSubServiceClientBase
from ._client import WebPubSubServiceClient as WebPubSubServiceClientGenerated


if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


class WebPubSubServiceClient(WebPubSubServiceClientBase, WebPubSubServiceClientGenerated):
    """WebPubSubServiceClient.

    :param endpoint: HTTP or HTTPS endpoint for the Web PubSub service instance.
    :type endpoint: str
    :param hub: Target hub name, which should start with alphabetic characters and only contain
     alpha-numeric characters or underscore.
    :type hub: str
    :param credential: Credential needed for the client to connect to Azure.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential or ~azure.core.credentials.AzureKeyCredential
    :keyword api_version: Api Version. The default value is "2021-10-01". Note that overriding this
     default value may result in unsupported behavior.
    :paramtype api_version: str
    """

    def __init__(
        self, endpoint: str, hub: str, credential: Union["AsyncTokenCredential", AzureKeyCredential], **kwargs: Any
    ) -> None:
        super().__init__(endpoint=endpoint, hub=hub, credential=credential, **kwargs)

    @classmethod
    def from_connection_string(cls, connection_string: str, hub: str, **kwargs: Any) -> "WebPubSubServiceClient":
        """Create a new WebPubSubServiceClient from a connection string.

        :param connection_string: Connection string
        :type connection_string: ~str
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
