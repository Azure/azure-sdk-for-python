# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import re

from azure_devtools.scenario_tests import RecordingProcessor

class URIReplacerProcessor(RecordingProcessor):
    def __init__(self, keys=None, replacement="sanitized"):
        self._keys = keys if keys else []
        self._replacement = replacement

    def process_request(self, request):
        request.uri = re.sub(
            "https://([^/?])*.communication",
            "https://sanitized.communication",
            request.uri,
        )
        return request

    def process_response(self, response):
        if 'url' in response :
            response['url'] = re.sub(
                "https://([^/?])*.communication",
                "https://sanitized.communication",
                response['url'],
            )
        return response