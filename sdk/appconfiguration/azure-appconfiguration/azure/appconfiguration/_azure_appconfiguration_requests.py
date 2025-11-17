# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import hashlib
import base64
import hmac
from urllib.parse import urlparse
from azure.core.credentials import AzureKeyCredential
from azure.core.pipeline.policies import HTTPPolicy
from ._utils import get_current_utc_time


class AppConfigRequestsCredentialsPolicy(HTTPPolicy):
    """Implementation of request-oauthlib except and retry logic."""

    def __init__(self, credential: AzureKeyCredential, endpoint: str, id_credential: str):
        super(AppConfigRequestsCredentialsPolicy, self).__init__()
        self._credential = credential
        self._endpoint = endpoint
        self._id_credential = id_credential

    def _signed_request(self, request):
        verb = request.http_request.method.upper()

        parsed_url = urlparse(self._endpoint)
        # Get the path, query and hash fragment from url, which looks like https://host/path?query#fragment
        query_url = str(request.http_request.url[len(parsed_url.geturl()) :])
        # Need URL() to get a correct encoded key value, from "%2A" to "*", when transport is in type AioHttpTransport.
        # There's a similar scenario in azure-storage-blob, the check logic is from there.
        try:
            from yarl import URL
            from azure.core.pipeline.transport import (  # pylint:disable=non-abstract-transport-import,no-name-in-module
                AioHttpTransport,
            )

            if (
                isinstance(request.context.transport, AioHttpTransport)
                or isinstance(getattr(request.context.transport, "_transport", None), AioHttpTransport)
                or isinstance(
                    getattr(getattr(request.context.transport, "_transport", None), "_transport", None),
                    AioHttpTransport,
                )
            ):
                query_url = str(URL(query_url))
        except (ImportError, TypeError):
            pass
        signed_headers = "x-ms-date;host;x-ms-content-sha256"

        utc_now = get_current_utc_time()
        if request.http_request.body is None:
            request.http_request.body = ""
        content_digest = hashlib.sha256((request.http_request.body.encode("utf-8"))).digest()
        content_hash = base64.b64encode(content_digest).decode("utf-8")

        string_to_sign = verb + "\n" + query_url + "\n" + utc_now + ";" + parsed_url.netloc + ";" + content_hash

        decoded_secret = base64.b64decode(self._credential.key)
        digest = hmac.new(decoded_secret, string_to_sign.encode("utf-8"), hashlib.sha256).digest()
        signature = base64.b64encode(digest).decode("utf-8")

        signature_header = {
            "x-ms-date": utc_now,
            "x-ms-content-sha256": content_hash,
            "Authorization": "HMAC-SHA256 Credential="
            + self._id_credential
            + "&SignedHeaders="
            + signed_headers
            + "&Signature="
            + signature,
        }

        request.http_request.headers.update(signature_header)

        return request

    def send(self, request):
        self._signed_request(request)
        return self.next.send(request)
