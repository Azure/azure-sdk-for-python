# Copyright 2018, OpenCensus Authors
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

try:
    # For Python 3.0 and later
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError, URLError
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen, Request
    from urllib2 import HTTPError, URLError


import socket

_REQUEST_TIMEOUT = 2  # in secs


def get_request(request_url, request_headers=dict()):
    """Execute http get request on given request_url with optional headers
    """
    request = Request(request_url)
    for key, val in request_headers.items():
        request.add_header(key, val)

    try:
        response = urlopen(request, timeout=_REQUEST_TIMEOUT)
        response_content = response.read()
    except (HTTPError, URLError, socket.timeout):
        response_content = None

    return response_content
