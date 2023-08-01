# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import re
from enum import auto, Enum
from devtools_testutils import AzureTestCase
from azure.communication.rooms._shared.utils import parse_connection_str
from azure_devtools.scenario_tests import RecordingProcessor, ReplayableTest
from azure_devtools.scenario_tests.utilities import is_text_payload


class ResponseReplacerProcessor(RecordingProcessor):
    def __init__(self, keys=None, replacement="sanitized"):
        self._keys = keys if keys else []
        self._replacement = replacement

    def process_response(self, response):
        def sanitize_dict(dictionary):
            for key in dictionary:
                value = dictionary[key]
                if isinstance(value, str):
                    dictionary[key] = re.sub(
                        r"(" + "|".join(self._keys) + r")",
                        self._replacement,
                        dictionary[key],
                    )
                elif isinstance(value, dict):
                    sanitize_dict(value)

        sanitize_dict(response)

        return response


class BodyReplacerProcessor(RecordingProcessor):
    """Sanitize the sensitive info inside request or response bodies"""

    def __init__(self, keys=None, replacement="sanitized"):
        self._replacement = replacement
        self._keys = keys if keys else []

    def process_request(self, request):
        if is_text_payload(request) and request.body:
            request.body = self._replace_keys(request.body.decode()).encode()

        return request

    def process_response(self, response):
        if is_text_payload(response) and response["body"]["string"]:
            response["body"]["string"] = self._replace_keys(response["body"]["string"])

        return response

    def _replace_keys(self, body):
        def _replace_recursively(obj):
            if isinstance(obj, dict):
                for key in obj:
                    value = obj[key]
                    if key in self._keys:
                        obj[key] = self._replacement
                    elif key == "iceServers":
                        _replace_recursively(value[0])
                    elif key == "urls":
                        obj[key][0] = "turn.skype.com"
                    else:
                        _replace_recursively(value)
            elif isinstance(obj, list):
                for i in obj:
                    _replace_recursively(i)

        import json

        try:
            body = json.loads(body)
            _replace_recursively(body)

        except (KeyError, ValueError):
            return body

        return json.dumps(body)


class CommunicationTestResourceType(Enum):
    """Type of ACS resource used for livetests."""

    UNSPECIFIED = auto()
    DYNAMIC = auto()
    STATIC = auto()


class CommunicationTestCase(AzureTestCase):
    FILTER_HEADERS = ReplayableTest.FILTER_HEADERS + [
        "x-azure-ref",
        "x-ms-content-sha256",
        "location",
    ]

    def __init__(self, method_name, *args, **kwargs):
        super(CommunicationTestCase, self).__init__(method_name, *args, **kwargs)

    def setUp(self, resource_type=CommunicationTestResourceType.UNSPECIFIED):
        super(CommunicationTestCase, self).setUp()
        self.connection_str = self._get_connection_str(resource_type)
        endpoint, _ = parse_connection_str(self.connection_str)
        self._resource_name = endpoint.split(".")[0]
        self.scrubber.register_name_pair(self._resource_name, "sanitized")

    def _get_connection_str(self, resource_type):
        if self.is_playback():
            return (
                "endpoint=https://sanitized.communication.azure.com/;accesskey=fake==="
            )
        if resource_type == CommunicationTestResourceType.UNSPECIFIED:
            return os.getenv(
                "COMMUNICATION_LIVETEST_DYNAMIC_CONNECTION_STRING"
            ) or os.getenv("COMMUNICATION_LIVETEST_STATIC_CONNECTION_STRING")
        if resource_type == CommunicationTestResourceType.DYNAMIC:
            return os.getenv("COMMUNICATION_LIVETEST_DYNAMIC_CONNECTION_STRING")
        if resource_type == CommunicationTestResourceType.STATIC:
            return os.getenv("COMMUNICATION_LIVETEST_STATIC_CONNECTION_STRING")
