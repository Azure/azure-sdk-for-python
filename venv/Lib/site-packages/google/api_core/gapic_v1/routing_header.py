# Copyright 2017 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Helpers for constructing routing headers.

These headers are used by Google infrastructure to determine how to route
requests, especially for services that are regional.

Generally, these headers are specified as gRPC metadata.
"""

import sys

from six.moves.urllib.parse import urlencode

ROUTING_METADATA_KEY = "x-goog-request-params"


def to_routing_header(params):
    """Returns a routing header string for the given request parameters.

    Args:
        params (Mapping[str, Any]): A dictionary containing the request
            parameters used for routing.

    Returns:
        str: The routing header string.
    """
    if sys.version_info[0] < 3:
        # Python 2 does not have the "safe" parameter for urlencode.
        return urlencode(params).replace("%2F", "/")
    return urlencode(
        params,
        # Per Google API policy (go/api-url-encoding), / is not encoded.
        safe="/",
    )


def to_grpc_metadata(params):
    """Returns the gRPC metadata containing the routing headers for the given
    request parameters.

    Args:
        params (Mapping[str, Any]): A dictionary containing the request
            parameters used for routing.

    Returns:
        Tuple(str, str): The gRPC metadata containing the routing header key
            and value.
    """
    return (ROUTING_METADATA_KEY, to_routing_header(params))
