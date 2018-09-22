# The MIT License (MIT)
# Copyright (c) 2017 Microsoft Corporation

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

"""Internal class for aggregation queries implementation in the Azure Cosmos database service.
"""
from abc import abstractmethod, ABCMeta
from azure.cosmos.execution_context.document_producer import _OrderByHelper


class _Aggregator(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def aggregate(self, other):
        pass

    @abstractmethod
    def get_result(self):
        pass


class _AverageAggregator(_Aggregator):
    def __init__(self):
        self.sum = None
        self.count = None

    def aggregate(self, other):
        if other is None or not 'sum' in other:
            return
        if self.sum is None:
            self.sum = 0.0
            self.count = 0
        self.sum += other['sum']
        self.count += other['count']

    def get_result(self):
        if self.sum is None or self.count is None or self.count <= 0:
            return None
        return self.sum / self.count


class _CountAggregator(_Aggregator):
    def __init__(self):
        self.count = 0

    def aggregate(self, other):
        self.count += other

    def get_result(self):
        return self.count


class _MinAggregator(_Aggregator):
    def __init__(self):
        self.value = None

    def aggregate(self, other):
        if self.value is None:
            self.value = other
        else:
            if (_OrderByHelper.compare({'item': other}, {'item': self.value}) < 0):
                self.value = other

    def get_result(self):
        return self.value


class _MaxAggregator(_Aggregator):
    def __init__(self):
        self.value = None

    def aggregate(self, other):
        if self.value is None:
            self.value = other
        else:
            if (_OrderByHelper.compare({'item': other}, {'item': self.value}) > 0):
                self.value = other

    def get_result(self):
        return self.value


class _SumAggregator(_Aggregator):
    def __init__(self):
        self.sum = None

    def aggregate(self, other):
        if other is None:
            return
        if self.sum is None:
            self.sum = other
        else:
            self.sum += other

    def get_result(self):
        return self.sum
