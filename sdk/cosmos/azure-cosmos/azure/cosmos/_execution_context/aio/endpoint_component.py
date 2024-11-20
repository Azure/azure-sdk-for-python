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

"""Internal class for query execution endpoint component implementation in the
Azure Cosmos database service.
"""
import numbers
import copy
import hashlib
import json

from azure.cosmos._execution_context.aggregators import (
    _AverageAggregator,
    _CountAggregator,
    _MaxAggregator,
    _MinAggregator,
    _SumAggregator,
)


class _QueryExecutionEndpointComponent(object):
    def __init__(self, execution_context):
        self._execution_context = execution_context

    def __aiter__(self):
        return self

    async def __anext__(self):
        # supports python 3 iterator
        return await self._execution_context.__anext__()


class _QueryExecutionOrderByEndpointComponent(_QueryExecutionEndpointComponent):
    """Represents an endpoint in handling an order by query.

    For each processed orderby result it returns 'payload' item of the result.
    """
    async def __anext__(self):
        payload = await self._execution_context.__anext__()
        return payload["payload"]

class _QueryExecutionNonStreamingEndpointComponent(_QueryExecutionEndpointComponent):
    """Represents an endpoint in handling a non-streaming order by query results.
    For each processed orderby result it returns the item result.
    """
    async def __anext__(self):
        payload = await self._execution_context.__anext__()
        return payload._item_result["payload"]

class _QueryExecutionTopEndpointComponent(_QueryExecutionEndpointComponent):
    """Represents an endpoint in handling top query.

    It only returns as many results as top arg specified.
    """

    def __init__(self, execution_context, top_count):
        super(_QueryExecutionTopEndpointComponent, self).__init__(execution_context)
        self._top_count = top_count

    async def __anext__(self):
        if self._top_count > 0:
            res = await self._execution_context.__anext__()
            self._top_count -= 1
            return res
        raise StopAsyncIteration


class _QueryExecutionDistinctOrderedEndpointComponent(_QueryExecutionEndpointComponent):
    """Represents an endpoint in handling distinct query.

    It returns only those values not already returned.
    """
    def __init__(self, execution_context):
        super(_QueryExecutionDistinctOrderedEndpointComponent, self).__init__(execution_context)
        self.last_result = None

    async def __anext__(self):
        res = await self._execution_context.__anext__()
        while self.last_result == res:
            res = await self._execution_context.__anext__()
        self.last_result = res
        return res


class _QueryExecutionDistinctUnorderedEndpointComponent(_QueryExecutionEndpointComponent):
    """Represents an endpoint in handling distinct query.

    It returns only those values not already returned.
    """
    def __init__(self, execution_context):
        super(_QueryExecutionDistinctUnorderedEndpointComponent, self).__init__(execution_context)
        self.last_result = set()

    def make_hash(self, value):
        if isinstance(value, (set, tuple, list)):
            return tuple([self.make_hash(v) for v in value])  # pylint: disable=consider-using-generator
        if not isinstance(value, dict):
            if isinstance(value, numbers.Number):
                return float(value)
            return value
        new_value = copy.deepcopy(value)
        for k, v in new_value.items():
            new_value[k] = self.make_hash(v)

        return tuple(frozenset(sorted(new_value.items())))

    async def __anext__(self):
        res = await self._execution_context.__anext__()

        json_repr = json.dumps(self.make_hash(res)).encode("utf-8")

        hash_object = hashlib.sha1(json_repr)   # nosec
        hashed_result = hash_object.hexdigest()

        while hashed_result in self.last_result:
            res = await self._execution_context.__anext__()
            json_repr = json.dumps(self.make_hash(res)).encode("utf-8")

            hash_object = hashlib.sha1(json_repr)   # nosec
            hashed_result = hash_object.hexdigest()
        self.last_result.add(hashed_result)
        return res


class _QueryExecutionOffsetEndpointComponent(_QueryExecutionEndpointComponent):
    """Represents an endpoint in handling offset query.

    It returns results offset by as many results as offset arg specified.
    """
    def __init__(self, execution_context, offset_count):
        super(_QueryExecutionOffsetEndpointComponent, self).__init__(execution_context)
        self._offset_count = offset_count

    async def __anext__(self):
        while self._offset_count > 0:
            res = await self._execution_context.__anext__()
            if res is not None:
                self._offset_count -= 1
            else:
                raise StopAsyncIteration
        return await self._execution_context.__anext__()


class _QueryExecutionAggregateEndpointComponent(_QueryExecutionEndpointComponent):
    """Represents an endpoint in handling aggregate query.

    It returns only aggregated values.
    """

    def __init__(self, execution_context, aggregate_operators):
        super(_QueryExecutionAggregateEndpointComponent, self).__init__(execution_context)
        self._local_aggregators = []
        self._results = None
        self._result_index = 0
        for operator in aggregate_operators:
            if operator == "Average":
                self._local_aggregators.append(_AverageAggregator())
            elif operator in ("Count", "CountIf"):
                self._local_aggregators.append(_CountAggregator())
            elif operator == "Max":
                self._local_aggregators.append(_MaxAggregator())
            elif operator == "Min":
                self._local_aggregators.append(_MinAggregator())
            elif operator == "Sum":
                self._local_aggregators.append(_SumAggregator())

    async def __anext__(self):
        async for res in self._execution_context:
            for item in res: #TODO check on this being an async loop
                for operator in self._local_aggregators:
                    if isinstance(item, dict) and item:
                        try:
                            operator.aggregate(item["item"])
                        except KeyError:
                            pass
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
        raise StopAsyncIteration
