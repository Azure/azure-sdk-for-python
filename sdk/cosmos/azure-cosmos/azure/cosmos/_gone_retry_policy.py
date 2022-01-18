# The MIT License (MIT)
# Copyright (c) 2021 Microsoft Corporation

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

"""Internal class for connection reset retry policy implementation in the Azure
Cosmos database service.
"""
from . import http_constants

# pylint: disable=protected-access


class GoneRetryPolicy(object):

    def __init__(self, client, *args):
        self._max_retry_attempt_count = 3
        self.current_retry_attempt_count = 0
        self.retry_after_in_milliseconds = 1000
        self.args = args
        self.client = client


    def ShouldRetry(self, exception):
        """Returns true if should retry based on the passed-in exception.

        :param (exceptions.CosmosHttpResponseError instance) exception:
        :rtype: boolean

        """
        if exception.sub_status == http_constants.SubStatusCodes.PARTITION_KEY_RANGE_GONE:
            # refresh routing_map_provider to refresh partition key range cache
            # return False to raise error to multi_execution_aggregator and repair document producer
            self.client.refresh_routing_map_provider()
            return False
        if self.current_retry_attempt_count < self._max_retry_attempt_count:
            self.current_retry_attempt_count += 1
            return True
        return False
