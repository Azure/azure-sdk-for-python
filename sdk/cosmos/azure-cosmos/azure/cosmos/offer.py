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

"""Create throughput properties in the Azure Cosmos DB SQL API service.
"""
from typing import Dict, Any


class ThroughputProperties(object):
    """Represents the throughput properties in an Azure Cosmos DB SQL API container.
    To read and update throughput properties use the associated methods on the :class:`Container`.

    :param offer_throughput: The provisioned throughput in request units per second as a number.

    :param auto_scale_max_throughput: is the max autoscale throughput, it should have valid throughput
   values between 1000 and 1000000 inclusive in increments of 1000.

    :param auto_scale_increment_percent: is the  % from the base selected RU it increases at a given time,
    up to a maximum default value is 0 the increment percent should be greater than or equal to zero.

    Both auto_scale_max_throughput and auto_scale_increment_percent have to be used simultaneously, you cannot
    set the offer_throughput when setting the auto_scale properties.
    """

    def __init__(self, offer_throughput=None, properties=None, **kwargs):  # pylint: disable=super-init-not-called
        # type: (int, Dict[str, Any], int) -> None
        self.offer_throughput = offer_throughput
        self.properties = properties
        self.auto_scale_max_throughput = kwargs.pop('auto_scale_max_throughput', None)
        self.auto_scale_increment_percent = kwargs.pop('auto_scale_increment_percent', None)



Offer = ThroughputProperties
