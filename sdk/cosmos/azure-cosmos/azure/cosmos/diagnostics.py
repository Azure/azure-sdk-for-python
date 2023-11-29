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

"""Diagnostic tools for Azure Cosmos database service operations.
IMPORTANT: This file has been marked for deprecation and will be removed in the future. For diagnostics logging in our
SDK, please use our CosmosHttpLoggingPolicy outlined in our README.
"""
import warnings

from azure.core.utils import CaseInsensitiveDict


class _RecordDiagnostics(object):
    """This file is currently deprecated and will be removed in the future. Please use our CosmosHttpLoggingPolicy
    for logging SDK diagnostics moving forward. More information on this can be found in our README.

    Record Response headers from Cosmos read operations.

    The full response headers are stored in the ``headers`` property.

    Examples:

        >>> rh = RecordDiagnostics()

        >>> col = b.create_container(
        ...     id="some_container",
        ...     partition_key=PartitionKey(path='/id', kind='Hash'),
        ...     response_hook=rh)

        >>> rh.headers['x-ms-activity-id']
        '6243eeed-f06a-413d-b913-dcf8122d0642'

    """

    _common = {
        "x-ms-activity-id",
        "x-ms-session-token",
        "x-ms-item-count",
        "x-ms-request-quota",
        "x-ms-resource-usage",
        "x-ms-retry-after-ms",
    }

    def __init__(self):
        self._headers = CaseInsensitiveDict()
        self._body = None
        self._request_charge = 0

    @property
    def headers(self):
        return CaseInsensitiveDict(self._headers)

    @property
    def body(self):
        return self._body

    @property
    def request_charge(self):
        return self._request_charge

    def clear(self):
        self._request_charge = 0

    def __call__(self, headers, body):
        self._headers = headers
        self._body = body

        self._request_charge += float(headers.get("x-ms-request-charge", 0))

    def __getattr__(self, name):
        key = "x-ms-" + name.replace("_", "-")
        if key in self._common:
            return self._headers[key]
        raise AttributeError(name)


def __getattr__(name):
    if name == 'RecordDiagnostics':
        warnings.warn(
            "RecordDiagnostics is deprecated and should not be used. " +
            "For logging diagnostics information for the SDK, please use our CosmosHttpLoggingPolicy. " +
            "For more information on this, please see our README.",
            DeprecationWarning
        )
        return _RecordDiagnostics

    raise AttributeError(f"module 'azure.cosmos.diagnostics' has no attribute {name}")
