# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import hashlib
import urllib
import base64
import hmac
from urllib.parse import ParseResult, urlparse
from typing import Union
from azure.core.credentials import AzureKeyCredential
from azure.core.pipeline.policies import SansIOHTTPPolicy
from .utils import get_current_utc_time


class HMACCredentialsPolicy(SansIOHTTPPolicy):
    """Implementation of HMAC authentication policy.

    :param str host: The host of the endpoint url for Azure Communication Service resource
    :param access_key: The access key we use to authenticate to the service
    :type access_key: str or AzureKeyCredential
    :param bool decode_url: `True` if there is a need to decode the url. Default value is `False`
    """

    def __init__(
        self,
        host,  # type: str
        access_key,  # type: Union[str, AzureKeyCredential]
        decode_url=False,  # type: bool
    ):
        # type: (...) -> None
        super(HMACCredentialsPolicy, self).__init__()

        if host.startswith("https://"):
            self._host = host.replace("https://", "")

        if host.startswith("http://"):
            self._host = host.replace("http://", "")

        self._access_key = access_key
        self._decode_url = decode_url

    def _compute_hmac(
        self, value  # type: str
    ):
        if isinstance(self._access_key, AzureKeyCredential):
            decoded_secret = base64.b64decode(self._access_key.key)
        else:
            decoded_secret = base64.b64decode(self._access_key)

        digest = hmac.new(
            decoded_secret, value.encode("utf-8"), hashlib.sha256
        ).digest()

        return base64.b64encode(digest).decode("utf-8")

    def _sign_request(self, request):
        verb = request.http_request.method.upper()

        # Get the path and query from url, which looks like https://host/path/query
        parsed_url: ParseResult = urlparse(request.http_request.url)
        query_url = parsed_url.path

        if parsed_url.query:
            query_url += "?" + parsed_url.query

        # Need URL() to get a correct encoded key value, from "%3A" to ":", when transport is in type AioHttpTransport.
        # There's a similar scenario in azure-storage-blob and azure-appconfiguration, the check logic is from there.
        try:
            from yarl import URL
            from azure.core.pipeline.transport import (  # pylint:disable=non-abstract-transport-import
                AioHttpTransport,
            )

            if (
                isinstance(request.context.transport, AioHttpTransport)
                or isinstance(
                    getattr(request.context.transport, "_transport", None),
                    AioHttpTransport,
                )
                or isinstance(
                    getattr(
                        getattr(request.context.transport, "_transport", None),
                        "_transport",
                        None,
                    ),
                    AioHttpTransport,
                )
            ):
                query_url = str(URL(query_url))
        except (ImportError, TypeError):
            pass

        if self._decode_url:
            query_url = urllib.parse.unquote(query_url)

        signed_headers = "x-ms-date;host;x-ms-content-sha256"

        utc_now = get_current_utc_time()
        if request.http_request.body is None:
            request.http_request.body = ""
        content_digest = hashlib.sha256(
            (request.http_request.body.encode("utf-8"))
        ).digest()
        content_hash = base64.b64encode(content_digest).decode("utf-8")

        string_to_sign = (
            verb
            + "\n"
            + query_url
            + "\n"
            + utc_now
            + ";"
            + self._host
            + ";"
            + content_hash
        )

        signature = self._compute_hmac(string_to_sign)

        signature_header = {
            "x-ms-date": utc_now,
            "x-ms-content-sha256": content_hash,
            "x-ms-return-client-request-id": "true",
            "Authorization": "HMAC-SHA256 SignedHeaders="
            + signed_headers
            + "&Signature="
            + signature,
        }

        request.http_request.headers.update(signature_header)

        return request

    def on_request(self, request):
        self._sign_request(request)
