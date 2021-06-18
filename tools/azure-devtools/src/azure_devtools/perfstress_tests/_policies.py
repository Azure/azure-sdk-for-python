# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.core.pipeline.policies import SansIOHTTPPolicy


class PerfTestProxyPolicy(SansIOHTTPPolicy):

    def __init__(self, url):
        self.recording_id = None
        self.mode = None
        self._proxy_url = url

    def redirect_to_test_proxy(self, request):
        if self.recording_id and self.mode:
            original_destination = request.url
            request.url = self._proxy_url
            request.headers["x-recording-id"] = self.recording_id
            request.headers["x-recording-mode"] = self.mode
            request.headers["x-recording-remove"] = "false"

            # Ensure x-recording-upstream-base-uri header is only set once, since the
            # same HttpMessage will be reused on retries
            if "x-recording-upstream-base-uri" not in request.headers:
                request.headers["x-recording-upstream-base-uri"] = original_destination

    def send(self, request):
        self.redirect_to_test_proxy(request.http_request)
