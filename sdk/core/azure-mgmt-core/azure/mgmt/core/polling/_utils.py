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
"""ARM-specific utilities for polling continuation token serialization."""

from typing import Dict, Mapping

from azure.core.polling._utils import _LRO_HEADERS

# ARM-specific LRO headers - includes azure-asyncoperation which is ARM-specific
_ARM_LRO_HEADERS = _LRO_HEADERS | frozenset(["azure-asyncoperation"])


def _filter_arm_headers(headers: Mapping[str, str]) -> Dict[str, str]:
    """Filter headers to only include those needed for ARM LRO rehydration.

    Uses an allowlist approach - only headers required for polling are included.
    This includes the azure-asyncoperation header which is ARM-specific.

    :param headers: The headers to filter.
    :type headers: Mapping[str, str]
    :return: A new dictionary with only allowed headers.
    :rtype: dict[str, str]
    """
    return {k: v for k, v in headers.items() if k.lower() in _ARM_LRO_HEADERS}
