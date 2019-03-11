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
from azure.core.pipeline.policies import HTTPPolicy

from .utils import parse_connection_string, get_current_utc_time
import hashlib
import base64
import hmac

class AzConfigRequestsCredentialsPolicy(HTTPPolicy):
    """Implementation of request-oauthlib except and retry logic.
    """
    def __init__(self, config):
        super(AzConfigRequestsCredentialsPolicy, self).__init__()
        self._config = config

    
    def _signed_session(self, request, session):
        verb = request.http_request.method.upper()
        host, credential, secret = parse_connection_string(self._config.connection_string)

        # Get the path and query from url, which looks like https://host/path/query
        query_url = str(request.http_request.url[len(host) + 8:])

        signed_headers = "x-ms-date;host;x-ms-content-sha256"

        utc_now = get_current_utc_time()
        if request.http_request.body is None:
            request.http_request.body = ''
        content_digest = hashlib.sha256((bytes(request.http_request.body, 'utf-8'))).digest()
        content_hash = base64.b64encode(content_digest).decode('utf-8')

        string_to_sign = verb + '\n' + query_url + '\n' + utc_now + ';' + host + ';' + content_hash

        #decode secret
        decoded_secret = base64.b64decode(secret, validate=True)
        digest = hmac.new(decoded_secret, bytes(string_to_sign, 'utf-8'), hashlib.sha256).digest()
        signature = base64.b64encode(digest).decode('utf-8')

        signature_header = {
            "x-ms-date": utc_now,
            "x-ms-content-sha256": content_hash,
            "Authorization": "HMAC-SHA256 Credential=" + credential + ", SignedHeaders=" + signed_headers + ", Signature=" + signature
        }

        request.http_request.headers.update(signature_header)

        return request

    def send(self, request, **kwargs):
        session = request.context.session
        self._signed_session(request, session)
        return self.next.send(request, **kwargs)
        