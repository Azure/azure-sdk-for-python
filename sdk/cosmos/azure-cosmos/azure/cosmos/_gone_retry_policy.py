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


# pylint: disable=protected-access


class PartitionKeyRangeGoneRetryPolicy(object):

    def __init__(self, client, *args):
        self.retry_after_in_milliseconds = 1000
        self.refresh_partition_key_range_cache = True
        self.args = args
        self.client = client
        self.exception = None

    def ShouldRetry(self, exception):
        """Returns true if the request should retry based on the passed-in exception.

        :param (exceptions.CosmosHttpResponseError instance) exception:
        :returns: a boolean stating whether the request should be retried
        :rtype: bool

        """
        self.exception = exception  # needed for pylint
        if self.refresh_partition_key_range_cache:
            # refresh routing_map_provider to refresh partition key range cache
            # make refresh_partition_key_range_cache False to skip this check on subsequent Gone exceptions
            self.client.refresh_routing_map_provider()
            self.refresh_partition_key_range_cache = False
        # return False to raise error to multi_execution_aggregator and repair document producer context
        return False
