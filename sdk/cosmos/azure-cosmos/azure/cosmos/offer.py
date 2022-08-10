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

    To read and update throughput properties, use the associated methods on the :class:`Container`.
    If configuring auto-scale, `auto_scale_max_throughput` needs to be set and
    `auto_scale_increment_percent` can also be set in conjunction with it.
    The value of `offer_throughput` will not be allowed to be set in conjunction with the auto-scale settings.

    :keyword int offer_throughput: The provisioned throughput in request units per second as a number.
    :keyword int auto_scale_max_throughput: The max auto-scale throughput. It should have a valid throughput
     value between 1000 and 1000000 inclusive, in increments of 1000.
    :keyword int auto_scale_increment_percent: is the % from the base selected RU it increases at a given time,
     the increment percent should be greater than or equal to zero.
    """

    def __init__(self, *args, **kwargs): # pylint: disable=super-init-not-called
        self.offer_throughput = args[0] if args else kwargs.get('offer_througput')
        self.properties = args[1] if len(args) > 1 else kwargs.get('properties')
        self.auto_scale_max_throughput = kwargs.get('auto_scale_max_throughput')
        self.auto_scale_increment_percent = kwargs.get('auto_scale_increment_percent')



Offer = ThroughputProperties
