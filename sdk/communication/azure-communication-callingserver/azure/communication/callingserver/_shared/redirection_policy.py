# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from azure.core.pipeline.policies import SansIOHTTPPolicy

def is_redirect_response(response):
    return response.status_code in [301, 302]

def should_redirect(response, request_number, attempted_locations):
    if request_number > 10:
        return False

    if attempted_locations.__contains__(response.headers["Location"]):
        return False

    return True

class RedirectPolicy(SansIOHTTPPolicy):
    def on_response(self, request, response):
        self._attempt_redirection(request, response)

    def _attempt_redirection(
            self,
            request,
            response
        ):
        request_number = request.http_request.headers.get("x-ms-redirected_times", 1)
        attempted_locations = request.http_request.headers.get("x-ms-attempted_locations", "")
        attempted_locations = attempted_locations.split(',')
        if (is_redirect_response(response.http_response)
            and should_redirect(response.http_response, request_number, attempted_locations)):
            new_location = response.http_response.headers["Location"]
            attempted_locations = new_location
            request.url = new_location
            request.http_request.headers["x-ms-attempted_locations"] = ','.join(attempted_locations)
            request.http_request.headers["x-ms-redirected_times"] = request_number + 1
            self.on_request(request)
