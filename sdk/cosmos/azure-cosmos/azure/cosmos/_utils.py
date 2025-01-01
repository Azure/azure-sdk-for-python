# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Internal Helper functions in the Azure Cosmos database service.
"""

import platform
import re
import urllib.parse
import json
from typing import Any, Dict, Optional

from ._version import VERSION


def get_user_agent() -> str:
    os_name = safe_user_agent_header(platform.platform())
    python_version = safe_user_agent_header(platform.python_version())
    user_agent = "azsdk-python-cosmos/{} Python/{} ({})".format(VERSION, python_version, os_name)
    return user_agent


def get_user_agent_async() -> str:
    os_name = safe_user_agent_header(platform.platform())
    python_version = safe_user_agent_header(platform.python_version())
    user_agent = "azsdk-python-cosmos-async/{} Python/{} ({})".format(VERSION, python_version, os_name)
    return user_agent


def safe_user_agent_header(s: Optional[str]) -> str:
    if s is None:
        s = "unknown"
    # remove all white spaces
    s = re.sub(r"\s+", "", s)
    if not s:
        s = "unknown"
    return s


def get_index_metrics_info(url_encoded_string: Optional[str]) -> Dict[str, Any]:
    if url_encoded_string is None:
        return {}

    try:
        # Decode the URL-encoded string
        decoded_string = urllib.parse.unquote(url_encoded_string, encoding='utf-8')

        # Python's json.loads method is used for deserialization
        result = json.loads(decoded_string) or {}
        return result
    except (json.JSONDecodeError, ValueError):
        return {}
