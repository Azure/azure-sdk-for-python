# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure_devtools.scenario_tests import RecordingProcessor


class OAuthv2RequestResponsesFilter(RecordingProcessor):
    """Remove oauth authentication requests and responses from recording."""

    def process_request(self, request):
        import re
        if not re.match('https://login.microsoftonline.com/([^/]+)/oauth2(?:/v2.0)?/token', request.uri):
            return request
        return None
