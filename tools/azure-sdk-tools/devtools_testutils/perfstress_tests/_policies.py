# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from urllib.parse import urlparse

from azure.core.pipeline.policies import SansIOHTTPPolicy


class PerfTestProxyPolicy(SansIOHTTPPolicy):

    def __init__(self, url):
        self.recording_id = None
        self.mode = None
        self._proxy_url = urlparse(url)

    def redirect_to_test_proxy(self, request):
        if self.recording_id and self.mode:
            live_endpoint = urlparse(request.http_request.url)
            redirected = live_endpoint._replace(
                scheme=self._proxy_url.scheme,
                netloc=self._proxy_url.netloc
            )
            request.http_request.url = redirected.geturl()
            request.http_request.headers["x-recording-id"] = self.recording_id
            request.http_request.headers["x-recording-mode"] = self.mode
            request.http_request.headers["x-recording-remove"] = "false"

            # Ensure x-recording-upstream-base-uri header is only set once, since the
            # same HttpMessage will be reused on retries
            if "x-recording-upstream-base-uri" not in request.http_request.headers:
                original_endpoint = "{}://{}".format(live_endpoint.scheme, live_endpoint.netloc)
                request.http_request.headers["x-recording-upstream-base-uri"] = original_endpoint

    def on_request(self, request):
        self.redirect_to_test_proxy(request)
