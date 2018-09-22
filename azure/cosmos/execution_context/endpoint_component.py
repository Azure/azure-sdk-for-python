#The MIT License (MIT)
#Copyright (c) 2014 Microsoft Corporation

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

"""Internal class for query execution endpoint component implementation in the Azure Cosmos database service.
"""
import numbers

from azure.cosmos.execution_context.aggregators import _AverageAggregator, _CountAggregator, _MaxAggregator, \
    _MinAggregator, _SumAggregator


class _QueryExecutionEndpointComponent(object):
    def __init__(self, execution_context):
        self._execution_context = execution_context

    def __iter__(self):
        return self

    def next(self):
        return next(self._execution_context)

    def __next__(self):
        # supports python 3 iterator
        return self.next()

class _QueryExecutionOrderByEndpointComponent(_QueryExecutionEndpointComponent):
    """Represents an endpoint in handling an order by query.

    For each processed orderby result it returns 'payload' item of the result
    """
    def __init__(self, execution_context):
        super(_QueryExecutionOrderByEndpointComponent, self).__init__(execution_context)

    def next(self):
        return next(self._execution_context)['payload']

class _QueryExecutionTopEndpointComponent(_QueryExecutionEndpointComponent):
    """Represents an endpoint in handling top query.

    It only returns as many results as top arg specified.
    """
    def __init__(self, execution_context, top_count):
        super(_QueryExecutionTopEndpointComponent, self).__init__(execution_context)
        self._top_count = top_count

    def next(self):
        if (self._top_count > 0):
            res = next(self._execution_context)
            self._top_count -= 1
            return res
        raise StopIteration

class _QueryExecutionAggregateEndpointComponent(_QueryExecutionEndpointComponent):
    """Represents an endpoint in handling aggregate query.

    It returns only aggreated values.
    """
    def __init__(self, execution_context, aggregate_operators):
        super(_QueryExecutionAggregateEndpointComponent, self).__init__(execution_context)
        self._local_aggregators = []
        self._results = None
        self._result_index = 0
        for operator in aggregate_operators:
            if operator == 'Average':
                self._local_aggregators.append(_AverageAggregator())
            elif operator == 'Count':
                self._local_aggregators.append(_CountAggregator())
            elif operator == 'Max':
                self._local_aggregators.append(_MaxAggregator())
            elif operator == 'Min':
                self._local_aggregators.append(_MinAggregator())
            elif operator == 'Sum':
                self._local_aggregators.append(_SumAggregator())

    def next(self):
        for res in self._execution_context:
            for item in res:
                for operator in self._local_aggregators:
                    if isinstance(item, dict) and len(item.keys()) > 0:
                        operator.aggregate(item['item'])
                    elif isinstance(item, numbers.Number):
                        operator.aggregate(item)
        if self._results is None:
            self._results = []
            for operator in self._local_aggregators:
                self._results.append(operator.get_result())
        if self._result_index < len(self._results):
            res = self._results[self._result_index]
            self._result_index += 1
            return res
        else:
            raise StopIteration
