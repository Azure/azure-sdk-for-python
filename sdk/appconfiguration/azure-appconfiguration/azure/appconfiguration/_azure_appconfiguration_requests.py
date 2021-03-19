# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import hashlib
import base64
import hmac
from azure.core.pipeline.policies import HTTPPolicy
from ._utils import get_current_utc_time


class AppConfigRequestsCredentialsPolicy(HTTPPolicy):
    """Implementation of request-oauthlib except and retry logic."""

    def __init__(self, credentials):
        super(AppConfigRequestsCredentialsPolicy, self).__init__()
        self._credentials = credentials

    def _signed_request(self, request):
        verb = request.http_request.method.upper()

        # Get the path and query from url, which looks like https://host/path/query
        query_url = str(request.http_request.url[len(self._credentials.host) + 8 :])

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
            + self._credentials.host
            + ";"
            + content_hash
        )

        decoded_secret = base64.b64decode(self._credentials.secret)
        digest = hmac.new(
            decoded_secret, string_to_sign.encode("utf-8"), hashlib.sha256
        ).digest()
        signature = base64.b64encode(digest).decode("utf-8")

        signature_header = {
            "x-ms-date": utc_now,
            "x-ms-content-sha256": content_hash,
            "Authorization": "HMAC-SHA256 Credential="
            + self._credentials.credential
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
